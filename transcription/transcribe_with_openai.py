"""
Transcribe anatomy card images using OpenAI GPT-4o vision API.

Usage:
    python3 transcription/transcribe_with_openai.py

Reads /tmp/transcription_manifest.json and processes all pending items.
Writes transcription JSONs to media-transcriptions/.
"""

import asyncio
import base64
import json
import os
import sys
import time
from pathlib import Path

import openai

TRANSCRIPTION_DIR = "media-transcriptions"
MANIFEST_PATH = "/tmp/transcription_manifest.json"
MAX_CONCURRENT = 15
MODEL = "gpt-5.2"

QUESTION_SYSTEM = """You are transcribing text from anatomy flashcard images. This is a QUESTION card.
Extract the following and return ONLY valid JSON (no markdown, no explanation):
{
  "question_en": "<the question text shown in the image, exactly as written>",
  "title": "<anatomical view caption shown below/near the image, empty string if none>",
  "attribution": "<source/copyright text if present, empty string if none>"
}"""

ANSWER_SYSTEM = """You are transcribing text from anatomy flashcard images. This is an ANSWER card.
Extract ALL labeled structures and text. Return ONLY valid JSON (no markdown, no explanation):
{
  "labels": [
    {
      "text": "<primary label/structure name>",
      "note": "<parenthetical note like '(Removed on right side)', empty string if none>",
      "details": ["<detail strings like 'Origin of gluteus medius', 'Insertion of piriformis'>"]
    }
  ],
  "title": "<anatomical view caption, empty string if none>",
  "subtitle": "<secondary caption text, empty string if none>",
  "orientation": "<orientation compass if present e.g. 'Superior (top), Inferior (bottom), Medial (left), Lateral (right)', empty string if none>",
  "attribution": "<source/copyright text if present, empty string if none>"
}
Include ALL labels visible in the image. For details, include origin/insertion info, bullet points, etc."""


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def build_answer_en(labels: list) -> str:
    parts = []
    for label in labels:
        text = label["text"]
        if label.get("note"):
            text += f" {label['note']}"
        parts.append(text)
        for detail in label.get("details", []):
            parts.append(detail)
    return " <br> ".join(parts)


async def transcribe_one(client, semaphore, item: dict) -> dict | None:
    output_path = os.path.join(TRANSCRIPTION_DIR, item["file"] + ".json")
    if os.path.exists(output_path):
        return None

    async with semaphore:
        img_path = item["path"]
        if not os.path.exists(img_path):
            print(f"  SKIP (missing): {item['file']}")
            return None

        b64 = encode_image(img_path)
        is_question = item["type"] == "question"
        system_msg = QUESTION_SYSTEM if is_question else ANSWER_SYSTEM

        for attempt in range(5):
            try:
                response = await client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{b64}",
                                        "detail": "low",
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": f"Transcribe this {'question' if is_question else 'answer'} card image. File: {item['file']}",
                                },
                            ],
                        },
                    ],
                    max_completion_tokens=1000,
                    temperature=0,
                )
                raw = response.choices[0].message.content.strip()
                # Strip markdown code fences if present
                if raw.startswith("```"):
                    raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                    if raw.endswith("```"):
                        raw = raw[:-3]
                    raw = raw.strip()

                data = json.loads(raw)

                # Build final output
                result = {"file": item["file"], "type": item["type"]}
                if is_question:
                    result["question_en"] = data.get("question_en", "")
                    result["title"] = data.get("title", "")
                    result["attribution"] = data.get("attribution", "")
                else:
                    labels = data.get("labels", [])
                    result["answer_en"] = build_answer_en(labels)
                    result["labels"] = labels
                    result["title"] = data.get("title", "")
                    result["subtitle"] = data.get("subtitle", "")
                    result["orientation"] = data.get("orientation", "")
                    result["attribution"] = data.get("attribution", "")

                with open(output_path, "w") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)

                return result

            except json.JSONDecodeError as e:
                print(f"  JSON error for {item['file']} (attempt {attempt+1}): {e}")
                if attempt == 4:
                    print(f"  FAILED: {item['file']} - raw response: {raw[:200]}")
                    return None
            except openai.RateLimitError as e:
                # Parse retry-after header if available, otherwise exponential backoff
                retry_after = getattr(e, 'response', None)
                if retry_after and hasattr(retry_after, 'headers'):
                    wait = float(retry_after.headers.get('retry-after', 2 ** (attempt + 2)))
                else:
                    wait = 2 ** (attempt + 2) + attempt * 5
                print(f"  Rate limited on {item['file']}, waiting {wait:.0f}s...")
                await asyncio.sleep(wait)
            except Exception as e:
                print(f"  Error for {item['file']} (attempt {attempt+1}): {e}")
                if attempt == 4:
                    return None
                await asyncio.sleep(2)

    return None


async def main():
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    # Filter already done
    pending = [
        item for item in manifest
        if not os.path.exists(os.path.join(TRANSCRIPTION_DIR, item["file"] + ".json"))
    ]

    print(f"Total in manifest: {len(manifest)}")
    print(f"Already done: {len(manifest) - len(pending)}")
    print(f"Pending: {len(pending)}")

    if not pending:
        print("Nothing to do!")
        return

    os.makedirs(TRANSCRIPTION_DIR, exist_ok=True)

    client = openai.AsyncOpenAI()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    start = time.time()
    done = 0
    failed = 0

    # Process in batches of 100 for progress reporting
    batch_size = 100
    for i in range(0, len(pending), batch_size):
        batch = pending[i : i + batch_size]
        tasks = [transcribe_one(client, semaphore, item) for item in batch]
        results = await asyncio.gather(*tasks)

        batch_done = sum(1 for r in results if r is not None)
        batch_failed = sum(1 for r in results if r is None)
        done += batch_done
        failed += batch_failed

        elapsed = time.time() - start
        rate = done / elapsed if elapsed > 0 else 0
        remaining = (len(pending) - done - failed) / rate if rate > 0 else 0
        print(
            f"Progress: {done + failed}/{len(pending)} "
            f"({done} ok, {failed} skipped/failed) "
            f"[{rate:.1f} img/s, ~{remaining:.0f}s remaining]"
        )

    elapsed = time.time() - start
    print(f"\nDone! {done} transcribed, {failed} failed in {elapsed:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
