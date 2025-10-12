# Ultimate Chinese - AI Coding Assistant Instructions

## Project Overview

This project generates a comprehensive Anki flashcard deck for learning Mandarin Chinese (Taiwanese focus). It uses a **custom build pipeline** that transforms structured JSON data (`res/words.json`) into CrowdAnki-compatible Anki decks via CSV intermediates and Brain Brew.

**Architecture Flow**: `words.json` (source) → `build_words.py` (generates CSV) → Brain Brew (generates Anki deck)

## Critical Build System

### Build Commands (via Makefile)
```bash
make build     # Full build: JSON→CSV→Anki deck
make release   # Build + zip for distribution
make format    # Format Python code + normalize words.json
```

**Key Build Steps**:
1. `src/build_words.py` converts `res/words.json` to `build/words.csv` with HTML formatting
2. `sass` compiles `src/brainbrew/note_models/style.scss` to `build/style.css`
3. Brain Brew runs recipe at `src/brainbrew/recipes/source_to_anki.yaml`

### Environment Setup
- **Python**: 3.12+ managed with `uv` (not pip)
- **Install dependencies**: `uv sync` (not `pip install`)
- **Run scripts**: `uv run script.py` (not `python script.py`)
- **External tools**: `sass` for CSS compilation

## Data Models & Schemas

### Core Schema (`src/schema.py`)
The source of truth is `res/words.json`, validated by Pydantic models:

```python
Note → guid, sort, words[], tags[], focus_entries, definitions[]
  └─ Word → hanzi, pronunciations[]
      └─ Pronunciation → pinyin, audio_file, tags[]
```

### Tag System
- **Pronunciation tags**: `Standard`, `Mainland`, `Taiwan`, `variant`, `erhua`, `meta:fix_me`
- **Note tags**: Prefixed with `UC::` during build (e.g., `UC::TOCFL-1`)
- **Tag serialization**: Auto-sorted by importance (Standard > Mainland/Taiwan > other > meta:*)

## Companion Project: uc-scripts

The `uc-scripts` workspace contains **utility tools** for data generation:
- `src/tool/new_words_tool.py`: Interactive CLI for adding notes to `words.json`
- `src/scripts/`: One-off generation scripts (reference only, not maintained)
- Uses identical Pydantic models in `src/words_pydantic_models.py`

## File Organization

- **Source data**: `res/words.json` (manually edited or via tools)
- **Media**: `res/media/audio/*.oga` (audio files), `res/media/styling/` (fonts/icons)
- **Build artifacts**: `build/` (git-ignored, regenerated on build)
- **Brain Brew config**: `src/brainbrew/` (note models, recipes, templates)

## Common Tasks

### Adding/Modifying Words
1. Edit `res/words.json` directly OR use `uc-scripts/src/tool/new_words_tool.py`
2. Run `make format` to normalize JSON
3. Run `make build` to test changes

### Changing Card Appearance
1. Edit `src/brainbrew/note_models/style.scss` for styling
2. Edit `src/brainbrew/note_models/Vocab_Review.html` for layout
3. Run `make build` (auto-compiles SCSS)

### Adding New Fields
1. Update `src/schema.py` (Pydantic models)
2. Ensure that the date in `res/words.json` matches the new schema
3. Modify `src/build_words.py` formatting functions
4. Update `src/brainbrew/note_models/Ultimate_Chinese.yaml` (field definitions)
5. Update `src/brainbrew/note_models/Vocab_Review.html` (template)

## Testing & Validation

- **Format validation**: `make format` (runs Ruff + normalizes JSON via Pydantic)
- **Build test**: `make build` (catches schema violations and formatting errors)
- **Import test**: Use CrowdAnki addon in Anki to import `build/Ultimate_Chinese/`

## Python Conventions

- **Type hints**: Required on all functions
- **Linting**: Ruff (config in `pyproject.toml`)
- **String handling**: UTF-8 everywhere, `ensure_ascii=False` in JSON dumps
- **Regex patterns**: Compile at module level (see `INITIAL_VOWEL`, `PINYIN_TOKENIZER`)
