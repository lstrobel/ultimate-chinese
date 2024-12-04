from pathlib import Path
import pandas as pd
from utils import find_project_root


def trim_audio_names(input_path: Path, output_path: Path) -> None:
    """Trim [sound: prefix and ] suffix from audio column values.

    Args:
        input_path: Path to input CSV file
        output_path: Path where the processed CSV will be written
    """
    # Read the CSV
    df = pd.read_csv(input_path)

    if "hanziaudio" in df.columns:
        # Remove [sound: prefix and ] suffix where values exist
        df["hanziaudio"] = df["hanziaudio"].apply(
            lambda x: x[7:-1] if pd.notna(x) and x.startswith("[sound:") else x
        )

    # Write the processed DataFrame to CSV
    df.to_csv(output_path, index=False)


def main() -> None:
    """Main entry point"""
    root = find_project_root()
    input_path = root / "res" / "tbcl" / "tbcl_words.csv"
    output_path = root / "res" / "tbcl" / "tbcl_words.csv"

    trim_audio_names(input_path, output_path)


if __name__ == "__main__":
    main()
