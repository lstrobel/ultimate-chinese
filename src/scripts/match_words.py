import ast
from pathlib import Path
import pandas as pd
from utils import find_project_root


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

    # Ensure required columns exist
    required_cols = ["traditional", "pinyin", "pos", "meaning", "audio"]
    if not all(col in input_df.columns for col in required_cols):
        raise ValueError(f"Input CSV must contain columns: {required_cols}")

    if "word" not in tbcl_df.columns:
        raise ValueError("TBCL CSV must contain 'word' column")

    # Create a set of TBCL words for faster lookup
    tbcl_words = set()
    for word_list in tbcl_df["word"]:
        # TBCL words may be slash-separated
        words = ast.literal_eval(word_list)
        tbcl_words.update(word for word in words)

    # Create a mapping of words to their audio files
    word_to_audio = dict(zip(input_df["traditional"], input_df["word_audio"]))

    # Create a copy of tbcl_df to modify
    output_df = tbcl_df.copy()

    # Add hanziaudio column if it doesn't exist
    if "hanziaudio" not in output_df.columns:
        output_df["hanziaudio"] = None

    # Update audio information for matching words
    for idx, row in output_df.iterrows():
        words = ast.literal_eval(row["word"])
        for word in words:
            if word in word_to_audio:
                output_df.at[idx, "hanziaudio"] = word_to_audio[word]
                break  # Use the first matching word's audio

    # Write the updated DataFrame to CSV
    output_df.to_csv(output_path, index=False)

    # Print statistics
    matched_count = output_df["hanziaudio"].notna().sum()
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
