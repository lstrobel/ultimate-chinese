"""Functions for working with CC-CEDICT dictionary entries."""

from functools import lru_cache
from typing import NamedTuple

from utils import find_project_root


class DictEntry(NamedTuple):
    """A parsed dictionary entry."""

    traditional: str
    simplified: str
    pinyin: str
    definitions: list[str]


def _parse_cedict_line(line: str) -> tuple[str, str, str, list] | None:
    """Parse a CC-CEDICT format line into components.

    Format: traditional simplified [pinyin] /def 1/def 2/def n/
    Example: 傲慢 傲慢 [ao4 man4] /arrogant/haughty/
    """
    if not line or line.startswith("#"):
        return None

    # Split into characters and definition parts
    chars_pinyin, raw_defs = line.split("/", 1)

    # Split characters part into components
    parts = chars_pinyin.split("[")
    chars = parts[0].strip()
    pinyin = parts[1].strip(" ]")

    # Split characters into traditional and simplified
    trad, simp = chars.split(" ")

    # Join definitions with semicolons
    defs = [d for d in raw_defs.strip("/").split("/") if d]

    return trad, simp, pinyin, defs


@lru_cache(maxsize=1)
def _load_dictionary() -> dict[str, list[DictEntry]]:
    """Load the CC-CEDICT dictionary file into a dictionary.

    Returns:
        Dictionary mapping (traditional) characters to their entries
    """
    char_dict: dict[str, list[DictEntry]] = {}

    with open(
        find_project_root() / "res" / "cedict" / "cedict_ts.u8",
        encoding="utf-8",
    ) as f:
        for line in f:
            parsed = _parse_cedict_line(line.strip())
            if parsed:
                entry = DictEntry(*parsed)
                # Add entry under traditional form
                char_dict.setdefault(entry.traditional, []).append(entry)

    return char_dict


def search_dict(query: str) -> list[DictEntry]:
    """Search dictionary entries for matches."""
    char_dict = _load_dictionary()
    return char_dict.get(query, [])


def format_entry(entry: DictEntry) -> str:
    """Format a dictionary entry for display."""
    defs = "; ".join(entry.definitions)
    return f"{entry.traditional} {entry.simplified} [{entry.pinyin}] - {defs}"
