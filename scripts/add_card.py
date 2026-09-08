#!/usr/bin/env python3
"""
Interactive helper to add a new flashcard to flashcards.json and prompt
for any missing character definitions in the dictionary.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

FEED_PATH = Path(__file__).parent.parent / "flashcards.json"

def is_cjk(char: str) -> bool:
    code = ord(char)
    return 0x4E00 <= code <= 0x9FFF or 0x3400 <= code <= 0x4DBF or 0x20000 <= code <= 0x2A6DF

def main():
    if not FEED_PATH.exists():
        print(f"Error: {FEED_PATH} not found.")
        sys.exit(1)

    with open(FEED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    cards = data.get("cards", [])
    dictionary = data.get("char_dictionary", {})

    print("=== Add a New Mandarin Flashcard ===")
    hanzi = input("Hanzi (Chinese characters): ").strip()
    if not hanzi:
        print("Aborted.")
        sys.exit(0)

    pinyin = input("Pinyin (with tone marks, e.g. nǐ hǎo): ").strip()
    english = input("English translation: ").strip()

    print("\nTypes: 1) word  2) sentence  3) number  4) phrase")
    type_choice = input("Select type (1-4) [1]: ").strip() or "1"
    type_map = {"1": "word", "2": "sentence", "3": "number", "4": "phrase"}
    card_type = type_map.get(type_choice, "word")

    concepts = [c["id"] for c in data.get("concepts", []) if c["id"] != "all"]
    print("\nConcepts:")
    for idx, c in enumerate(concepts, 1):
        print(f"  {idx}) {c}")
    concept_idx = input(f"Select concept (1-{len(concepts)}) [1]: ").strip() or "1"
    try:
        card_concept = concepts[int(concept_idx) - 1]
    except Exception:
        card_concept = "phrases"

    new_id = f"card_{len(cards) + 1:03d}"
    new_card = {
        "id": new_id,
        "hanzi": hanzi,
        "pinyin": pinyin,
        "english": english,
        "type": card_type,
        "concept": card_concept
    }

    cards.append(new_card)

    # Check for missing characters
    missing_chars = [ch for ch in hanzi if is_cjk(ch) and ch not in dictionary]
    if missing_chars:
        print(f"\nMissing definitions for characters: {', '.join(missing_chars)}")
        for ch in missing_chars:
            ch_pinyin = input(f"  Pinyin for '{ch}': ").strip()
            ch_eng = input(f"  English for '{ch}': ").strip()
            if ch_pinyin and ch_eng:
                dictionary[ch] = {"pinyin": ch_pinyin, "english": ch_eng}

    data["total_cards"] = len(cards)
    data["last_updated"] = datetime.now(timezone.utc).isoformat()

    with open(FEED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\n✅ Card '{hanzi}' ({new_id}) successfully added! Total cards: {len(cards)}")

if __name__ == "__main__":
    main()
