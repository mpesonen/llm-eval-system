"""Git utility functions."""

import subprocess


def get_current_commit_hash() -> str | None:
    """
    Get the current git commit hash (short form, 7 characters).
    
    Returns:
        The short commit hash, or None if not in a git repository
        or git is not available.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None
