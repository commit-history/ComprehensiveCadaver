#!/usr/bin/env python3
"""Analyze deck.json to report which fields are filled/missing per card and section."""

import json
import sys
from collections import defaultdict
from pathlib import Path

FIELD_NAMES = [
    "Question",          # 0
    "Question_EN",       # 1
    "Question_DE",       # 2
    "Question_FR",       # 3
    "Text_Question_EN",  # 4
    "Text_Question_DE",  # 5
    "Text_Question_FR",  # 6
    "Answer",            # 7 (image)
    "Answer_LA",         # 8
    "Answer_EN",         # 9
    "Answer_DE",         # 10
    "Answer_FR",         # 11
    "Description_EN",    # 12
    "Description_DE",    # 13
    "Description_FR",    # 14
    "Keywords",          # 15
    "Source",            # 16
]

TRANSLATION_FIELDS = [
    "Question_EN", "Question_DE", "Question_FR",
    "Text_Question_EN", "Text_Question_DE", "Text_Question_FR",
    "Answer_LA", "Answer_EN", "Answer_DE", "Answer_FR",
    "Description_EN", "Description_DE", "Description_FR",
]


def collect_notes(node, path=""):
    """Recursively collect all notes with their section path."""
    name = node.get("name", "")
    current_path = f"{path}::{name}" if path else name
    results = []
    for note in node.get("notes", []):
        results.append((current_path, note))
    for child in node.get("children", []):
        results.extend(collect_notes(child, current_path))
    return results


def is_filled(value: str) -> bool:
    """Check if a field value is non-empty (ignoring whitespace/HTML tags)."""
    if not value:
        return False
    stripped = value.strip()
    if not stripped:
        return False
    return True


def analyze(deck_path: str, verbose: bool = False):
    with open(deck_path) as f:
        data = json.load(f)

    all_notes = collect_notes(data)
    total = len(all_notes)

    # Per-field stats
    field_filled = defaultdict(int)
    field_missing = defaultdict(int)

    # Per-section stats
    section_stats = defaultdict(lambda: {
        "total": 0,
        "field_filled": defaultdict(int),
        "field_missing": defaultdict(int),
    })

    # Cards that need work
    incomplete_cards = []

    for section, note in all_notes:
        fields = note.get("fields", [])
        guid = note.get("guid", "?")
        missing_fields = []

        for i, fname in enumerate(FIELD_NAMES):
            value = fields[i] if i < len(fields) else ""
            filled = is_filled(value)
            if filled:
                field_filled[fname] += 1
                section_stats[section]["field_filled"][fname] += 1
            else:
                field_missing[fname] += 1
                section_stats[section]["field_missing"][fname] += 1
                missing_fields.append(fname)

        section_stats[section]["total"] += 1

        if missing_fields:
            incomplete_cards.append({
                "guid": guid,
                "section": section,
                "missing": missing_fields,
                "answer_la": fields[8] if len(fields) > 8 else "",
                "answer_en": fields[9] if len(fields) > 9 else "",
            })

    # --- Print Report ---
    print("=" * 80)
    print(f"DECK ANALYSIS REPORT — {total} total cards")
    print("=" * 80)

    # Overall field completion
    print("\n## Overall Field Completion\n")
    print(f"{'Field':<20} {'Filled':>8} {'Missing':>8} {'% Done':>8}")
    print("-" * 48)
    for fname in FIELD_NAMES:
        filled = field_filled[fname]
        missing = field_missing[fname]
        pct = (filled / total * 100) if total else 0
        marker = " ✓" if missing == 0 else ""
        print(f"{fname:<20} {filled:>8} {missing:>8} {pct:>7.1f}%{marker}")

    # Translation fields only
    print("\n## Translation Fields Summary\n")
    total_translation_slots = total * len(TRANSLATION_FIELDS)
    total_filled = sum(field_filled[f] for f in TRANSLATION_FIELDS)
    total_missing_t = total_translation_slots - total_filled
    print(f"Total translation slots: {total_translation_slots}")
    print(f"Filled:                  {total_filled} ({total_filled/total_translation_slots*100:.1f}%)")
    print(f"Missing:                 {total_missing_t} ({total_missing_t/total_translation_slots*100:.1f}%)")

    # Per-section breakdown
    print("\n## Per-Section Breakdown\n")
    for section in sorted(section_stats.keys()):
        stats = section_stats[section]
        sec_total = stats["total"]
        # Count cards fully complete in this section
        sec_label = section.split("::")[-1]
        missing_translation = 0
        for fname in TRANSLATION_FIELDS:
            missing_translation += stats["field_missing"].get(fname, 0)
        total_slots = sec_total * len(TRANSLATION_FIELDS)
        filled_slots = total_slots - missing_translation
        pct = filled_slots / total_slots * 100 if total_slots else 0
        print(f"  {sec_label} ({sec_total} cards): {pct:.0f}% translations filled")
        # Show which fields are missing
        missing_summary = []
        for fname in TRANSLATION_FIELDS:
            m = stats["field_missing"].get(fname, 0)
            if m > 0:
                missing_summary.append(f"{fname}:{m}")
        if missing_summary:
            print(f"    Missing: {', '.join(missing_summary)}")

    # Cards needing work (summary by missing-field pattern)
    print("\n## Missing Field Patterns\n")
    pattern_count = defaultdict(int)
    for card in incomplete_cards:
        pattern = tuple(card["missing"])
        pattern_count[pattern] += 1
    for pattern, count in sorted(pattern_count.items(), key=lambda x: -x[1]):
        print(f"  {count:>5}x  missing: {', '.join(pattern)}")

    # Verbose: list every incomplete card
    if verbose:
        print("\n## All Incomplete Cards\n")
        for card in incomplete_cards:
            label = card["answer_en"] or card["answer_la"] or card["guid"]
            print(f"  [{card['guid']}] {label}")
            print(f"    Section: {card['section']}")
            print(f"    Missing: {', '.join(card['missing'])}")

    return {
        "total": total,
        "field_filled": dict(field_filled),
        "field_missing": dict(field_missing),
        "incomplete_cards": incomplete_cards,
        "section_stats": {k: {"total": v["total"]} for k, v in section_stats.items()},
    }


if __name__ == "__main__":
    deck_path = sys.argv[1] if len(sys.argv) > 1 else "deck.json"
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    analyze(deck_path, verbose=verbose)
