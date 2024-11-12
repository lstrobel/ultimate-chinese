#!/usr/bin/env python3
"""
Script to convert TBCL wordlist CSV to our format.
Reads from res/tbcl/TBCL_wordlist_2023-05-17.csv
Writes to src/data/tbcl_words.csv
"""

import csv
import os
import re
from pathlib import Path
import pandas as pd


def find_project_root() -> Path:
    """Find the project root by looking for pyproject.toml or .git"""
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    raise RuntimeError("Unable to find project root")


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
