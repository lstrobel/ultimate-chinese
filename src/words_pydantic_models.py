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

        return sorted(tags, key=custom_sort) if tags is not None else []


class Word(BaseModel):
    hanzi: str
    pronunciations: list[Pronunciation] = pydantic.Field(min_length=1)


class SimpleDefinition(BaseModel):
    part_of_speech: str
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
    focus_entries: str | list[SimpleDefinition] | None = (
        None  # str is legacy formatting
    )
    note: str | None = None
    # TODO: Replace with more complex definition model? Support examples, etc.
    definitions: list[str] | None = None

    @field_validator("tags", mode="before")
    def dedupe_tags(cls, v):
        if v is None:
            return None
        return list(dict.fromkeys(v))  # Preserve order

    @field_serializer("tags", when_used="json")
    def serialize_tags(self, tags: list[str]) -> list[str]:
        return sorted(tags) if tags is not None else []
