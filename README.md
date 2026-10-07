# Anki: Ultimate Chinese

An attempt to make a comprehensive Mandarin Chinese vocab study deck for Anki, inspired by [Ultimate Geography](https://github.com/anki-geo/ultimate-geography).

Currently focused on Modern Standard Mandarin as spoken in Taiwan (國語), but I do plan to expand to support learners focused on the Mainland (普通话) as well.

If you have any suggestions or concerns, please leave an issue!

## Getting Started

### Adding the Deck to Anki

To add the deck, follow these steps on Anki Desktop:

1. Install the [CrowdAnki](https://github.com/Stvad/CrowdAnki) addon.
2. Download the latest release of this deck from the [GitHub repository](https://github.com/lstrobel/ultimate-chinese/releases).
3. Extract the downloaded archive.
4. Open Anki and go to `File` > `CrowdAnki: Import from disk`.
5. Study!

### Updating the Deck

To update the deck with the latest changes, you only need to re-import it using the same steps as above.

However, pay close attention to the version number of the release you are importing. Changes in the major or minor version (e.g., from 1.x.x to 2.x.x or from 1.2.x to 1.3.x) may include significant changes to the deck's structure or content, which could affect your existing cards. Read the release notes carefully to understand what you might need to do.

> [!CAUTION]
> Any changes you made to the field values of existing cards (e.g., adding tags, modifying definitions) will be overwritten when you reimport the deck. However, your review history and scheduling data will remain intact.

### How to Use This Deck

Please see [docs/HOW_TO_USE_THIS_DECK.md](docs/HOW_TO_USE_THIS_DECK.md) for some advice.

## Contributing

If you'd like to contribute new vocab, enhance the deck, fix issues, or build from source, please see [CONTRIBUTING.md](CONTRIBUTING.md) for instructions (currently a work in progress).

## License

For license information, please see [LICENSE.md](LICENSE.md).

## TODO

There should be some consideration for separation of single character cards vs multi-character word cards. Multi-characters better map 1:1 to English words, but single characters can be on a spectrum of "word" to "idea" which is hard to translate as flashcards. I think whatever taxonomy is chosen, it shouldnt try too hard to lump characters into strict categories: they are flashcards, not a dictionary.

Having a separate character note type would also allow for stroke order cards.

Idea: character and word cards are separate, but so combined that they are still learned in an appropriate order when you study the top-level deck.

Problem: I'd really like a more elegant way to handle multiple pronunciations or meanings for a single character or word. Multiple cards causes me to be unsure how to grade myself when I recall only one of the meanings/pronunciations. Multiple fields is ugly and hard to study. Pretty sure this is what sentence mining decks are solving.
    Ideas: Adding context (in the form of a sentence or associated idea) would definitely help to deliminate them, but it would also reveal that that word has multiple meaning, and therefore make it "easier" to remember the word. Is that okay? Or should there be "no cheating".
    Alternatively, we exclude those? Or combine them? aargh.

Problem: It's really hard to combine and keep track of multiple wordlists. e.g. TOCFL has 白 and HSK has 白色. Do I make two separate cards? Do I merge them? How do I keep track of their providence such that if the wordlists are updated, I can update my deck accordingly?
    - I think the solution here is actually to keep them as separate cards, as they *are* different: 白 is the character, and can have associated ideas, while 白色 is the word meaning specifically "white color". It's okay if they are different.
    - There will be some fun trickniess around ordering: remember that study where you might want to learn the component characters first, but sometimes the words are more common than the characters alone and you want to learn those first. This is solvable with careful ordering of the cards in the deck.

Idea: Perhaps the scope of the deck needs to narrow to a "first 10,000", and abandon the idea of being comprehensive. Then, to replace the gap, make very good sentence mining tooling.
    Problem: One thing I like about this approach is that you can measure your progress against standardized benchmarks. Abandoning that means you lose that metric.

2026-03:
Idea:  Ive long thought about how to separate out single characters: what if you have a "beginner" deck, where single characters and words live together, with simple definitions. Once you pass a certain proficiency, however, you can better comprehend the nuance: so spearate out the decks.