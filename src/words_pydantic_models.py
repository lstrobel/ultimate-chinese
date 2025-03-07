import pydantic
from pydantic import BaseModel, field_serializer


class Pronunciation(BaseModel):
    pinyin: str
    audio_file: str | None = None
    tags: set[str] | None = (
        None  # Tags on the pinyin, primary region info and variant info
    )

    @field_serializer("tags", when_used="json")
    def serialize_my_set(self, tags: set[str]) -> list[str]:
        # Sort so that the most important tags come first
        def custom_sort(tag: str) -> tuple[int, str]:
            if tag == "Standard":
                return (0, tag)
            if tag in ["Mainland", "Taiwan"]:
                return (1, tag)
            if tag.startswith("meta:"):
                return (4, tag)
            return (3, tag)

        return sorted(tags, key=custom_sort)


class Word(BaseModel):
    hanzi: str
    pronunciations: list[Pronunciation] = pydantic.Field(min_length=1)


class Note(BaseModel):
    guid: str
    sort: int
    # Word + variants. The first word is the canonical word, the rest are variants
    words: list[Word] = pydantic.Field(min_length=1)
    tags: set[str]
    simple_definition: str | None = None
    note: str | None = None  # Note to display on card
    # TODO: Replace with more complex definition model? Support examples, etc.
    definitions: list[str]

    @field_serializer("tags", when_used="json")
    def serialize_my_set(self, tags: set[str]) -> list[str]:
        return sorted(tags)
