#!/usr/bin/env python3
"""
Feed validation script for Mandarin FlashCards.
Validates JSON syntax, schema rules, and character dictionary coverage.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

FEED_PATH = Path(__file__).parent.parent / "flashcards.json"

REQUIRED_CARD_FIELDS = {"id", "hanzi", "pinyin", "english", "type", "concept"}
VALID_TYPES = {"word", "number", "sentence", "phrase"}
VALID_CONCEPTS = {
    "all", "greetings", "introductions", "time", "numbers",
    "countries", "food", "weather", "verbs_adjectives", "objects", "phrases"
}

def is_cjk(char: str) -> bool:
    """Check if a character is a CJK Unified Ideograph."""
    code = ord(char)
    return (
        0x4E00 <= code <= 0x9FFF or
        0x3400 <= code <= 0x4DBF or
        0x20000 <= code <= 0x2A6DF
    )

def validate():
    if not FEED_PATH.exists():
        print(f"❌ Error: {FEED_PATH} does not exist.")
        sys.exit(1)

    try:
        with open(FEED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {FEED_PATH}: {e}")
        sys.exit(1)

    errors = []
    warnings = []

    # 1. Top-level structure
    for key in ["version", "last_updated", "total_cards", "concepts", "types", "cards", "char_dictionary"]:
        if key not in data:
            errors.append(f"Missing top-level key: '{key}'")

    cards = data.get("cards", [])
    dictionary = data.get("char_dictionary", {})

    if len(cards) != data.get("total_cards"):
        warnings.append(f"total_cards ({data.get('total_cards')}) doesn't match actual card count ({len(cards)}). Auto-fixing.")
        data["total_cards"] = len(cards)

    # 2. Validate cards
    seen_ids = set()
    cjk_chars_in_cards = set()

    for idx, card in enumerate(cards):
        card_id = card.get("id")
        if not card_id:
            errors.append(f"Card #{idx} is missing 'id'")
        elif card_id in seen_ids:
            errors.append(f"Duplicate card id: '{card_id}'")
        else:
            seen_ids.add(card_id)

        for field in REQUIRED_CARD_FIELDS:
            if not card.get(field):
                errors.append(f"Card '{card_id}' missing required field '{field}'")

        card_type = card.get("type")
        if card_type not in VALID_TYPES:
            errors.append(f"Card '{card_id}' has invalid type '{card_type}'. Must be one of {VALID_TYPES}")

        concept = card.get("concept")
        if concept not in VALID_CONCEPTS:
            errors.append(f"Card '{card_id}' has invalid concept '{concept}'. Must be one of {VALID_CONCEPTS}")

        for ch in card.get("hanzi", ""):
            if is_cjk(ch):
                cjk_chars_in_cards.add(ch)

    # 3. Validate character dictionary
    for ch, entry in dictionary.items():
        if not isinstance(entry, dict) or "pinyin" not in entry or "english" not in entry:
            errors.append(f"Invalid dictionary entry for '{ch}': {entry}")

    missing_in_dict = sorted([ch for ch in cjk_chars_in_cards if ch not in dictionary])
    if missing_in_dict:
        warnings.append(f"{len(missing_in_dict)} Chinese character(s) in flashcards lack tooltip dictionary definitions: {', '.join(missing_in_dict)}")

    # Summary
    print(f"📊 Summary:")
    print(f"  • Total Cards: {len(cards)}")
    print(f"  • Total Dict Entries: {len(dictionary)}")
    print(f"  • Unique Chinese Characters in Cards: {len(cjk_chars_in_cards)}")
    print(f"  • Character Coverage: {((len(cjk_chars_in_cards) - len(missing_in_dict)) / len(cjk_chars_in_cards) * 100):.1f}%")

    if warnings:
        print("\n⚠️ Warnings:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\n❌ Errors found:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    print("\n✅ Feed validation PASSED! No schema errors found.")

    # Re-save with updated timestamp and total_cards
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(FEED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

if __name__ == "__main__":
    validate()
