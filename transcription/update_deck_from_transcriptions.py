"""
Update deck.json with transcribed Question_EN and Answer_EN from media transcriptions.

Usage:
    python3 update_deck_from_transcriptions.py "Osteology: Lower Limb"

This script:
1. Finds all notes in the specified deck
2. For each note, looks up the transcription JSON for its question and answer images
3. Sets field[1] (Question_EN) and field[6] (Answer_EN) in deck.json
"""

import json
import os
import re
import sys


DECK_JSON = "deck.json"
TRANSCRIPTION_DIR = "media-transcriptions"


def find_deck(deck, name):
    """Find a deck by exact name (recursive)."""
    if deck.get("name", "") == name:
        return deck
    for child in deck.get("children", []):
        result = find_deck(child, name)
        if result:
            return result
    return None


def collect_notes(deck):
    """Collect all notes from a deck and its children."""
    notes = list(deck.get("notes", []))
    for child in deck.get("children", []):
        notes.extend(collect_notes(child))
    return notes


def extract_image(field):
    """Extract image filename from an HTML img tag."""
    m = re.search(r'src=["\']([^"\']+)["\']', field)
    return m.group(1) if m else None


def load_transcription(image_file):
    """Load a transcription JSON for an image file."""
    path = os.path.join(TRANSCRIPTION_DIR, image_file + ".json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 update_deck_from_transcriptions.py <deck_name>")
        sys.exit(1)

    deck_name = sys.argv[1]

    with open(DECK_JSON, "r") as f:
        data = json.load(f)

    deck = find_deck(data, deck_name)
    if not deck:
        print(f"Deck '{deck_name}' not found.")
        sys.exit(1)

    notes = collect_notes(deck)

    updated_q = 0
    updated_a = 0
    missing_q = 0
    missing_a = 0

    for note in notes:
        question_img = extract_image(note["fields"][0])
        answer_img = extract_image(note["fields"][4])

        # Update Question_EN (field[1])
        if question_img:
            transcription = load_transcription(question_img)
            if transcription and transcription.get("question_en"):
                note["fields"][1] = transcription["question_en"]
                updated_q += 1
            else:
                missing_q += 1

        # Update Answer_EN (field[6])
        if answer_img:
            transcription = load_transcription(answer_img)
            if transcription and transcription.get("answer_en"):
                note["fields"][6] = transcription["answer_en"]
                updated_a += 1
            else:
                missing_a += 1

    print(f"Deck: {deck_name}")
    print(f"Notes: {len(notes)}")
    print(f"Question_EN updated: {updated_q}, missing: {missing_q}")
    print(f"Answer_EN updated: {updated_a}, missing: {missing_a}")

    with open(DECK_JSON, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("deck.json updated.")


if __name__ == "__main__":
    main()
