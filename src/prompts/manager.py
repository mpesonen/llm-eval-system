"""Functions to manage and query system prompts."""

import glob
import re
from pathlib import Path
from typing import Optional


def get_prompts_dir() -> Path:
    """Get the system prompts directory path."""
    return Path(__file__).parent.parent.parent / "system_prompts"


def list_prompts() -> list[str]:
    """
    List all available system prompt names.
    
    Returns:
        List of prompt names (without version suffixes)
    """
    prompts_dir = get_prompts_dir()
    
    if not prompts_dir.exists():
        return []
    
    prompt_names = set()
    pattern = re.compile(r"^(.+)-v(\d+)\.txt$")
    
    for file_path in prompts_dir.glob("*.txt"):
        match = pattern.match(file_path.name)
        if match:
            prompt_names.add(match.group(1))
    
    return sorted(prompt_names)


def list_versions(prompt_name: str) -> list[str]:
    """
    List all available versions for a prompt.
    
    Args:
        prompt_name: Name of the prompt
        
    Returns:
        List of version strings (e.g., ['v1', 'v2', 'v3'])
    """
    prompts_dir = get_prompts_dir()
    
    if not prompts_dir.exists():
        return []
    
    pattern = re.compile(rf"^{re.escape(prompt_name)}-v(\d+)\.txt$")
    versions = []
    
    # Escape prompt_name for glob pattern to handle special characters
    escaped_prompt_name = glob.escape(prompt_name)
    for file_path in prompts_dir.glob(f"{escaped_prompt_name}-v*.txt"):
        match = pattern.match(file_path.name)
        if match:
            version_num = int(match.group(1))
            versions.append(f"v{version_num}")
    
    # Sort versions numerically
    versions.sort(key=lambda v: int(v[1:]))
    return versions


def prompt_exists(prompt_name: str, version: Optional[str] = None) -> bool:
    """
    Check if a prompt (and optionally a specific version) exists.
    
    Args:
        prompt_name: Name of the prompt
        version: Optional version string. If None, checks if any version exists.
        
    Returns:
        True if the prompt exists, False otherwise
    """
    prompts_dir = get_prompts_dir()
    
    if not prompts_dir.exists():
        return False
    
    if version:
        filename = f"{prompt_name}-{version}.txt"
        return (prompts_dir / filename).exists()
    else:
        return len(list_versions(prompt_name)) > 0


def get_latest_version(prompt_name: str) -> str:
    """
    Get the latest version string for a prompt.
    
    Args:
        prompt_name: Name of the prompt
        
    Returns:
        The latest version string (e.g., 'v3')
        
    Raises:
        ValueError: If no versions exist for the prompt
    """
    versions = list_versions(prompt_name)
    
    if not versions:
        raise ValueError(f"No versions found for system prompt: {prompt_name}")
    
    return versions[-1]  # Already sorted, last is latest

