import subprocess

from src.data.tbcl_words import useful


def main() -> None:
    useful()
    subprocess.run(["brainbrew", "run", "recipes/source_to_anki.yaml"])


if __name__ == "__main__":
    main()
