import httpx
import json
import os
import re

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_URL     = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


async def generate_batch(context: str = "") -> list:
    context_hint = context.strip() or "general vocabulary for everyday life"

    prompt = (
        f"Act as a polyglot linguist. Generate a JSON array of exactly 100 unique vocabulary objects.\n"
        f"User Context: {context_hint}\n"
        f"Each object must have these exact keys:\n"
        f'  "en": English word (level B2-C1)\n'
        f'  "uz": Uzbek translation\n'
        f'  "kr": Korean translation in Hangul\n'
        f'  "ru_def": Short definition in Russian (1 sentence, max 15 words)\n'
        f'  "ex": array of exactly 5 example sentences in English\n'
        f'  "ex_uz": array of exactly 5 example sentences in Uzbek\n'
        f'  "ex_kr": array of exactly 5 example sentences in Korean (Hangul)\n'
        f'  "topic": one of: IT, Daily, Business, Science, Art, Travel\n'
        f"Rules:\n"
        f"  - 80% of words must relate to the user context\n"
        f"  - 20% must be general high-frequency words\n"
        f"  - No duplicate words\n"
        f"  - ex_uz and ex_kr must be natural translations of the English examples\n"
        f"Return ONLY a valid JSON array. No markdown, no explanation, no code fences."
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

    match = re.search(r"\[[\s\S]*\]", raw)
    if match:
        return json.loads(match.group())
    return json.loads(raw)
