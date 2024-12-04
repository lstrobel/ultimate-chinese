from pathlib import Path
import pandas as pd
from utils import find_project_root


def split_fields(input_path: Path, output_path: Path) -> None:
    """Split word, zhuyin and pinyin fields into lists in the TBCL CSV.

    Args:
        input_path: Path to the input CSV file
        output_path: Path where the processed CSV will be written
    """
    # Read the CSV
    df = pd.read_csv(input_path)

    # Split fields on '/' and strip whitespace from each element
    for field in ["word", "zhuyin", "pinyin"]:
        if field in df.columns:
            df[field] = df[field].apply(
                lambda x: [item.strip() for item in str(x).split("/")]
                if pd.notna(x)
                else []
            )

    # Write the processed DataFrame back to CSV
    df.to_csv(output_path, index=False)


def main() -> None:
    """Main entry point"""
    root = find_project_root()
    input_path = root / "res" / "tbcl" / "tbcl_words.csv"
    output_path = root / "res" / "tbcl" / "tbcl_words_split.csv"

    split_fields(input_path, output_path)


if __name__ == "__main__":
    main()
