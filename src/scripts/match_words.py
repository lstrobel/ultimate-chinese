import ast
import os
from pathlib import Path
import re
import pandas as pd
from utils import find_project_root
import shutil


def match_words(input_path: Path, tbcl_path: Path, output_path: Path) -> None:
    """Match words from input CSV against TBCL words and create a new CSV with matches.

    Args:
        input_path: Path to input CSV with traditional, pinyin, pos, meaning, audio columns
        tbcl_path: Path to TBCL words CSV
        output_path: Path where the matched CSV will be written
    """
    # Read the CSVs
    input_df = pd.read_csv(input_path)
    tbcl_df = pd.read_csv(tbcl_path)

    # Create pinyin to audio mapping, handling multiple pinyin variants separated by '/'
    pinyin_to_audio = {}
    for pinyin, audio in zip(input_df["pinyin"], input_df["audio"]):
        if pd.isna(pinyin) or pd.isna(audio):
            continue
        if "/" in pinyin:
            # Split pinyin variants and map each to the same audio
            variants = [p.strip() for p in pinyin.split("/")]
            for variant in variants:
                pinyin_to_audio[
                    re.sub(r"\s", lambda m: "", variant.strip().lower())
                    .replace("'", "")
                    .replace("-", "")
                ] = audio
        else:
            pinyin_to_audio[
                re.sub(r"\s", lambda m: "", pinyin.strip().lower())
                .replace("'", "")
                .replace("-", "")
            ] = audio

    print(pinyin_to_audio)

    # Create a copy of tbcl_df to modify
    output_df = tbcl_df.copy()

    # Add hanziaudio column if it doesn't exist
    # if "word_audio" not in output_df.columns:
    output_df["word_audio"] = None

    root = find_project_root()
    source_path = root / "build" / "zz.dangdai" / "media"

    # Update audio information for matching words
    for idx, row in output_df.iterrows():
        pinyin_options = ast.literal_eval(row["pinyin"])
        for pinyin in pinyin_options:
            normalized = (
                re.sub(r"\s", lambda m: "", pinyin.strip().lower())
                .replace("'", "")
                .replace("-", "")
            )
            # Try exact match first
            if normalized in pinyin_to_audio:
                mp3_name = pinyin_to_audio[normalized][7:-1]
                new_name = normalized + ".mp3"
                shutil.copy(
                    os.path.join(source_path, mp3_name),
                    os.path.join(root, "src", "media", "audio", new_name),
                )

                output_df.at[idx, "word_audio"] = new_name
                break  # Use the first matching word's audio

    # Write the updated DataFrame to CSV
    output_df.to_csv(output_path, index=False)

    # Print statistics
    matched_count = output_df["word_audio"].notna().sum()
    print(f"Total input words: {len(input_df)}")
    print(f"TBCL entries with audio: {matched_count}")


def main() -> None:
    """Main entry point"""
    root = find_project_root()
    tbcl_path = root / "res" / "tbcl" / "tbcl_words.csv"

    # These paths should be adjusted based on your actual file locations
    input_path = root / "src" / "data" / "dangdai.csv"
    output_path = root / "res" / "tbcl" / "tbcl_words_with_audio.csv"

    match_words(input_path, tbcl_path, output_path)


if __name__ == "__main__":
    main()
