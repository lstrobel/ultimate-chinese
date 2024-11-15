from pathlib import Path
import ast
import pandas as pd
import re


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
        # Create HTML ordered list
        items = "\n".join(f"<li>{m}</li>" for m in meanings)
        return f"<ol>\n{items}\n</ol>"
    except (ValueError, SyntaxError):
        return meaning  # Return original if parsing fails


def build_tbcl_words(input: Path, output_dir: Path) -> None:
    """Build TBCL word data files in the specified directory

    Args:
        input: Path to the input CSV file
        output_dir: Directory where the generated files will be written
    """
    # Read the input CSV
    df = pd.read_csv(input)

    # Add empty 'guid' column
    df["guid"] = ""

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
