"""
The script used to generate the first iteration of tbcl_words.csv
Manual corrections were needed after running this script, so it was really only useful once.
"""

import csv
import os
import re

import pandas as pd
from cedict import search_dict
from pypinyin.contrib.tone_convert import to_tone
from utils import find_project_root


def context_to_tag(context: str) -> str:
    """Convert context string to tag format.

    Examples:
        "核心詞" -> "UC::TBCL-context-core"
        "10.餐飲、烹飪" -> "UC::TBCL-context-food"
        etc.
    """
    if pd.isna(context):
        return ""

    context_map = {
        "核心詞": "core",
        "1.個人資料": "personal-info",
        "2.日常起居": "daily-routines",
        "3.職業": "work-career",
        "4.休閒、娛樂": "leisure-entertainment",
        "5.交通、旅遊": "travel-transport",
        "6.社交、人際": "social-relations",
        "7.身體、醫療": "health-medical",
        "8.教育、學習": "education-learning",
        "9.購物、商店": "shopping-retail",
        "10.餐飲、烹飪": "food-dining",
        "11.公共服務": "public-services",
        "12.安全": "safety-security",
        "13.自然環境": "environment-nature",
        "14.社會": "society-community",
        "15.文化": "culture-arts",
        "16.情緒、態度": "emotions-attitudes",
        "17.科技": "tech-digital",
    }
    return f"UC::TBCL-context-{context_map.get(context, '')}"


def category_to_tag(category: str) -> str:
    """Convert category string to tag format.

    Examples:
        "基礎" -> "UC::TBCL-basic"
        "進階" -> "UC::TBCL-intermediate"
        "精熟" -> "UC::TBCL-advanced"
    """
    category_map = {"基礎": "basic", "進階": "intermediate", "精熟": "advanced"}
    return f"UC::TBCL-{category_map.get(category, '')}"


def normalize_pinyin(pinyin: str) -> str:
    """Convert cedict pinyin format to a unicode format.

    Handles each space-separated syllable separately to ensure proper tone conversion.
    Replaces 'u:' with 'v' for proper tone handling.
    """
    words = pinyin.split()
    converted = [to_tone(word.replace("u:", "v")) for word in words]
    return " ".join(converted).strip()


def choose_entry(word: str, entries: list, expected_pinyin: str) -> str:
    """Sometimes there might be multiple dictionary entries for a word that we need the definition of.

    This method will choose one intelligently, and log to console if no choice could be made
    """

    # Fast-fail
    if len(entries) == 1:
        return entries[0].definitions

    matching_entries = [
        entry for entry in entries if normalize_pinyin(entry.pinyin) == expected_pinyin
    ]

    # If exactly one match, use it without prompting
    if len(matching_entries) == 1:
        return matching_entries[0].definitions
    # If some matches found, the user needs to choose between them
    elif matching_entries:
        entries = matching_entries
    else:
        # Last-ditch effort: Someimes CEDICT differs in whether to put spaces between pinyin syllables.
        # Try looking for matching entries by removing spaces.
        no_spaces = [
            entry
            for entry in entries
            if ("".join(normalize_pinyin(entry.pinyin).split())) == expected_pinyin
        ]

        if len(no_spaces) == 1:
            return no_spaces[0].definitions
        elif no_spaces:
            entries = matching_entries

    print(
        f"\nMultiple entries found for '{word}' (expected pinyin: {expected_pinyin}):"
    )
    for i, entry in enumerate(entries, 0):
        print(f"{i}. {entry.traditional} {entry.simplified} [{entry.pinyin}]")
        print(f"   Definitions: {'/ '.join(entry.definitions)}")
    return ["REPLACE_ME"]


def get_definition(word: str, pinyin: str) -> list:
    """Get definition for a word from CC-CEDICT.

    If the word contains forward slashes, only look up the first word.
    If multiple entries are found, try to match pinyin first, then let user choose.
    """
    # Take first word if multiple words are separated by slashes
    first_word = word.split("/")[0].strip()
    first_word = "".join(i for i in first_word if not i.isdigit()).strip()
    first_pinyin = pinyin.split("/")[0].strip()
    entries = search_dict(first_word)
    if not entries:
        print(f"No entry found for word: {word}\n")
        return ["REPLACE_ME"]
    return choose_entry(first_word, entries, first_pinyin)


def level_to_tag(level: str) -> str:
    """Convert level string to tag format.

    Examples:
        "第1級" -> "UC::TBCL-level-1"
        "第2*級" -> "UC::TBCL-level-2-star"
    """
    # Extract the number and check for star
    match = re.match(r"第(\d+)(\*)?級", level)
    if not match:
        return ""

    number, star = match.groups()
    tag = f"UC::TBCL-level-{number}"
    if star:
        tag += "-star"
    return tag


def main():
    # Column name mappings
    header_mapping = {
        "序號": "id",
        "詞語": "word",
        "等別": "category",
        "級別": "level",
        "情境": "context",
        "書面字頻(每百萬字)": "written_freq",
        "口語字頻(每百萬字)": "spoken_freq",
        "參考注音": "zhuyin",
        "參考漢語拼音": "pinyin",
    }

    root_dir = find_project_root()
    input_file = root_dir / "res" / "tbcl" / "TBCL_wordlist_2023-05-17.csv"
    output_dir = root_dir / "src" / "data"
    output_file = output_dir / "tbcl_words.csv"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Read CSV, rename columns, and drop system_id column
    df = pd.read_csv(input_file)
    df = df.rename(columns=header_mapping)
    df = df.drop(columns=["簡編本系統號"])

    # Add definitions column, using pinyin to help match entries
    df["definition"] = df.apply(
        lambda row: get_definition(row["word"], row["pinyin"]), axis=1
    )

    # Create tags column combining level and category tags
    df["tags"] = df.apply(
        lambda row: ", ".join(
            filter(
                None,
                [
                    level_to_tag(row["level"]),
                    category_to_tag(row["category"]),
                    context_to_tag(row["context"]),
                ],
            )
        ),
        axis=1,
    )
    df = df.drop(columns=["level", "category", "context"])

    # Write to output file with proper quoting
    df.to_csv(output_file, index=False, quoting=csv.QUOTE_NONNUMERIC)


if __name__ == "__main__":
    main()
