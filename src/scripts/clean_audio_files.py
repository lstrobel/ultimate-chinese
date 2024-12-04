from pathlib import Path
import pandas as pd
from utils import find_project_root


def clean_audio_files(csv_path: Path, audio_dir: Path) -> None:
    """Remove audio files that aren't referenced in the TBCL words CSV.

    Args:
        csv_path: Path to TBCL words CSV
        audio_dir: Path to audio files directory
    """
    # Read the CSV
    df = pd.read_csv(csv_path)

    # Get set of referenced audio files
    referenced_files = set()
    if "hanziaudio" in df.columns:
        # Remove [sound:] wrapper if present and filter out None/NaN
        referenced_files = {
            x[7:-1] if x.startswith("[sound:") else x for x in df["hanziaudio"].dropna()
        }

    # Get all audio files in directory
    audio_files = {f.name for f in audio_dir.glob("*") if f.is_file()}

    # Find unreferenced files
    unreferenced = audio_files - referenced_files

    # Remove unreferenced files
    for filename in unreferenced:
        file_path = audio_dir / filename
        file_path.unlink()
        print(f"Removed unreferenced file: {filename}")

    print(f"\nSummary:")
    print(f"Total audio files: {len(audio_files)}")
    print(f"Referenced files: {len(referenced_files)}")
    print(f"Removed files: {len(unreferenced)}")


def main() -> None:
    """Main entry point"""
    root = find_project_root()
    csv_path = root / "res" / "tbcl" / "tbcl_words.csv"
    audio_dir = root / "src" / "media" / "audio"

    if not audio_dir.exists():
        print(f"Audio directory not found: {audio_dir}")
        return

    clean_audio_files(csv_path, audio_dir)


if __name__ == "__main__":
    main()
