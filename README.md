# Anki: Ultimate Chinese

An attempt to make a complete and comprehensive Chinese study deck for Anki, inspired by [Ultimate Geography](https://github.com/anki-geo/ultimate-geography).

Currently focused on Taiwanese Mandarin due to the priorities of the creator, but I do plan to expand to support learners focused on Mainland Mandarin as well.

If you have any suggestions or concerns, please leave an issue.

TBCL data was originally sourced from: https://coct.naer.edu.tw/page.jsp?ID=41

## Pinyin Guidelines

Here are some guidelines for contributing pronunciation data:

### Choosing Pronunciations

- There are a lot of different ways to pronounce Chinese words, differing across dialects, regions, context, and even individual speakers. This deck is built for Chinese learners, so we aim to only provide a narrow view of the pronunciation of each word.
- This deck is not an authoritative source on pronunciation. In fact, it is generally difficult to find any single authoritative source which captures the aspects of pronunciation relevant to this deck. When adding or modifying pronunciations, try to cite as many sources as possible! I found [Wiktionary](https://en.wiktionary.org), [Pleco](https://www.pleco.com/), and the [Taiwanese MOE dictionary](https://www.moedict.tw/) to be good sources.
- When a word is a single character there are often multiple pronunciations for the various meanings of the word. We source and display pronunciations only relevant to the meaning present in the simple definition.

Because we aim to provide a narrow view of pronunciation, we exclude any pronunciations which are:

- **Highly regional or dialectal**: With the exception of Taiwan and Mainland China, we exclude pronunciations that are only used in specific regions.
- **Rare**: Not commonly used, or only used in specific contexts.
- **Historical**: No longer used in modern vernacular.
- **Literary**: Only used in literary readings, including songs, poems, or performance.
- **Generally non-standard**: Not considered standard in any context, or really just not the obvious choice for a learner.

### Tagging Pronunciations

To help learners understand and prioritize different pronunciations, we tag each pronunciation with extra information. These are the tags we use:

- `Standard`: The default tag if a pronunciation would otherwise have no tags. This is the most common pronunciation of the word in Mandarin Chinese and is the one learners should prioritize.
- `variant`: Nonstandard but noteworthy variants. If specific to a region, use `Mainland (variant)` or `Taiwan (variant)`. Otherise use `variant`. This is kind of a catch-all. Even better if you can add a note about the context in which the variant is used.
- `Mainland` and `Mainland (variant)`: Pronunciations that are specific to Mainland China.
- `Taiwan` and `Taiwan (variant)`: Pronunciations that are specific to Taiwan.
- `erhua`: Pronunciations that include the erhua suffix. Pronunciations with the `erhua` tag don't also need a `Mainland` tag.
- `toneless variant`: Pronunciations that drop a tone.
- `has sandhi`: Pronunciations that are subject to tone sandhi.

There are also `meta:` prefixed tags which are temporary and used for organization.

### Formatting pronunciations

In general, pinyin should contain no spaces and be all lowercase. However, there are some exceptions:

- Seperable verbs
- Adjective-noun compounds
- Verb-noun compounds

This is a pretty loose guideline.

### Tone Sandhi

Do not include tone sandhi in the pinyin, but do add a `has sandhi` tag if the word is subject to tone sandhi.

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
- Go back and be consistent for 那/這 na/nei zhe/zhei

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
