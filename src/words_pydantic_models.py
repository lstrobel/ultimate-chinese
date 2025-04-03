from enum import Enum

import pydantic
from pydantic import BaseModel, field_serializer, field_validator


class Pronunciation(BaseModel):
    pinyin: str
    audio_file: str | None = None
    tags: list[str] | None = None

    @field_validator("tags", mode="before")
    def dedupe_tags(cls, v):
        if v is None:
            return None
        return list(dict.fromkeys(v))  # Preserve order

    @field_serializer("tags", when_used="json")
    def serialize_tags(self, tags: list[str]) -> list[str]:
        # Sort so that the most important tags come first
        def custom_sort(tag: str) -> tuple[int, str]:
            if tag == "Standard":
                return (0, tag)
            if tag in ["Mainland", "Taiwan"]:
                return (1, tag)
            if tag.startswith("meta:"):
                return (4, tag)
            return (3, tag)

        return sorted(tags, key=custom_sort) if tags is not None else None


class Word(BaseModel):
    hanzi: str
    pronunciations: list[Pronunciation] = pydantic.Field(min_length=1)


class PartOfSpeech(Enum):
    NOUN = "Noun"
    PRONOUN = "Pronoun"

    ADVERB = "Adverb"
    VERB = "Verb"
    ADJECTIVE = "Adjective"  # A subclass/subtype of stative verbs

    CONJUNCTION = "Conjunction"
    PREPOSITION = "Preposition"
    MEASURE_WORD = "Measure Word"
    INTERJECTION = "Interjection"
    DETERMINER = "Determiner"
    PARTICLE = "Particle"

    PHRASE = "Phrase"


# Descriptions for common POS tags
POS_TAG_DESCRIPTIONS = {
    # Noun Tags
    "place-word": "Inherently denotes location, does not need a preposition.",
    "time-word": "Denotes time. Can function adverbially.",
    # Verb Tags
    "transitive": "Takes a direct object.",
    "intransitive": "Does not take a direct object.",
    "separable": "Verb with internal V+O structure that can be split.",
    "auxiliary": "Helping verb. Precedes main verb; negation is before it.",
    "process": "Denotes an instantaneous change of one state to another. Often uses 沒 for past negation.",
    "stative": "Denotes a non-time-sensitive state. Often uses 不 for negation.",
    # Adjective Tags
    "mainly-attributive": "Normally can only modify nouns (e.g., 公共), not function as a predicate (*很公共).",
    "mainly-predicative": "Normally only as a predicate (e.g., 夠), not attributive modification (*夠時間).",
    # Phrase/Expression Tags
    "idiom": "Meaning is not literal.",
    "sentence-adv": "Functions like an adverb modifying the whole sentence.",
}


class SimpleDefinition(BaseModel):
    part_of_speech: PartOfSpeech
    tags: list[str] | None = (
        None  # Tags to add specificity and context to the part of speech
    )
    meaning: str
    classifiers: list[str] | None = (
        None  # Measure words applicable to this definition, if a noun
    )


class Note(BaseModel):
    guid: str
    sort: int
    # Word + variants. The first word is the canonical word, the rest are variants
    words: list[Word] = pydantic.Field(min_length=1)
    tags: list[str]
    # The definition to focus on. `str` is legacy formatting
    simple_definition: str | list[SimpleDefinition] | None = None
    note: str | None = None  # Note to display on card
    # TODO: Replace with more complex definition model? Support examples, etc.
    definitions: list[str]

    @field_validator("tags", mode="before")
    def dedupe_tags(cls, v):
        if v is None:
            return None
        return list(dict.fromkeys(v))  # Preserve order

    @field_serializer("tags", when_used="json")
    def serialize_tags(self, tags: list[str]) -> list[str]:
        return sorted(tags) if tags is not None else []
