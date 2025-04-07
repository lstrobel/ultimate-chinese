# Contributing

Thank you for your interest in contributing!

## Adding or modifying card content

### Pinyin Guidelines

Here are some guidelines for contributing pronunciation data:

#### Choosing Pronunciations

- There are a lot of different ways to pronounce Chinese words, differing across dialects, regions, context, and even individual speakers. This deck is built for Chinese learners, so we aim to only provide a narrow view of the pronunciation of each word.
- This deck is not an authoritative source on pronunciation. In fact, it is generally difficult to find any single authoritative source which captures the aspects of pronunciation relevant to this deck. When adding or modifying pronunciations, try to cite as many sources as possible! I found [Wiktionary](https://en.wiktionary.org), [Pleco](https://www.pleco.com/), and the [Taiwanese MOE dictionary](https://www.moedict.tw/) to be good sources.
- When a word is a single character there are often multiple pronunciations for the various meanings of the word. We source and display pronunciations only relevant to the meaning present in the simple definition.

Because we aim to provide a narrow view of pronunciation, we exclude any pronunciations which are:

- **Highly regional or dialectal**: With the exception of Taiwan and Mainland China, we exclude pronunciations that are only used in specific regions.
- **Rare**: Not commonly used, or only used in specific contexts.
- **Historical**: No longer used in modern vernacular.
- **Literary**: Only used in literary readings, including songs, poems, or performance.
- **Generally non-standard**: Not considered standard in any context, or really just not the obvious choice for a learner.

#### Tagging Pronunciations

To help learners understand and prioritize different pronunciations, we tag each pronunciation with extra information. These are the tags we use:

- `Standard`: The default tag if a pronunciation would otherwise have no tags. This is the most common pronunciation of the word in Mandarin Chinese and is the one learners should prioritize.
- `variant`: Nonstandard but noteworthy variants. If specific to a region, use `Mainland (variant)` or `Taiwan (variant)`. Otherise use `variant`. This is kind of a catch-all. Even better if you can add a note about the context in which the variant is used.
- `Mainland` and `Mainland (variant)`: Pronunciations that are specific to Mainland China.
- `Taiwan` and `Taiwan (variant)`: Pronunciations that are specific to Taiwan.
- `erhua`: Pronunciations that include the erhua suffix. Pronunciations with the `erhua` tag don't also need a `Mainland` tag.
- `toneless variant`: Pronunciations that drop a tone.
- `has sandhi`: Pronunciations that are subject to tone sandhi.

There are also `meta:` prefixed tags which are temporary and used for organization.

#### Formatting pronunciations

In general, pinyin should contain no spaces and be all lowercase. The only exception is for seperable verbs/adjectives (which are actually a type of verb) which should be separated by a space.

This is a pretty loose guideline.

#### Tone Sandhi

Do not include tone sandhi in the pinyin, but do add a `has sandhi` tag if the word is subject to tone sandhi.

### Simple Definition Guidelines

Simple definitions aim to provide concise, learner-focused meanings for words. Each word can have multiple simple definitions to cover different parts of speech or core meanings. The system used for categorizing parts of speech is a custom mix of the parts of speech from the [ABC Chinese-English Comprehensive Dictionary](https://android.pleco.com/manual/240/abc.html#pos) and [An A to Z Grammar for Chinese Language Learners](https://chino.hol.es/mod/book/tool/print/index.php?id=218&chapterid=17286).

A simple definition consists of:

1.  A **`part_of_speech`**: The grammatical role of the word for this specific meaning:

    - `Noun`: General nouns, including people, places, things, and abstract concepts.
    - `Pronoun`
    - `Adverb`: Modifies verbs, adjectives, or other adverbs (e.g., 很, 都, 不). Many adjectives can also be used adverbially, but you should always add a separate definition for the adjectival use.
    - `Verb`: An umbrella term for all verbs. Use tags to specify more specific types, like those specified in the A to Z Grammar.
    - `Adjective`: While most "adjectives" are actually a subtype of stative verbs in Chinese, we use this category for ease of understanding. Learners will be aware of the quirks of Chinese adjectives.
    - `Conjunction`
    - `Preposition`: Often called coverbs.
    - `Measure Word`: Also known as classifiers.
    - `Interjection`: Exclamations or other short expressions.
    - `Determiner`: Specifies nouns (e.g., 這, 那, 每).
    - `Particle`: Other grammatical function words (e.g., 的, 了, 嗎).
    - `Phrase`: Multi-word expressions functioning as a unit. See ABC's description of "Set expressions that allow for little if any freedom to substitute different words."

2.  **`tags`** (Optional): Add specificity and context to the part of speech. Multiple tags can be used. Available tags and their descriptions:

    - `place-word`: (Noun) Inherently denotes location, does not need a preposition.
    - `time-word`: (Noun) Denotes time. Can function adverbially.
    - `transitive`: (Verb) Takes a direct object.
    - `intransitive`: (Verb) Does not take a direct object.
    - `separable`: (Verb) Verb with internal V+O structure that can be split (e.g., 唱歌 -> 唱(了)歌).
    - `auxiliary`: (Verb) Helping verb. Precedes main verb; negation is before it (e.g., 能, 會, 可以).
    - `process`: (Verb) Denotes an instantaneous change of state. Often uses 沒 for past negation (e.g., 死, 忘).
    - `stative`: (Verb) Denotes a non-time-sensitive state. Often uses 不 for negation. Adjectives are a subclass of these.
    - `mainly-attributive`: (Adjective) Normally only modifies nouns (e.g., 公共), not used as a predicate (\*很公共 is incorrrect).
    - `mainly-predicative`: (Adjective) Normally only used as a predicate (e.g., 夠), not attributive (\*夠時間 is incorrect).
    - `idiom`: (Phrase) Meaning is not literal. This is not the right tag for Chengyu.
    - `sentence-adv`: (Phrase) Functions like an adverb modifying the whole sentence.

3.  **`meaning`**: A concise definition in English.

    - For Verbs, use "to" (e.g., "to eat").
    - For Adjectives (Stative Verbs), omit "to be" (e.g., use "good" instead of "to be good").
    - For Measure Words, surround the measure word in parentheses (e.g., "(for people)").
    - Use parentheses to denote optional clarifying examples (e.g., "to do (something)") or usage contexts (e.g., "(finance) profit").
    - Use square brackets to denote other non-gloss meanings (e.g. [indicating motion away from the speaker]).

4.  **`classifiers`** (Optional, for Nouns only): A list of applicable measure words (classifiers) for this noun definition.

#### Choosing Simple Definitions

- Ensure that each simple definition is clear and concise, focusing on the most relevant meaning for learners.
- Not every meaning of a word needs to be included! Focus on the most common or important meanings.
- Many adjectives can be used adverbially, but you should always add a separate definition for the adjectival use.
- Many classifiers/measure words are also nouns, but you should always add a separate definition for the classifier use.

## Development

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

- `src/` - Build scripts and Brain Brew source
- `res/` - Resources (word definitions, media, styling)
- `recipes/` - Brain Brew recipe(s)
- `src/note_models/` - Anki templates and styling

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
