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
            examples TEXT,
            topic TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def get_random_word(exclude_id: int = None):
    conn = get_conn()
    if exclude_id:
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
    try:
        d["examples"] = json.loads(d["examples"]) if d["examples"] else []
    except (json.JSONDecodeError, TypeError):
        d["examples"] = []
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
            conn.execute(
                """INSERT OR IGNORE INTO dictionary
                   (word_en, word_uz, word_kr, def_ru, examples, topic)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    w.get("en", "").strip(),
                    w.get("uz", "").strip(),
                    w.get("kr", "").strip(),
                    w.get("ru_def", "").strip(),
                    json.dumps(w.get("ex", []), ensure_ascii=False),
                    w.get("topic", "general").strip(),
                )
            )
            if conn.execute("SELECT changes()").fetchone()[0]:
                inserted += 1
        except Exception:
            pass
    conn.commit()
    conn.close()
    return inserted
