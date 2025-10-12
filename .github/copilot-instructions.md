# Ultimate Chinese - AI Coding Assistant Instructions

## Project Goal

This project generates an Anki flashcard deck for learning Mandarin Chinese. Cards include multiple pronunciations (Standard/Taiwan/Mainland variants), tone information, and structured definitions with parts of speech.

## Architecture

**Build Pipeline**: `res/words.json` (JSON source) → `src/build_words.py` (generates CSV with HTML) → Brain Brew (generates CrowdAnki deck)

**Key Commands**:
```bash
make build     # Full build: JSON→CSV→Anki deck
make release   # Build + zip for distribution
make format    # Format code + normalize words.json
```

## ⚠️ Python Environment

**ALWAYS use `uv`, never `pip`**:
- Install dependencies: `uv sync`
- Run scripts: `uv run script.py`
- Python 3.12+ required

## Directory Structure

```
ultimate-chinese/
├── res/
│   ├── words.json              # SOURCE OF TRUTH - all card data
│   └── media/                  # Audio files (.oga), fonts, icons
├── src/
│   ├── schema.py               # Pydantic models (Note/Word/Pronunciation)
│   ├── build_words.py          # JSON→CSV converter
│   ├── format_json.py          # JSON normalizer
│   └── brainbrew/              # Brain Brew config (note models, templates, recipes)
└── build/                      # Generated files (git-ignored)

uc-scripts/                     # Companion workspace
├── src/tool/                   # Reusable tools (new_words_tool.py)
└── src/scripts/                # One-off generation scripts
```

## Script Locations

- **Community-useful scripts** → `ultimate-chinese/` (maintained, versioned)
- **Personal one-off scripts** → `uc-scripts/` (keeps main repo clean)

## Common Workflows

**Edit words**: Modify `res/words.json` directly OR use `uc-scripts/src/tool/new_words_tool.py`
**Change styling**: Edit `src/brainbrew/note_models/style.scss` (auto-compiles via Makefile)
**Add fields**: Update `schema.py` → `build_words.py` → `Ultimate_Chinese.yaml` → `Vocab_Review.html`
