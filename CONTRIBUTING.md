# Contributing

Thank you for your interest in contributing!

If your interest is in adding new vocabulary or modifying existing cards, please read [How to add words](docs/HOW_TO_ADD_WORDS.md) and the [card content guidelines](docs/CARD_CONTENT_GUIDELINES.md).

## Project Structure

This project ultimately generates flashcards using [Brain Brew](https://github.com/ohare93/brain-brew), which turns a csv file into a set of Anki cards. However, we add a layer of complexity by using a custom build system to generate such a csv file from json source data. This allows us to use a more structured format for the data, as well as easily inject styling into individual Anki fields.

Data flow:

`words.json` (source) → `build_words.py` (generates CSV) → Brain Brew (generates Anki deck)

The project is structured as follows:

- `res/` - Resources (word definitions, media, styling)
  - `words.json` - The main source of truth for the notes in the deck
  - `media/` - audio/fonts/icons
- `src/` - Build scripts
  - `brainbrew/` - Brainbrew specific source: note and deck models
  - `schema.py` - The schema for `words.json`
  - `build_words.py` - The script that builds the csv file from `words.json`
- `recipes/` - Brain Brew recipe(s)

## Versioning

We use a modified version of [Semantic Versioning](https://semver.org/):

- `MAJOR`: Changes to the deck that require special attention or manual work from users, such as changes to the card structure.
- `MINOR`: Changes to the deck that would change the response of a user to already existing cards, such as changes to the simple definition or first pronunciation.
- `PATCH`: Changes to the deck that would not change the response of a user to already existing cards, like styling changes, new cards, or minor edits to existing cards.

## Development

If you would like to modify the build scripts for the deck, setup a development environment using the following steps.

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [sass](https://sass-lang.com/install/)

### Quick Start

```bash
# Clone and setup environment
git clone https://github.com/lstrobel/ultimate-chinese.git
cd ultimate-chinese
uv sync

# Build the project
make build

# Optionally, package for release
make release
```

## Roadmap

### Words Deck

Pronunciation and content vaidations to be done:

- First pronunciations that arent Taiwan or Standard (what gives?)
- erhua variants as official pronunciations
- Make sure usage of "Standard" and other tags is consistent
  - Refactor tag system to account for official vs colloquial pronunciations while still allowing for regional variants
- Go back and be consistent for 那/這 na/nei zhe/zhei
- Add notes for variants - when are they used?

1. Add wiktionary TTS Audio for pronunciations
2. Add simple definitions for all words
3. Add parts of speech for all words
4. Expand definition sections to be more comprehensive: add example sentences, and grammar notes
5. Expand the wordlist with words from the official TOCFL wordlist and new HSK wordlist

### Characters Deck

1. Add a new deck: characters-only with writing practice

### Expansion decks

1. Add additional word decks for specific topics
   1. Colors
   2. Opposites
   3. Animals
   4. Food
   5. etc
2. Familial relationships
3. Chengyu/idioms deck

### Card Styling

1. Hide extra pronunciations - keep it to around two?
2. Color-code tags?
