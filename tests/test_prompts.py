import pytest
from pathlib import Path


class TestLoadPrompt:
    def test_loads_existing_prompt(self, tmp_path):
        from src.prompts.loader import load_prompt, get_prompts_dir
        from unittest.mock import patch

        # Create a test prompt file
        prompt_content = "You are a helpful assistant."
        prompt_file = tmp_path / "test-prompt-v1.txt"
        prompt_file.write_text(prompt_content)

        with patch.object(
            __import__("src.prompts.loader", fromlist=["get_prompts_dir"]),
            "get_prompts_dir",
            return_value=tmp_path,
        ):
            from importlib import reload
            import src.prompts.loader as loader_module

            reload(loader_module)

            # Need to patch at module level
            original_func = loader_module.get_prompts_dir
            loader_module.get_prompts_dir = lambda: tmp_path

            try:
                result = loader_module.load_prompt("test-prompt-v1")
                assert result == prompt_content
            finally:
                loader_module.get_prompts_dir = original_func

    def test_raises_for_nonexistent_prompt(self, tmp_path):
        from src.prompts import loader as loader_module

        original_func = loader_module.get_prompts_dir
        loader_module.get_prompts_dir = lambda: tmp_path

        try:
            with pytest.raises(FileNotFoundError):
                loader_module.load_prompt("nonexistent-prompt")
        finally:
            loader_module.get_prompts_dir = original_func

    def test_strips_whitespace(self, tmp_path):
        from src.prompts import loader as loader_module

        prompt_file = tmp_path / "whitespace-test.txt"
        prompt_file.write_text("  content with whitespace  \n\n")

        original_func = loader_module.get_prompts_dir
        loader_module.get_prompts_dir = lambda: tmp_path

        try:
            result = loader_module.load_prompt("whitespace-test")
            assert result == "content with whitespace"
        finally:
            loader_module.get_prompts_dir = original_func


class TestPromptExists:
    def test_returns_true_for_existing_prompt(self, tmp_path):
        from src.prompts import manager as manager_module

        prompt_file = tmp_path / "existing-prompt.txt"
        prompt_file.write_text("content")

        original_func = manager_module.get_prompts_dir
        manager_module.get_prompts_dir = lambda: tmp_path

        try:
            result = manager_module.prompt_exists("existing-prompt")
            assert result is True
        finally:
            manager_module.get_prompts_dir = original_func

    def test_returns_false_for_nonexistent_prompt(self, tmp_path):
        from src.prompts import manager as manager_module

        original_func = manager_module.get_prompts_dir
        manager_module.get_prompts_dir = lambda: tmp_path

        try:
            result = manager_module.prompt_exists("nonexistent")
            assert result is False
        finally:
            manager_module.get_prompts_dir = original_func

    def test_returns_false_when_directory_missing(self, tmp_path):
        from src.prompts import manager as manager_module

        nonexistent_dir = tmp_path / "nonexistent"

        original_func = manager_module.get_prompts_dir
        manager_module.get_prompts_dir = lambda: nonexistent_dir

        try:
            result = manager_module.prompt_exists("any-prompt")
            assert result is False
        finally:
            manager_module.get_prompts_dir = original_func


class TestListPrompts:
    def test_returns_prompt_names(self, tmp_path):
        from src.prompts import manager as manager_module

        (tmp_path / "prompt-a.txt").write_text("a")
        (tmp_path / "prompt-b.txt").write_text("b")
        (tmp_path / "prompt-c.txt").write_text("c")

        original_func = manager_module.get_prompts_dir
        manager_module.get_prompts_dir = lambda: tmp_path

        try:
            result = manager_module.list_prompts()
            assert "prompt-a" in result
            assert "prompt-b" in result
            assert "prompt-c" in result
        finally:
            manager_module.get_prompts_dir = original_func

    def test_returns_sorted_list(self, tmp_path):
        from src.prompts import manager as manager_module

        (tmp_path / "z-prompt.txt").write_text("z")
        (tmp_path / "a-prompt.txt").write_text("a")
        (tmp_path / "m-prompt.txt").write_text("m")

        original_func = manager_module.get_prompts_dir
        manager_module.get_prompts_dir = lambda: tmp_path

        try:
            result = manager_module.list_prompts()
            assert result == sorted(result)
        finally:
            manager_module.get_prompts_dir = original_func

    def test_returns_empty_list_when_no_prompts(self, tmp_path):
        from src.prompts import manager as manager_module

        original_func = manager_module.get_prompts_dir
        manager_module.get_prompts_dir = lambda: tmp_path

        try:
            result = manager_module.list_prompts()
            assert result == []
        finally:
            manager_module.get_prompts_dir = original_func

    def test_returns_empty_list_when_directory_missing(self, tmp_path):
        from src.prompts import manager as manager_module

        nonexistent_dir = tmp_path / "nonexistent"

        original_func = manager_module.get_prompts_dir
        manager_module.get_prompts_dir = lambda: nonexistent_dir

        try:
            result = manager_module.list_prompts()
            assert result == []
        finally:
            manager_module.get_prompts_dir = original_func
