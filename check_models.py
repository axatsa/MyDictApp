#!/usr/bin/env python3
"""
Check available Gemini models and pick the best one for MyDict.
Usage:  python check_models.py [API_KEY]
        or set GEMINI_API_KEY env var and just run python check_models.py
"""
import sys
import os
import json
import urllib.request
import urllib.error

API_KEY = sys.argv[1] if len(sys.argv) > 1 else os.getenv("GEMINI_API_KEY", "")

if not API_KEY:
    print("❌  Укажи ключ: python check_models.py <API_KEY>")
    sys.exit(1)

# ── Fetch model list ──────────────────────────────────────────────────────────
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
try:
    with urllib.request.urlopen(url, timeout=15) as r:
        data = json.loads(r.read())
except urllib.error.HTTPError as e:
    print(f"❌  HTTP {e.code}: {e.read().decode()}")
    sys.exit(1)

models = data.get("models", [])
if not models:
    print("❌  Модели не найдены. Проверь ключ.")
    sys.exit(1)

# ── Filter: only models that support generateContent ─────────────────────────
supported = [
    m for m in models
    if "generateContent" in m.get("supportedGenerationMethods", [])
]

# ── Score each model (lower = cheaper / faster) ───────────────────────────────
# Priority keywords (matched in model name):
TIERS = [
    ("flash-lite",  1),   # cheapest flash variant
    ("flash-8b",    2),   # small flash
    ("flash",       3),   # standard flash  ← sweet spot
    ("lite",        4),   # other lite variants
    ("pro-002",     7),   # older pro
    ("pro",         8),   # pro — capable but pricier
    ("ultra",       10),  # skip
    ("exp",         6),   # experimental — unstable, skip
]

def score(name: str) -> int:
    n = name.lower()
    for keyword, s in TIERS:
        if keyword in n:
            return s
    return 5  # unknown → middle

scored = sorted(supported, key=lambda m: (score(m["name"]), m["name"]))

# ── Print table ───────────────────────────────────────────────────────────────
print(f"\n{'MODEL NAME':<55} {'INPUT LIMIT':>12} {'OUTPUT LIMIT':>13}")
print("─" * 82)
for m in scored:
    name        = m["name"].replace("models/", "")
    in_lim      = m.get("inputTokenLimit", "?")
    out_lim     = m.get("outputTokenLimit", "?")
    marker      = "  ← РЕКОМЕНДУЕТСЯ" if m is scored[0] else ""
    print(f"  {name:<53} {str(in_lim):>12} {str(out_lim):>13}{marker}")

# ── Recommendation ────────────────────────────────────────────────────────────
best = scored[0]["name"].replace("models/", "")
print(f"\n✅  Лучший вариант для MyDict: {best}")
print(f'\nОбнови .env на сервере:\n  GEMINI_MODEL={best}')
print(f'\nИли задеплой сразу:\n  docker exec mydict_backend sh -c "GEMINI_MODEL={best} python seed.py"')
