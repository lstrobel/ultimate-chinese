import argparse
import json
import logging
import os
import subprocess
import zipfile
from pathlib import Path

from src import words
from src.words_pydantic_models import Note

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main(debug: bool = False) -> None:
    res_dir = Path("res")
    output_dir = res_dir / "generated"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate notes.csv from words json
    logger.info("Generating notes.csv from words.json...")

    notes = []
    with open(res_dir / "words.json") as p:
        notes = [Note.model_validate(obj) for obj in json.loads(p.read())]

    formatted_df = words.format_notes(notes)
    output_path = output_dir / "notes.csv"
    formatted_df.to_csv(output_path, index=False)

    logger.info(f"Output written to {output_path}")

    # Generate CSS
    logger.info("Generating CSS from style.scss...")
    subprocess.run(
        [
            "sass",
            "--no-source-map",
            "src/note_models/style.scss",
            str(output_dir / "style.css"),
        ]
    )
    logger.info("CSS generation completed.")

    # Run brainbrew
    logger.info("Running brainbrew...")
    subprocess.run(["brainbrew", "run", "recipes/source_to_anki.yaml"])

    # Zip the output deck for distribution
    logger.info("Packaging build deck...")

    build_dir = Path("build") / "Ultimate_Chinese"
    output_path = Path("build") / "Ultimate_Chinese.zip"

    with zipfile.ZipFile(output_path, "w") as zipf:
        for root, _, files in os.walk(build_dir):
            for file in files:
                file_path = os.path.join(root, file)
                archive_name = os.path.relpath(file_path, build_dir)
                zipf.write(file_path, arcname=archive_name)

    logger.info(f"Zip file created at {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    # Debug currently unused
    main(debug=args.debug)
