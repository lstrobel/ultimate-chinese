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


def _process_single_pinyin(
    word: str, pinyin: str, max_chars: int | None = None
) -> str | None:
    """Process a single pinyin string and return its HTML representation."""
    possible_splits = split(pinyin, include_erhua=True, include_nonstandard=True)

    # Determine valid splits based on character count
    if max_chars is None:
        valid_splits = [split for split in possible_splits if len(split) == len(word)]
    else:
        valid_splits = [split for split in possible_splits if len(split) <= max_chars]

    if len(valid_splits) == 0:
        print(
            f"WARNING: No valid syllable splits for '{word}' "
            f"with pinyin '{pinyin}': {possible_splits}"
        )
        return None

    # If multiple valid splits exist, prefer the one where no syllables begin with a vowel
    if len(valid_splits) > 1:
        no_initial_vowels = [
            split
            for split in valid_splits
            if not any(
                syllable[0].lower() in "aeiouāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ"
                for syllable in split
            )
        ]
        if no_initial_vowels:
            syllables = no_initial_vowels[0]
        else:
            syllables = valid_splits[0]
    else:
        syllables = valid_splits[0]
    tone_nums = []
    tone_marks = []

    for syllable in syllables:
        tone_nums.append(to_tone3(syllable, neutral_tone_with_five=True))
        tone_marks.append(syllable)

    # Verify against the original pinyin
    verify = "".join(tone_marks).replace(" ", "")
    if not pinyin or verify != pinyin.replace(" ", "").strip():
        print(
            f"WARNING: Pinyin verification failed for word '{word}'. "
            f"Expected '{pinyin}', but pypinyin produced '{verify}'"
        )
        return None

    # Convert to HTML
    html_syllables = []
    for tone_num, tone_mark in zip(tone_nums, tone_marks):
        tone = tone_num[-1] if tone_num[-1].isdigit() else "5"
        html_syllables.append(f'<span class="tone{tone}">{tone_mark}</span>')

    return "".join(html_syllables)


def _convert_pinyin_to_html(word: str, pinyin: str) -> str:
    """Convert pinyin to HTML with tone classes, using pypinyin for syllable detection."""
    words = [w.strip() for w in word.split("/") if w]
    pinyins = [p.strip() for p in pinyin.split("/") if p]
    html_alternatives = []

    if len(words) == len(pinyins):
        # Process each word-pinyin pair
        for word, pinyin in zip(words, pinyins):
            html = _process_single_pinyin(word, pinyin)
            if html is None:
                return ["ERR"]
            html_alternatives.append(html)
    else:
        # Process each pinyin with max character limit
        max_chars = max(len(w) for w in words)
        for pinyin in pinyins:
            html = _process_single_pinyin(words[0], pinyin, max_chars)
            if html is None:
                return ["ERR"]
            html_alternatives.append(html)

    return " / ".join(html_alternatives)


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
