from pathlib import Path

import yaml


def load_suite(path: str) -> dict:
    """Load a YAML eval suite from disk."""
    content = Path(path).read_text()
    return yaml.safe_load(content)
