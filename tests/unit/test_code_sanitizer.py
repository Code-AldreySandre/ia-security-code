import pytest
from ia_security_code.code_sanitizer import extract_python_code, is_valid_syntax


def test_extract_python_code_from_markdown_block():
    raw_response = (
        "Aqui está a implementação solicitada:\n"
        "```python\n"
        "def login(user, pwd):\n"
        "    return True\n"
        "```\n"
        "Espero que ajude!"
    )
    cleaned = extract_python_code(raw_response)
    assert cleaned == "def login(user, pwd):\n    return True"


def test_extract_python_code_from_generic_code_block():
    raw_response = "```\nx = 10\ny = 20\n```"
    assert extract_python_code(raw_response) == "x = 10\ny = 20"


def test_extract_python_code_without_markdown_fences():
    raw_response = "import os\n\ndef list_dir(path):\n    os.system(f'ls {path}')"
    assert extract_python_code(raw_response) == raw_response


def test_is_valid_syntax_returns_true_for_valid_python():
    code = "def add(a: int, b: int) -> int:\n    return a + b\n"
    assert is_valid_syntax(code) is True


def test_is_valid_syntax_returns_false_for_broken_code():
    broken_code = "def broken_func(\n    return 'missing closing paren'"
    assert is_valid_syntax(broken_code) is False


def test_is_valid_syntax_returns_false_for_empty_code():
    assert is_valid_syntax("   \n  ") is False