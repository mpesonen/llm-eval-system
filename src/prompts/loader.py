"""Functions to load system prompts from files."""

from pathlib import Path


def get_prompts_dir() -> Path:
    """Get the system prompts directory path."""
    # Assuming we're running from project root
    return Path(__file__).parent.parent.parent / "system_prompts"


def load_prompt(prompt_name: str, version: str) -> str:
    """
    Load a system prompt from file.
    
    Args:
        prompt_name: Name of the prompt (e.g., 'example', 'assistant')
        version: Version string (e.g., 'v1', 'v2')
        
    Returns:
        The prompt content as a string
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    prompts_dir = get_prompts_dir()
    filename = f"{prompt_name}-{version}.txt"
    file_path = prompts_dir / filename
    
    if not file_path.exists():
        raise FileNotFoundError(
            f"System prompt file not found: {file_path}"
        )
    
    return file_path.read_text().strip()


def load_latest_prompt(prompt_name: str) -> tuple[str, str]:
    """
    Load the latest version of a system prompt.
    
    Args:
        prompt_name: Name of the prompt
        
    Returns:
        Tuple of (prompt_content, version_string)
        
    Raises:
        FileNotFoundError: If no versions of the prompt exist
        ValueError: If prompt_name is invalid
    """
    from src.prompts.manager import get_latest_version, list_versions
    
    versions = list_versions(prompt_name)
    if not versions:
        raise FileNotFoundError(
            f"No versions found for system prompt: {prompt_name}"
        )
    
    latest_version = get_latest_version(prompt_name)
    content = load_prompt(prompt_name, latest_version)
    
    return content, latest_version

