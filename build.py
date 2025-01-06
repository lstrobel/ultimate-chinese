import argparse
import subprocess
from pathlib import Path

from src import tbcl


def main(debug: bool = False) -> None:
    output_dir = Path("res/generated")

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
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    main(debug=args.debug)
