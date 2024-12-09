import ast
import re
from pathlib import Path

import pandas as pd
from py_pinyin_split import PinyinTokenizer
from pypinyin.contrib.tone_convert import to_tone, to_tone3

# Compile regex patterns once at module level
LEVEL_STAR_PATTERN = re.compile(r"UC::TBCL-level-(\d+)-star")
LEVEL_REGULAR_PATTERN = re.compile(r"UC::TBCL-level-(\d+)")
INITIAL_VOWEL = re.compile(r"^[aeiouāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]", re.IGNORECASE)
PINYIN_TOKENIZER = PinyinTokenizer(include_nonstandard=True)


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
    except (ValueError, SyntaxError) as e:
        print(f"ERROR: Received error: {e} while parsing {meaning}")
        return meaning  # Return original if parsing fails


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
        lambda row: _convert_pinyin_to_html(ast.literal_eval(row["pinyin"])), axis=1
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
