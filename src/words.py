import json
import re
from pathlib import Path

import pandas as pd
from airium import Airium
from py_pinyin_split import PinyinTokenizer
from pypinyin.contrib.tone_convert import to_tone, to_tone3

from src.words_pydantic_models import Note, Pronunciation

# Compile regex patterns once at module level
INITIAL_VOWEL = re.compile(r"^[aeiouāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]", re.IGNORECASE)
PINYIN_TOKENIZER = PinyinTokenizer(include_nonstandard=True)


def _syllable_to_html(syllable: str) -> str:
    """
    Process a single pinyin syllable and return its HTML representation.
    If the passed syllable is whitespace, just returns whitespace
    """
    if not syllable.isalpha():
        return syllable

    as_tone3 = to_tone3(syllable.lower(), neutral_tone_with_five=True)
    tone_num = next((c for c in as_tone3 if c.isdigit()), "5")
    return f'<span class="tone{tone_num}">{syllable}</span>'


def _convert_pinyin_to_html(pinyin: str) -> str:
    """
    Convert pinyin to HTML with tone classes, using pypinyin for syllable detection.
    """
    spans = PINYIN_TOKENIZER.span_tokenize(pinyin)
    converted = []
    current_pos = 0

    # Process each span
    for start, end in spans:
        # Add text before span
        converted.append(pinyin[current_pos:start])
        # Add transformed span text
        converted.append(_syllable_to_html(pinyin[start:end]))
        current_pos = end

    # Add remaining text after last span
    converted.append(pinyin[current_pos:])

    return "".join(converted)


def _reformat_definitions(meanings: list[str]) -> str:
    """Convert meaning string list to HTML ordered list and apply some formatting."""
    if not meanings:  # Handle empty list
        raise ValueError

    # Create HTML ordered list
    processed_meanings = []
    for m in meanings:
        # Add space before brackets if not present
        m = re.sub(r"(?<!\s)\[", " [", m)

        # Find bracketed pinyin sections and convert syllables
        def process_bracketed_pinyin(match):
            pinyin = match.group(1)
            # Preserve original spacing by splitting on existing spaces
            pinyin_groups = pinyin.split()
            converted_groups = []
            for group in pinyin_groups:
                syllables = re.findall(r"[A-Za-z]+[0-9]", group)
                converted = [to_tone(s.replace("u:", "ü")) for s in syllables]
                converted_groups.append("".join(converted))
            converted_groups_as_html = [
                _convert_pinyin_to_html(group) for group in converted_groups
            ]

            return "[" + " ".join(converted_groups_as_html) + "]"

        new_m = re.sub(r"\[((?:[A-Za-z]+[0-9]\s*)+)\]", process_bracketed_pinyin, m)
        processed_meanings.append(new_m)

    items = "".join(f"<li>{m}</li>" for m in processed_meanings)
    return f"<ol>{items}</ol>"


def _reformat_pronunciations(pronunciations: list[list[Pronunciation]]) -> str:
    a = Airium(source_minify=True)

    for i, sublist in enumerate(pronunciations):
        for pron in sublist:
            try:
                tags = sorted(pron.tags) if pron.tags else []
                if "erhua" in tags:
                    continue  # Skip erhua pronunciations
                with a.div(class_="pronunciation-row"):
                    with a.div(class_="pinyin-entry"):
                        with a.div():
                            as_html = _convert_pinyin_to_html(pron.pinyin)
                            if i == 0:
                                a(as_html)
                            else:
                                a(f"({as_html})")
                        if pron.audio_file:
                            a(f" [sound:{pron.audio_file}]")
                    with a.div(class_="pinyin-tags"):
                        for t in tags:
                            if not t.startswith("meta:"):  # Skip meta tags
                                with a.div(class_="pinyin-tag"):
                                    a(t)
                            if t == "meta:fix_me":
                                a("⚠️")
            except ValueError as e:
                print(f"Error processing pronunciation {pron}: {e}")
                raise e

    return str(a)


def build_notes(res_dir: Path, output_dir: Path) -> None:
    """Build CrowdAnki notes CSV file from JSON data.

    Args:
        input: Path to the input CSV file
        output_dir: Directory where the generated files will be written
    """

    # Read data
    with open(res_dir / "words.json") as p:
        notes = [Note.model_validate(obj) for obj in json.loads(p.read())]

    # convert to flat dataframe
    df = pd.DataFrame(
        [
            {
                "SortPosition": note.sort,
                "MainHanzi": note.words[0].hanzi,
                "AltHanzi": [word.hanzi for word in note.words[1:]],
                "PronunciationSection": [
                    [p for p in word.pronunciations] for word in note.words
                ],  # To be formatted
                "FocusSection": note.simple_definition,
                "DefinitionSection": note.definitions,  # To be formatted
                "tags": sorted(note.tags),
                "guid": note.guid,
            }
            for note in notes
        ]
    )

    # Convert AltHanzi to a comma-separated string
    df["AltHanzi"] = df["AltHanzi"].apply(lambda x: ", ".join(x))

    # Convert PronunciationSection to HTML
    df["PronunciationSection"] = df["PronunciationSection"].apply(
        _reformat_pronunciations
    )

    # Convert definitions to an HTML ordered list
    df["DefinitionSection"] = df["DefinitionSection"].apply(_reformat_definitions)

    # Append "UC::" to every tag
    df["tags"] = df["tags"].apply(lambda x: [f"UC::{tag}" for tag in x])
    # Convert tags to simple comma-separated string for CrowdAnki
    df["tags"] = df["tags"].apply(lambda x: ", ".join(x))

    # Write processed data to output CSV
    output_path = output_dir / "notes.csv"
    print(output_path)
    df.to_csv(output_path, index=False)
