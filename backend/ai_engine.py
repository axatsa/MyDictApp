import httpx
import json
import os
import re

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_URL     = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

BATCH_SIZE = 50  # 100 words split into 2 requests — avoids JSON truncation


async def _request_batch(context: str, count: int, offset_hint: str = "") -> list:
    prompt = (
        f"Act as a polyglot linguist. Generate a JSON array of exactly {count} unique vocabulary objects.\n"
        f"User Context: {context}\n"
        + (f"Avoid words already generated: {offset_hint}\n" if offset_hint else "")
        + "Each object must have these exact keys:\n"
        f'  "en": English word (level B2-C1)\n'
        f'  "uz": Uzbek translation\n'
        f'  "kr": Korean translation in Hangul\n'
        f'  "ru_def": Short definition in Russian (1 sentence, max 12 words)\n'
        f'  "def_en": Short definition in English (1 sentence, max 12 words)\n'
        f'  "def_uz": Short definition in Uzbek (1 sentence, max 12 words)\n'
        f'  "def_kr": Short definition in Korean (1 sentence, max 12 words)\n'
        f'  "trans_en": IPA phonetic transcription of the English word, e.g. /ˈbɛntʃmɑːrk/\n'
        f'  "trans_uz": Latin pronunciation guide for the Uzbek word, e.g. [al-go-RÍTM]\n'
        f'  "trans_kr": Revised Romanization of the Korean word, e.g. benchimakeu\n'
        f'  "ex": array of exactly 8 English sentences — vary complexity: 2 simple (A2), 3 intermediate (B1-B2), 3 advanced (C1)\n'
        f'  "ex_uz": array of exactly 8 Uzbek sentences matching the same complexity order\n'
        f'  "ex_kr": array of exactly 8 Korean sentences (Hangul) matching the same complexity order\n'
        f'  "topics": array of 1-3 tags from: IT, Daily, Business, Science, Nature, Art, Travel, Health, Psychology, Finance, Sports, Food, Politics, Education, Technology\n'
        "Rules:\n"
        "  - 80% of words must relate to the user context\n"
        "  - 20% must be general high-frequency words\n"
        "  - No duplicate words\n"
        "Return ONLY a valid JSON array. No markdown, no explanation, no code fences."
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 16384,
            "responseMimeType": "application/json",
        },
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json=payload,
        )
        resp.raise_for_status()
        body = resp.json()

    raw = body["candidates"][0]["content"]["parts"][0]["text"]
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())

    # Extract JSON array, handle truncated response by cutting at last complete object
    match = re.search(r"\[[\s\S]*\]", raw)
    if match:
        return _safe_parse(match.group())
    return _safe_parse(raw)


def _safe_parse(text: str) -> list:
    """Parse JSON array, recovering partial output if truncated."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Find last complete object (ends with "}")
        last_brace = text.rfind("}")
        if last_brace == -1:
            raise
        truncated = text[: last_brace + 1]
        # Wrap into valid array
        if not truncated.strip().startswith("["):
            truncated = "[" + truncated
        truncated = truncated.rstrip(",") + "]"
        return json.loads(truncated)


async def generate_batch(context: str = "") -> list:
    ctx = context.strip() or "general vocabulary for everyday life"

    # First batch
    first = await _request_batch(ctx, BATCH_SIZE)

    # Second batch — hint to avoid duplicates
    used = ", ".join(w.get("en", "") for w in first[:10])
    second = await _request_batch(ctx, BATCH_SIZE, offset_hint=used)

    return first + second
