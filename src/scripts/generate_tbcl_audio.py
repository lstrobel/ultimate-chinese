#!/usr/bin/env python3
import itertools
import os
import re
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pypinyin.contrib.tone_convert import to_tone3
from tts_generator import TTSGenerator

# Regex patterns for pinyin processing
INITIAL_VOWEL = re.compile(r"^[aeiouāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]", re.IGNORECASE)


def _split_pinyin(word: str, pinyin: str, max_chars: int) -> list:
    """Given a word and pinyin string from TBCL, return a list where entries are either a single pinyin syllable, or whitespace"""
    from pinyin_split import split

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

        # Prefer splits where no syllable starts with a vowel
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

    # Resolve remaining possibilities greedily
    def find_eligible(lst, remaining_length) -> list | None:
        eligible = [
            x for x in lst if isinstance(x, list) and len(x) <= remaining_length
        ]
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


def convert_to_numbered_pinyin(word: str, pinyin: str) -> list:
    """Convert pinyin to numbered format with spaces between syllables"""
    words = [w.strip() for w in word.split("/") if w]
    pinyins = [p.strip() for p in pinyin.split("/") if p]
    result = []

    max_chars = max(len(w) for w in words)

    for word, pinyin in zip(words, pinyins, strict=False):
        if len(words) == len(pinyins):
            max_chars = len(word)

        split = _split_pinyin(word, pinyin, max_chars)
        numbered = [
            to_tone3(syl.lower(), neutral_tone_with_five=True)
            for syl in split
            if not syl.isspace()
        ]
        result.append(" ".join(numbered))

    return result


def process_tbcl_words(csv_path: Path, audio_dir: Path, template_path: Path) -> None:
    """Process TBCL words CSV and generate audio files"""
    # Ensure audio directory exists
    audio_dir.mkdir(parents=True, exist_ok=True)

    # Read the CSV file
    df = pd.read_csv(csv_path)

    # Initialize TTS generator
    tts_gen = TTSGenerator(str(template_path), "zh-CN-XiaoxiaoNeural")

    # Add audio column if it doesn't exist
    if "audio" not in df.columns:
        df["audio"] = ""

    # Process each row
    for idx, row in df.iterrows():
        word = row["word"]
        pinyin = row["pinyin"]

        # Convert pinyin to SAPI format for SSML
        numbered = convert_to_numbered_pinyin(word, pinyin)
        # Fancy one-liner to take the first element, and get a proper sapi split as a list
        # `["ge4 ge5", "ge4"]` -> `['ge', '1', 'ge', '5']`
        sapi_list = sum(
            [re.findall(r"[0-9]+|[^0-9]+", x) for x in numbered[0].split()], []
        )
        sapi = " ".join(sapi_list)

        # Generate base filename from word
        base_filename = f"tbcl_{''.join(sapi_list)}"
        audio_path = audio_dir / f"{base_filename}.mp3"

        # Update audio filename whether it exists or not
        df.at[idx, "audio"] = f"{base_filename}.mp3"

        if audio_path.exists():
            print(f"Skipping {base_filename} as it already exists")
        else:
            print(f"{base_filename}: {word} ({sapi})")
            # Generate audio file
            if not tts_gen.generate_audio(sapi, str(audio_path)):
                print(f"Failed to generate audio for {word}")

        # Save CSV after each word is processed
        df.to_csv(csv_path, index=False)


def main():
    load_dotenv()

    if not os.environ.get("AZURE_SPEECH_KEY"):
        print("Error: AZURE_SPEECH_KEY environment variable not set")
        return

    # Define paths
    project_root = Path(__file__).parents[2]
    csv_path = project_root / "res" / "tbcl" / "tbcl_words.csv"
    audio_dir = project_root / "src" / "media" / "audio"
    template_path = project_root / "src" / "scripts" / "tts_template.xml"

    # Process the words
    process_tbcl_words(csv_path, audio_dir, template_path)


if __name__ == "__main__":
    main()
