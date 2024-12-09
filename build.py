import shutil
import subprocess
from pathlib import Path

from src.data import tbcl


def main() -> None:
    # Create build directory structure
    build_dir = Path("build")
    output_dir = build_dir / "data"

    # Clear existing data directory if it exists
    if output_dir.exists():
        shutil.rmtree(output_dir)

    # Create fresh directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate data files
    tbcl_words = Path("res/tbcl/tbcl_words.csv")
    tbcl.build_tbcl_words(tbcl_words, output_dir)

    # Run brainbrew
    subprocess.run(["brainbrew", "run", "recipes/source_to_anki.yaml"])


if __name__ == "__main__":
    main()
