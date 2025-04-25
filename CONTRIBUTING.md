# Contributing

Thank you for your interest in contributing!

## Development

If you would like to modify the build process for the deck, setup a development environment using the following steps.

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

## Project Structure

This project ultimately generates flashcards using [Brain Brew](https://github.com/ohare93/brain-brew), which turns a csv file into a set of Anki cards. However, we add a layer of complexity by using a custom build system to generate such a csv file from json source data.

This allows us to use a more structured format for the data, as well as easily inject styling into individual Anki fields.

The project is structured as follows:

- `res/` - Resources (word definitions, media, styling)
  - `words.json` - The main source of truth for the notes in the deck
  - `media/` - audio/fonts/icons
- `src/` - Build scripts and Brain Brew source
  - `words_pydantic_models.py` - The schema for `words.json`
  - `build_words.py` - The script that builds the csv file from `words.json`
  - `headers/` and `note_models/` - Brain Brew deck and card models
- `recipes/` - Brain Brew recipe(s)

## Adding or modifying card content

The source of truth for the deck is `res/words.json`. This file contains all the information about the words in the deck. It is structured as a list of notes, each with a set of fields. To add or modify a note, you should edit this file.

This deck is made for Chinese learners. It is not a dictionary, nor is it comprehensive. To this end, we have a few guidelines for adding or modifying card content.

### When to split notes or add a new note

> [!IMPORTANT]
> Anki makes a distinction between "notes" and "cards". A note is a single entry in the database, while a card is a specific way of displaying that note. For example, a single note can be displayed as a question or an answer, or in multiple different ways. This deck uses a single card type for all notes, so for us, a note is a card.

This deck was originally created by creating one note for each word in the Taiwanese Ministry of Education's [TOCFL](https://coct.naer.edu.tw/page.jsp?ID=41) word list. The Taiwanese MOE split some words into multiple notes, and that distinction may still exist in the deck. However, most notes should follow this criteria:

1. If a single word/character (set of hanzi) has multiple distinct pronunciations, each with their own meanings, they should be separate notes. Otherwise, they should be combined into a single note.
2. If two sets of hanzi have the same meaning, then they can be combined into a single note, with main- and sub-hanzi as appropriate. Use your best judgement when determining if two words have similar enough meaning.

Here are some concrete examples of this:

- The character "行" can be pronounced as "xíng" (to walk) or "háng" (a row/column). These are two different pronunciations, and each has a different meaning. Therefore, they are two different notes.
- "堂" has several distinct meanings (hall, measure word for classes, etc.), but they are all pronounced the same. In this deck they are all combined into a single note.
- "垃圾" (garbage) famously has two very different pronunciations across the strait: "lèsè" (Taiwan) and "lājī" (Mainland). However, they are fundamentally the same word with the same meaning. One note.
- "老鼠" and "鼠" are two different sets of hanzi, but their meanings are similar enough ("mouse" and "rat") that they can be combined into a single note.
- Often, a single character with a 子 suffix can be combined with the character it modifies. For example "巷子" (alley) and "巷" (alley) are combined into a single note.

#### Choosing Pronunciations

There are a lot of different ways to pronounce Chinese words, differing across dialects, regions, context, and even individual speakers. Our pronunciations are all romanized using [Hanyu Pinyin](https://en.wikipedia.org/wiki/Pinyin).

We aim to provide a narrow view of pronunciation. When at all possible, and agreed to across the strait, we display the Modern Standard Mandarin pronunciation. When it exists, we can instead add a distinction between the difference in colloquial pronunciation between Taiwan and standard Mainland Chinese. Due to its presence in proficiency tests, we also document erhua pronunciations. Finally, if a word has a nearly ubiquitous colloquial pronunciation that is not standard, we include that as well.

We do not include pronunciations that:

- Exist in other 方言/topolects (e.g., Cantonese, Hakka, etc.)
- Exist in colloquial Mandarin from other regions (e.g., Singapore, Malaysia, etc.)
- Are rare, archaic, historical, or literary
- Are variants of the standard pronunciation that are not commonly used

A rough guideline for choosing what pronunciations to include is: "would a Chinese teacher from (Taiwan/Mainland) accept this pronunciation as correct?" If the answer is yes, include it. If the answer is no, don't include it.

#### Tone Sandhi

Do not include tone sandhi in the pinyin, but do add a `has sandhi` tag if the word is subject to tone sandhi.

#### Tagging Pronunciations

WIP
<!-- 

To clarify the usage of different pronunciations, we use a tagging system. These are the tags we use:

- `Standard`: Modern Standard Mandarin pronunciation. This is the default pronunciation for a word. Generally agreed to across the strait.
- `variant`: Nonstandard but noteworthy variants. Even better if you can add a note about the context in which the variant is used.
- `Mainland`: Pronunciations that are specific to Mainland China.
- `Taiwan`: Pronunciations that are specific to Taiwan.
- `erhua`: 兒化, if it wasnt already obvious by the presence of 兒/儿. Pronunciations with the `erhua` tag don't also need a `Mainland` tag.
- `has sandhi`: Pronunciations that are subject to tone sandhi.

There are also `meta:` prefixed tags which are temporary and undocumented. 
-->

#### Formatting pronunciations

In general, pinyin should contain no spaces and be all lowercase. The exception is for separable verb-object compounds, where adding a space aids memorization of this feature. For example, "唱歌" (to sing) could be formatted as "chàng gē".

This is a pretty loose guideline.

### Focus Section Guidelines

The focus section is the portion of the note that contains those definitions/meanings that learners should try to remember and grade themselves on when reviewing a note. It is not necessary for the focus section on a card to contain every sense of a character or word. The entries should be clear and concise, and should be those meanings that a speaker would most likely think of when they see the word.

The focus section consists of a list of rows, each corresponding roughly to a single definition. Right now, each row has the following fields:

1. **`part_of_speech`**: A free-text field that describes the part of speech of the word. See below for more details.
2. **`tags`**: A list of tags that add specificity and context to the part of speech field. This is an optional field, but it can be useful for learners to understand how the word is used. See below for more details.
3. **`meaning`**: A concise definition in English. See below for more details.
4. **`classifiers`** (Optional, for Nouns only): A list of applicable measure words (classifiers) for this noun definition.

Focus sections for words later in the list can be more comprehensive.

#### Part of Speech Field

The `part_of_speech` field is a free-text field that describes the part of speech of the word. This is not a strict part of speech, but rather a way to categorize the usage of the word. The goal is to help learners understand how to use the word in context. Our focus is less on linguistic categories, and more on helping learners recall the grammar rules and usage of words in that context.

When possible, try to stay consistent with the categories already present in the deck.

#### Adjectives

Adjectives are a subclass of stative verbs in Chinese. They are not strictly adjectives, but rather a type of verb that describes a state. However, we use the term "adjective" for ease of understanding. Learners should be aware of the quirks of Chinese adjectives.

Adjectives can also sometimes be used as adverbs. For this, add a separate definition for the adjectival use.

**Tagging**: Some adjectives are only used in an attributive position, while others are only used in a predicative position. We use the tags `mainly-attributive` and `mainly-predicative` to indicate this.

**Style**: When adding meanings for adjectives, omit the "to be" in the definition.

#### Verbs

WIP

- Address verb-complement structures
- Address types of verbs

## Releasing

We use a modified version of [Semantic Versioning](https://semver.org/):

- `MAJOR`: Changes to the deck that require special attention from users, such as changes to the card structure.
- `MINOR`: Changes to the deck that would change the response of a user to already existing cards, such as changes to the simple definition or first pronunciation.
- `PATCH`: Changes to the deck that would not change the response of a user to already existing cards, like styling changes, new cards, or edits to existing cards that don't change the simple definition or first pronunciation.

## Roadmap

### Words Deck

Pronunciation vaidations to be done:

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
