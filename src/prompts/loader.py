"""Functions to load system prompts from files."""

from pathlib import Path


def get_prompts_dir() -> Path:
    """Get the system prompts directory path."""
    return Path(__file__).parent.parent.parent / "system_prompts"


def load_prompt(prompt_name: str) -> str:
    """
    Load a system prompt from file.
    
    Args:
        prompt_name: Full name of the prompt (e.g., 'assistant-prompt-v2')
        
    Returns:
        The prompt content as a string
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    prompts_dir = get_prompts_dir()
    file_path = prompts_dir / f"{prompt_name}.txt"
    
    if not file_path.exists():
        raise FileNotFoundError(
            f"System prompt file not found: {file_path}"
        )
    
    return file_path.read_text().strip()
