import itertools
from pathlib import Path
import ast
from typing import List
import pandas as pd
import re
from pinyin_split import split
from pypinyin.contrib.tone_convert import to_tone3, to_tone

# Compile regex patterns once at module level
LEVEL_STAR_PATTERN = re.compile(r"UC::TBCL-level-(\d+)-star")
LEVEL_REGULAR_PATTERN = re.compile(r"UC::TBCL-level-(\d+)")
INITIAL_VOWEL = re.compile(r"^[aeiouāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]", re.IGNORECASE)


def _extract_level(tags: str) -> float:
    """Extract TBCL level from tags string."""
    star_match = LEVEL_STAR_PATTERN.search(tags)
    if star_match:
        return float(star_match.group(1)) + 0.5

    regular_match = LEVEL_REGULAR_PATTERN.search(tags)
    return (
        float(regular_match.group(1)) if regular_match else 999.0
    )  # Default high number for sorting


def _sort_by_level_and_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """Sort tbcl words dataframe by TBCL level and frequency metrics."""
    # Extract level for sorting
    df["level"] = df["tags"].apply(_extract_level)

    # Sort by level (ascending) and frequencies (descending)
    df = df.sort_values(
        ["level", "spoken_freq", "written_freq"], ascending=[True, False, False]
    )

    # Reassign IDs based on new order
    df["id"] = range(1, len(df) + 1)

    # Drop temporary level column
    df = df.drop("level", axis=1)

    return df


def _reformat_meaning(meaning: str) -> str:
    """Convert meaning string list to HTML ordered list and apply some formatting."""
    # Safely evaluate string representation of list
    try:
        meanings = ast.literal_eval(meaning)
        if not meanings:  # Handle empty list
            raise ValueError
        # Create HTML ordered list

        processed_meanings = []
        for m in meanings:

            def _replace_pinyin(match):
                start_pos = match.start()
                needs_space = start_pos > 0 and m[start_pos - 1] != " "

                parts = re.findall(r"[^0-9]+[0-9]?", match.group(1))
                converted = [
                    _syllable_to_html(to_tone(part.replace("u:", "ü")))
                    for part in parts
                ]

                return (" " if needs_space else "") + "[" + "".join(converted) + "]"

            new_m = re.sub(r"\[(.*?)\]", _replace_pinyin, m)
            processed_meanings.append(new_m)

        items = "".join(f"<li>{m}</li>" for m in processed_meanings)
        return f"<ol>{items}</ol>"
    except (ValueError, SyntaxError) as e:
        print(f"ERROR: Received error: {e} while parsing {meaning}")
        return meaning  # Return original if parsing fails


def _split_pinyin(word: str, pinyin: str, max_chars: int) -> List:
    """Given a word and pinyin string from TBCL, return a list where entries are either a single pinyin syllable, or whitespace"""

    grouped = ["".join(g) for _, g in itertools.groupby(pinyin, str.isspace)]
    out = []

    discovered_syllables = 0
    for entry in grouped:
        if entry.isspace():
            out.append(entry)
            continue

        possible_splits = split(entry, include_erhua=True, include_nonstandard=True)

        if len(possible_splits) == 0:
            raise RuntimeError(f"No splits found for {word} {pinyin}!")

        if len(possible_splits) == 1:
            discovered_syllables += len(possible_splits[0])
            out.extend(possible_splits[0])
            continue

        # Prefer splits where no syllable starts with a vowel over splits where that is the case.
        no_initial_vowels = [
            split
            for split in possible_splits
            if not any(INITIAL_VOWEL.match(syllable) for syllable in split)
        ]
        valid_splits = no_initial_vowels if no_initial_vowels else possible_splits
        if len(valid_splits) == 1:
            discovered_syllables += len(valid_splits[0])
            out.extend(valid_splits[0])
        else:
            out.append(valid_splits)

    if not any(isinstance(x, list) for x in out):
        return out

    # Resolve remaining possiblities greedily. This works fine for our usecase, even if it wouldnt be robust to all scenarios
    def find_eligible(lst, remaining_length) -> List | None:
        eligible = [
            x for x in lst if isinstance(x, list) and len(x) <= remaining_length
        ]
        if len(eligible) > 1:
            print(
                f"Warning: Multiple eligible entries found for {lst}, {remaining_length}"
            )
        return eligible[0] if eligible else None

    remaining_syllables = max_chars - discovered_syllables
    reduced_out = []
    for entry in out:
        if isinstance(entry, list):
            selected = find_eligible(entry, remaining_syllables)
            if selected:
                reduced_out.extend(selected)
                remaining_syllables -= len(selected)
        else:
            reduced_out.append(entry)
    return reduced_out


def _syllable_to_html(syllable: str) -> str:
    """Process a single pinyin syllable and return its HTML representation. If the passed syllable is whitespace, just returns whitespace"""
    if syllable.isspace():
        return syllable

    as_tone3 = to_tone3(syllable.lower(), neutral_tone_with_five=True)
    tone_num = next((c for c in as_tone3 if c.isdigit()), "5")
    return f'<span class="tone{tone_num}">{syllable}</span>'


def _convert_pinyin_to_html(word_list: str, pinyin_list: str) -> str:
    """Convert pinyin to HTML with tone classes, using pypinyin for syllable detection."""
    # Convert string representations of lists to actual lists
    words = ast.literal_eval(word_list)
    pinyins = ast.literal_eval(pinyin_list)
    as_html = []

    max_chars = max(len(w) for w in words)

    for word, pinyin in zip(words, pinyins):
        if len(words) == len(pinyins):
            max_chars = len(word)

        split = _split_pinyin(word, pinyin, max_chars)
        as_html.append("".join(map(lambda x: _syllable_to_html(x), split)))

    return " / ".join(as_html)


def build_tbcl_words(input: Path, output_dir: Path) -> None:
    """Build TBCL word data files in the specified directory

    Args:
        input: Path to the input CSV file
        output_dir: Directory where the generated files will be written
    """

    # Read the input CSV
    df = pd.read_csv(input)

    # Convert pinyin to HTML
    df["pinyin"] = df.apply(
        lambda row: _convert_pinyin_to_html(row["word"], row["pinyin"]), axis=1
    )

    # Convert lists to HTML spans for word variants
    df["hanzi"] = df["word"].apply(
        lambda x: "".join(
            f'<span class="word-variant">{variant}</span>'
            for variant in ast.literal_eval(x)
        )
    )
    df["zhuyin"] = df["zhuyin"].apply(lambda x: " / ".join(ast.literal_eval(x)))

    # Drop the original word column since we've replaced it with hanzi
    df = df.drop("word", axis=1)

    # Rename definition column to match note model
    df = df.rename(columns={"definition": "meaning"})

    # Sort and reassign IDs
    df = _sort_by_level_and_frequency(df)

    # Convert meaning column to HTML ordered lists
    df["meaning"] = df["meaning"].apply(_reformat_meaning)

    # Add sound tags to audio filenames and rename word_audio column to hanziaudio
    if "word_audio" in df.columns:
        df = df.rename(columns={"word_audio": "hanziaudio"})
        df["hanziaudio"] = df["hanziaudio"].apply(
            lambda x: f"[sound:{x}]" if pd.notna(x) else x
        )

    # Reorder columns to put id, hanzi first and hanziaudio last if it exists
    cols = ["id", "hanzi"]
    remaining_cols = [col for col in df.columns if col not in ["id", "hanzi"]]
    cols.extend(remaining_cols)
    df = df[cols]

    # Write processed data to output CSV
    output_path = output_dir / "tbcl_words.csv"
    print(output_path)
    df.to_csv(output_path, index=False)
