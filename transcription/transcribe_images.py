"""
Transcribe images from ComprehensiveCadaver cards.

Usage:
    python3 transcribe_images.py "Osteology: Lower Limb"

This script:
1. Finds all notes in the specified deck
2. Builds a manifest of question/answer images
3. Saves the manifest to /tmp/transcription_manifest.json

The manifest is then used by Claude Code agents to transcribe each image.
Each transcription is saved as a JSON file in media-transcriptions/.
"""

import json
import os
import re
import sys


DECK_JSON = "deck.json"
MEDIA_DIR = "media"
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


def build_manifest(deck_name):
    """Build a manifest of images to transcribe."""
    with open(DECK_JSON, "r") as f:
        data = json.load(f)

    deck = find_deck(data, deck_name)
    if not deck:
        print(f"Deck '{deck_name}' not found.")
        print("Available decks:")
        def list_decks(d, depth=0):
            print(f"{'  ' * depth}{d.get('name', '?')}")
            for child in d.get("children", []):
                list_decks(child, depth + 1)
        list_decks(data)
        sys.exit(1)

    notes = collect_notes(deck)
    manifest = []

    for note in notes:
        guid = note.get("guid", "")
        keywords = note["fields"][12] if len(note["fields"]) > 12 else ""
        question_img = extract_image(note["fields"][0])
        answer_img = extract_image(note["fields"][4])

        if question_img:
            manifest.append({
                "guid": guid,
                "keywords": keywords,
                "file": question_img,
                "type": "question",
                "path": os.path.join(MEDIA_DIR, question_img),
            })
        if answer_img:
            manifest.append({
                "guid": guid,
                "keywords": keywords,
                "file": answer_img,
                "type": "answer",
                "path": os.path.join(MEDIA_DIR, answer_img),
            })

    return manifest


def get_pending(manifest):
    """Filter manifest to only images not yet transcribed."""
    pending = []
    for item in manifest:
        output_path = os.path.join(TRANSCRIPTION_DIR, item["file"] + ".json")
        if not os.path.exists(output_path):
            pending.append(item)
    return pending


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 transcribe_images.py <deck_name>")
        sys.exit(1)

    deck_name = sys.argv[1]
    manifest = build_manifest(deck_name)

    os.makedirs(TRANSCRIPTION_DIR, exist_ok=True)

    pending = get_pending(manifest)

    print(f"Deck: {deck_name}")
    print(f"Total images: {len(manifest)}")
    print(f"Already transcribed: {len(manifest) - len(pending)}")
    print(f"Pending: {len(pending)}")

    # Save manifest for agents to use
    manifest_path = "/tmp/transcription_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(pending, f, indent=2, ensure_ascii=False)
    print(f"Manifest saved to {manifest_path}")

    if pending:
        # Print chunk info for agent parallelization
        chunk_size = 50
        num_chunks = (len(pending) + chunk_size - 1) // chunk_size
        print(f"\nSuggested: {num_chunks} agents, {chunk_size} images each")
        for i in range(num_chunks):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, len(pending))
            print(f"  Chunk {i}: indices [{start}:{end}] ({end - start} images)")


if __name__ == "__main__":
    main()
