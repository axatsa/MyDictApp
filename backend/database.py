import sqlite3
import json
import os

DB_PATH = os.getenv("DB_PATH", "/data/dict.db")


def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS dictionary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_en TEXT NOT NULL UNIQUE,
            word_uz TEXT,
            word_kr TEXT,
            def_ru TEXT,
            def_en TEXT,
            def_uz TEXT,
            def_kr TEXT,
            examples TEXT,
            examples_uz TEXT,
            examples_kr TEXT,
            trans_en TEXT,
            trans_uz TEXT,
            trans_kr TEXT,
            topic TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            word_count INTEGER DEFAULT 0
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS word_topics (
            word_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            PRIMARY KEY (word_id, topic_id),
            FOREIGN KEY (word_id) REFERENCES dictionary(id) ON DELETE CASCADE,
            FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
        )
    """)

    # Migrate: add new columns if missing
    existing = {row[1] for row in conn.execute("PRAGMA table_info(dictionary)")}
    for col in ("def_en", "def_uz", "def_kr", "examples_uz", "examples_kr",
                "trans_en", "trans_uz", "trans_kr"):
        if col not in existing:
            conn.execute(f"ALTER TABLE dictionary ADD COLUMN {col} TEXT")

    # Seed default topics
    defaults = [
        ("IT",),("Daily",),("Business",),("Science",),("Nature",),
        ("Art",),("Travel",),("Health",),("Psychology",),("Finance",),
        ("Sports",),("Food",),("Politics",),("Education",),("Technology",),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO topics (name) VALUES (?)", defaults
    )

    # Migrate existing words that have a topic string but no word_topics rows
    orphan_words = conn.execute("""
        SELECT d.id, d.topic FROM dictionary d
        WHERE d.topic IS NOT NULL AND d.topic != ''
          AND d.id NOT IN (SELECT DISTINCT word_id FROM word_topics)
    """).fetchall()
    for row in orphan_words:
        _link_topics(conn, row["id"], [row["topic"]])

    conn.commit()
    conn.close()


def _ensure_topic(conn, name: str) -> int:
    name = name.strip().title()
    conn.execute("INSERT OR IGNORE INTO topics (name, word_count) VALUES (?, 0)", (name,))
    row = conn.execute("SELECT id FROM topics WHERE name = ?", (name,)).fetchone()
    return row["id"]


def _link_topics(conn, word_id: int, topic_names: list):
    for name in topic_names:
        if not name:
            continue
        tid = _ensure_topic(conn, name)
        conn.execute(
            "INSERT OR IGNORE INTO word_topics (word_id, topic_id) VALUES (?, ?)",
            (word_id, tid)
        )
    # Recompute word_count for affected topics
    conn.execute("""
        UPDATE topics SET word_count = (
            SELECT COUNT(*) FROM word_topics WHERE topic_id = topics.id
        )
    """)


def get_topics():
    conn = get_conn()
    rows = conn.execute("""
        SELECT name, word_count FROM topics
        WHERE word_count > 0
        ORDER BY word_count DESC, name ASC
    """).fetchall()
    conn.close()
    return [{"name": r["name"], "count": r["word_count"]} for r in rows]


def get_random_word(exclude_id: int = None, topic: str = None):
    conn = get_conn()

    if topic:
        base = """
            SELECT d.* FROM dictionary d
            JOIN word_topics wt ON wt.word_id = d.id
            JOIN topics t ON t.id = wt.topic_id
            WHERE t.name = ?
        """
        params = [topic]
        if exclude_id:
            base += " AND d.id != ?"
            params.append(exclude_id)
        base += " ORDER BY RANDOM() LIMIT 1"
        row = conn.execute(base, params).fetchone()
    elif exclude_id:
        row = conn.execute(
            "SELECT * FROM dictionary WHERE id != ? ORDER BY RANDOM() LIMIT 1",
            (exclude_id,)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM dictionary ORDER BY RANDOM() LIMIT 1"
        ).fetchone()

    conn.close()
    if not row:
        return None

    d = dict(row)
    for field in ("examples", "examples_uz", "examples_kr"):
        try:
            d[field] = json.loads(d[field]) if d[field] else []
        except (json.JSONDecodeError, TypeError):
            d[field] = []

    # Attach topic list
    conn2 = get_conn()
    topic_rows = conn2.execute("""
        SELECT t.name FROM topics t
        JOIN word_topics wt ON wt.topic_id = t.id
        WHERE wt.word_id = ?
        ORDER BY t.name
    """, (d["id"],)).fetchall()
    conn2.close()
    d["topics"] = [r["name"] for r in topic_rows]

    return d


def get_word_count() -> int:
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM dictionary").fetchone()[0]
    conn.close()
    return count


def insert_words(words: list) -> int:
    conn = get_conn()
    inserted = 0
    for w in words:
        try:
            # topics can be a list or a single string
            raw_topics = w.get("topics") or w.get("topic") or []
            if isinstance(raw_topics, str):
                raw_topics = [raw_topics]

            conn.execute(
                """INSERT OR IGNORE INTO dictionary
                   (word_en, word_uz, word_kr,
                    def_ru, def_en, def_uz, def_kr,
                    examples, examples_uz, examples_kr,
                    trans_en, trans_uz, trans_kr, topic)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    w.get("en", "").strip(),
                    w.get("uz", "").strip(),
                    w.get("kr", "").strip(),
                    w.get("ru_def", "").strip(),
                    w.get("def_en", "").strip(),
                    w.get("def_uz", "").strip(),
                    w.get("def_kr", "").strip(),
                    json.dumps(w.get("ex", []),    ensure_ascii=False),
                    json.dumps(w.get("ex_uz", []), ensure_ascii=False),
                    json.dumps(w.get("ex_kr", []), ensure_ascii=False),
                    w.get("trans_en", "").strip(),
                    w.get("trans_uz", "").strip(),
                    w.get("trans_kr", "").strip(),
                    raw_topics[0] if raw_topics else "general",
                )
            )
            if conn.execute("SELECT changes()").fetchone()[0]:
                word_id = conn.execute(
                    "SELECT id FROM dictionary WHERE word_en = ?",
                    (w.get("en", "").strip(),)
                ).fetchone()["id"]
                _link_topics(conn, word_id, raw_topics)
                inserted += 1
        except Exception:
            pass

    conn.commit()
    conn.close()
    return inserted
