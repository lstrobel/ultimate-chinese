from pathlib import Path
import pandas as pd
import hashlib
import argparse


def generate_guid(word: str, pinyin: str) -> str:
    """Generate a deterministic GUID from word and pinyin."""
    # Combine word and pinyin, encode to bytes
    combined = f"{word}:{pinyin}".encode("utf-8")
    # Create SHA-256 hash and take first 32 chars
    return hashlib.sha256(combined).hexdigest()[:32]


def add_guids_to_csv(input_path: Path, output_path: Path) -> None:
    """Add GUIDs to CSV file based on word and pinyin columns."""
    # Read the input CSV
    df = pd.read_csv(input_path)

    # Generate GUIDs
    df["guid"] = df.apply(lambda row: generate_guid(row["word"], row["pinyin"]), axis=1)

    # Write processed data to output CSV
    df.to_csv(output_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Add GUIDs to TBCL word CSV file")
    parser.add_argument("input", type=Path, help="Input CSV file path")
    parser.add_argument("output", type=Path, help="Output CSV file path")

    args = parser.parse_args()
    add_guids_to_csv(args.input, args.output)


if __name__ == "__main__":
    main()
