import json
import re
from pathlib import Path

import pandas as pd
from py_pinyin_split import PinyinTokenizer
from pypinyin.contrib.tone_convert import to_tone, to_tone3

from src.words_pydantic_models import Note

# Compile regex patterns once at module level
INITIAL_VOWEL = re.compile(r"^[aeiouāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]", re.IGNORECASE)
PINYIN_TOKENIZER = PinyinTokenizer(include_nonstandard=True)


def _reformat_meaning(meanings: list[str]) -> str:
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
            return "[" + _convert_pinyin_to_html([" ".join(converted_groups)]) + "]"

        new_m = re.sub(r"\[((?:[A-Za-z]+[0-9]\s*)+)\]", process_bracketed_pinyin, m)
        processed_meanings.append(new_m)

    items = "".join(f"<li>{m}</li>" for m in processed_meanings)
    return f"<ol>{items}</ol>"


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


def _convert_pinyin_to_html(pinyin_list: list[str]) -> str:
    """
    Convert pinyin to HTML with tone classes, using pypinyin for syllable detection.
    """
    # Convert string representations of lists to actual lists
    as_html = []

    for pinyin in pinyin_list:
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
        as_html.append("".join(converted))

    return " / ".join(as_html)


def build_tbcl_words(res_dir: Path, output_dir: Path) -> None:
    """Build TBCL word data files in the specified directory

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
                "id": note.sort,
                "hanzi": set(word.hanzi for word in note.words),
                "pinyin": set(
                    p.pinyin for word in note.words for p in word.pronuncations
                ),
                "definitions": note.definitions,
                "tags": note.tags,
                "guid": note.guid,
                "hanziaudio": set(
                    word.pronuncations[0].audio_file if word.pronuncations else None
                    for word in note.words
                ),
                "simpledefinition": note.simple_definition,
            }
            for note in notes
        ]
    )

    # Convert pinyin to HTML
    df["pinyin"] = df.apply(
        lambda row: _convert_pinyin_to_html(list(row["pinyin"])), axis=1
    )

    # Convert lists to HTML spans for word variants
    df["hanzi"] = df["hanzi"].apply(
        lambda x: "".join(
            f'<span class="word-variant">{variant}</span>' for variant in list(x)
        )
    )

    # Convert definitions column to HTML ordered lists
    df["definitions"] = df["definitions"].apply(_reformat_meaning)

    # Drop any None from hanziaudio sets
    df["hanziaudio"] = df["hanziaudio"].apply(lambda x: {a for a in x if a})
    # Add sound tags to audio filenames and rename word_audio column to hanziaudio
    df["hanziaudio"] = df["hanziaudio"].apply(
        lambda x: f"[sound:{list(x)[0]}]" if len(x) > 0 else ""
    )

    # Append "UC::" to every tag
    df["tags"] = df["tags"].apply(lambda x: [f"UC::{tag}" for tag in x])
    # Convert tags to simple comma-separated string
    df["tags"] = df["tags"].apply(lambda x: ", ".join(x))

    # Write processed data to output CSV
    output_path = output_dir / "tbcl_words.csv"
    print(output_path)
    df.to_csv(output_path, index=False)
