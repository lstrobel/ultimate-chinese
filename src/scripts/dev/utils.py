from pathlib import Path


def find_project_root() -> Path:
    """Find the project root by looking for pyproject.toml or .git"""
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    raise RuntimeError("Unable to find project root")
