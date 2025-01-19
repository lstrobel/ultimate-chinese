import argparse
import subprocess
from pathlib import Path

from src import words


def main(debug: bool = False) -> None:
    res_dir = Path("res")
    output_dir = res_dir / "generated"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate notes.csv
    words.build_notes(res_dir, output_dir)

    # Generate css
    subprocess.run(
        [
            "sass",
            "--no-source-map",
            "src/note_models/style.scss",
            str(output_dir) + "/style.css",
        ]
    )

    # Run brainbrew
    subprocess.run(["brainbrew", "run", "recipes/source_to_anki.yaml"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    # Debug currently unused
    main(debug=args.debug)
