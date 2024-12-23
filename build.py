import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path

from src import tbcl


def main(debug: bool = False) -> None:
    # Create build directory structure
    build_dir = Path("build")
    output_dir = build_dir / "intermediate"

    # Create timestamped backup of existing intermediate directory only in debug mode
    if debug and output_dir.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = build_dir / f"backup_{timestamp}"
        os.rename(output_dir, backup_dir)

    # Create fresh directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate data files
    tbcl_words = Path("res/tbcl/tbcl_words.csv")
    tbcl.build_tbcl_words(tbcl_words, output_dir)

    # Generate css
    subprocess.run(
        ["sass", "src/note_models/style.scss", str(output_dir) + "/style.css"]
    )

    # Run brainbrew
    subprocess.run(["brainbrew", "run", "recipes/source_to_anki.yaml"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug", action="store_true", help="Create backup of existing data directory"
    )
    args = parser.parse_args()

    main(debug=args.debug)
