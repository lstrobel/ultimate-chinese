import argparse
import json

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

    with open(args.file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Formatted JSON data in {args.file}")
