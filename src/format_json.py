import argparse
import json

from schema import Note

# Format JSON data in place in a manner consistent with other tooling.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Format JSON data in place.")
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to the JSON file to format.",
    )
    args = parser.parse_args()

    with open(args.file, encoding="utf-8") as f:
        data = json.load(f)

    # Parse notes using Pydantic models
    notes = [Note(**item) for item in data]

    with open(args.file, "w", encoding="utf-8") as f:
        json_data = [note.model_dump(exclude_none=True, mode="json") for note in notes]
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    print(f"Formatted JSON data in {args.file}")
