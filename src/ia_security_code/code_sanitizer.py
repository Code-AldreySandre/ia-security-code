import ast
import re

_CODE_BLOCK_PATTERN = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_python_code(raw_text: str) -> str:
    """Extracts clean Python code from LLM markdown responses."""
    if not raw_text:
        return ""
    match = _CODE_BLOCK_PATTERN.search(raw_text)
    if match:
        return match.group(1).strip()
    return raw_text.strip()


def is_valid_syntax(code: str) -> bool:
    """Validates whether a Python snippet parses cleanly without syntax errors."""
    if not code or not code.strip():
        return False
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False