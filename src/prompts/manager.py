"""Functions to manage and query system prompts."""

from pathlib import Path


def get_prompts_dir() -> Path:
    """Get the system prompts directory path."""
    return Path(__file__).parent.parent.parent / "system_prompts"


def list_prompts() -> list[str]:
    """
    List all available system prompt names.
    
    Returns:
        List of prompt names (without .txt extension)
    """
    prompts_dir = get_prompts_dir()
    
    if not prompts_dir.exists():
        return []
    
    return sorted([f.stem for f in prompts_dir.glob("*.txt")])


def prompt_exists(prompt_name: str) -> bool:
    """
    Check if a prompt exists.
    
    Args:
        prompt_name: Full name of the prompt (e.g., 'assistant-prompt-v2')
        
    Returns:
        True if the prompt exists, False otherwise
    """
    prompts_dir = get_prompts_dir()
    
    if not prompts_dir.exists():
        return False
    
    return (prompts_dir / f"{prompt_name}.txt").exists()
