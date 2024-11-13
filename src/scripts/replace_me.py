import argparse
import pandas as pd
import pyperclip
from pathlib import Path


def replace_definitions(csv_path: Path) -> None:
    """Replace definitions marked with REPLACE_ME in a CSV file."""
    # Read the CSV file
    df = pd.read_csv(csv_path)

    # Find rows containing REPLACE_ME in definition
    mask = df["definition"].str.contains("REPLACE_ME", na=False)
    rows_to_update = df[mask]

    if len(rows_to_update) == 0:
        print("No definitions found containing 'REPLACE_ME'")
        return

    # Process each row needing updates
    for idx in rows_to_update.index:
        row = df.loc[idx]
        print("\nCurrent row:")
        for col in df.columns:
            print(f"{col}: {row[col]}")

        # Copy word to clipboard
        pyperclip.copy(row["word"])
        print("\nCopied word to clipboard!")

        # Get new definition from user
        print(
            "\nEnter definitions separated by forward slashes (or 'q'/'quit' to save and exit):"
        )
        new_def = input().strip()

        if new_def.lower() in ["q", "quit"]:
            # Save changes before quitting
            df.to_csv(csv_path, index=False)
            print("\nSaving changes and exiting...")
            return

        # Split on forward slashes and convert to list representation
        definitions = [d.strip() for d in new_def.split("/")]
        # Update the definition as a string representation of the list
        df.at[idx, "definition"] = str(definitions)

    # Save the updated CSV after all changes
    df.to_csv(csv_path, index=False)
    print("\nAll definitions updated and saved!")


def main():
    parser = argparse.ArgumentParser(
        description="Replace REPLACE_ME definitions in a CSV file"
    )
    parser.add_argument("csv_path", type=Path, help="Path to the CSV file")

    args = parser.parse_args()

    if not args.csv_path.exists():
        print(f"Error: File {args.csv_path} does not exist")
        return

    replace_definitions(args.csv_path)


if __name__ == "__main__":
    main()
