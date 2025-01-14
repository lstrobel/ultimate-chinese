import pydantic
from pydantic import BaseModel


class Pronuncation(BaseModel):
    pinyin: str
    audio_file: str | None = None
    association: str | None = (
        None  # Notes on the pinyin, mainly regional association and usage notes
    )


class Word(BaseModel):
    hanzi: str
    pronuncations: list[Pronuncation] = pydantic.Field(min_length=1)


class Note(BaseModel):
    guid: str
    sort: int
    words: list[Word] = pydantic.Field(min_length=1)  # Word + variants
    tags: list[str]
    # TODO: Replace with more complex definition model
    simple_definition: str | None = None
    definitions: list[str]
