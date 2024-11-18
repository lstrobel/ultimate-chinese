import itertools
from pathlib import Path
import ast
import hashlib
import pandas as pd
import re
from pinyin_split import split
from pypinyin.contrib.tone_convert import to_tone3


def _extract_level(tags: str) -> float:
    """Extract TBCL level from tags string."""
    star_match = re.search(r"UC::TBCL-level-(\d+)-star", tags)
    if star_match:
        return float(star_match.group(1)) + 0.5

    regular_match = re.search(r"UC::TBCL-level-(\d+)", tags)
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


def _convert_meaning_to_html_list(meaning: str) -> str:
    """Convert meaning string list to HTML ordered list."""
    # Safely evaluate string representation of list
    try:
        meanings = ast.literal_eval(meaning)
        if not meanings:  # Handle empty list
            return ""
        # Create HTML ordered list on a single line
        items = "".join(f"<li>{m}</li>" for m in meanings)
        return f"<ol>{items}</ol>"
    except (ValueError, SyntaxError):
        return meaning  # Return original if parsing fails


def _split_pinyin(word: str, pinyin: str, max_chars: int):
    """Given a word and pinyin string from TBCL, return a list where entries are either a single pinyin syllable, or whitespace"""
    INITIAL_VOWEL = re.compile(r"^[aeiouāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]", re.IGNORECASE)

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
    def find_eligible(lst, remaining_length):
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


def _syllable_to_html(syllable: str):
    """Process a single pinyin syllable and return its HTML representation. If the passed syllable is whitespace, just returns whitespace"""
    if syllable.isspace():
        return syllable

    as_tone3 = to_tone3(syllable, neutral_tone_with_five=True)
    tone_num = as_tone3[-1] if as_tone3[-1].isdigit() else "5"
    return f'<span class="tone{tone_num}">{syllable}</span>'


def _convert_pinyin_to_html(word: str, pinyin: str) -> str:
    """Convert pinyin to HTML with tone classes, using pypinyin for syllable detection."""
    words = [w.strip() for w in word.split("/") if w]
    pinyins = [p.strip() for p in pinyin.split("/") if p]
    as_html = []

    max_chars = max(len(w) for w in words)

    for word, pinyin in zip(words, pinyins):
        if len(words) == len(pinyins):
            max_chars = len(word)

        split = _split_pinyin(word, pinyin, max_chars)
        # print(f"{words}, {split}, {max_chars}")
        as_html.append("".join(map(lambda x: _syllable_to_html(x), split)))

    return " / ".join(as_html)


def _generate_guid(word: str, pinyin: str) -> str:
    """Generate a deterministic GUID from word and pinyin."""
    # Combine word and pinyin, encode to bytes
    combined = f"{word}:{pinyin}".encode("utf-8")
    # Create SHA-256 hash and take first 32 chars
    return hashlib.sha256(combined).hexdigest()[:32]


def build_tbcl_words(input: Path, output_dir: Path) -> None:
    """Build TBCL word data files in the specified directory

    Args:
        input: Path to the input CSV file
        output_dir: Directory where the generated files will be written
    """

    # Read the input CSV
    df = pd.read_csv(input)

    # Generate GUIDs
    df["guid"] = df.apply(
        lambda row: _generate_guid(row["word"], row["pinyin"]), axis=1
    )

    # Convert pinyin to HTML
    df["pinyin"] = df.apply(
        lambda row: _convert_pinyin_to_html(row["word"], row["pinyin"]), axis=1
    )

    # Rename columns to match note model
    df = df.rename(columns={"word": "hanzi", "definition": "meaning"})

    # Sort and reassign IDs
    df = _sort_by_level_and_frequency(df)

    # Convert meaning column to HTML ordered lists
    df["meaning"] = df["meaning"].apply(_convert_meaning_to_html_list)

    # Write processed data to output CSV
    output_path = output_dir / "tbcl_words.csv"
    print(output_path)
    df.to_csv(output_path, index=False)
