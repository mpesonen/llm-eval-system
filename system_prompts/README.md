# System Prompts

This directory contains versioned system prompts used in LLM evaluation runs.

## File Naming Convention

System prompts are named using the format: `{prompt-name}-v{version}.txt`

Examples:
- `example-v1.txt`
- `assistant-v1.txt`
- `assistant-v2.txt`

## Versioning

- Use simple sequential versioning: v1, v2, v3, etc.
- The latest version is automatically determined as the highest numbered version.
- When creating a new version, increment the version number.

## Adding New System Prompts

1. Create a new file in this directory following the naming convention: `{name}-v1.txt`
2. Write your system prompt content in the file
3. The prompt will be automatically available for use in evaluation runs

## Adding New Versions

1. Copy the previous version file
2. Rename it with the next version number (e.g., `assistant-v2.txt`)
3. Modify the content as needed
4. The new version will be automatically detected

## Usage

Specify a system prompt when running evaluations:

```bash
python main.py --suite datasets/examples/basic.yaml --system-prompt example --system-prompt-version v1
```

Or use the latest version automatically:

```bash
python main.py --suite datasets/examples/basic.yaml --system-prompt example
```

## Querying Available Prompts

You can use the Python API to query available prompts:

```python
from src.prompts import list_prompts, list_versions, get_latest_version

# List all prompt names
prompts = list_prompts()  # ['example', 'assistant', ...]

# List versions for a prompt
versions = list_versions('example')  # ['v1', 'v2', ...]

# Get latest version
latest = get_latest_version('example')  # 'v2'
```

