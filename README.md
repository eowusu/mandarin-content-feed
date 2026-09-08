# Mandarin FlashCards Data Feed

Automated, versioned public data feed providing vocabulary, grammar cards, and interactive character definitions for the Mandarin FlashCards web and mobile applications.

### Endpoints
* **Raw JSON Feed**: `https://raw.githubusercontent.com/eowusu/mandarin-content-feed/main/flashcards.json`

### Content Schema
- `version`: Semantic version string.
- `last_updated`: ISO-8601 UTC timestamp of the latest change.
- `total_cards`: Integer count of active cards.
- `concepts`: Available study categories with IDs and emojis (Greetings, Time, Food, etc.).
- `types`: Card formats (`word`, `number`, `sentence`, `phrase`).
- `cards`: Array of flashcard objects containing:
  - `id`: Unique identifier (e.g. `card_001`).
  - `hanzi`: Chinese characters.
  - `pinyin`: Pinyin romanization with tone marks.
  - `english`: English translation.
  - `type`: One of `word`, `number`, `sentence`, `phrase`.
  - `concept`: Topic tag.
- `char_dictionary`: Mapping of individual Chinese characters to pinyin and English breakdown for interactive hover/tap tooltips.

### Managing Content
To add a card interactively:
```bash
python3 scripts/add_card.py
```

To validate schema, IDs, and dictionary coverage:
```bash
python3 scripts/validate_feed.py
```
