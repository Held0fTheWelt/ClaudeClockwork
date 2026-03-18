"""Robust parser for Ollama responses wrapped in markdown.

Handles markdown code blocks and format corruption from Ollama outputs.
"""

import re
from typing import Optional


def extract_python_code(response_text: str) -> str:
    """Extract executable Python code from Ollama markdown response.

    Args:
        response_text: Ollama response that may contain ```python...``` blocks

    Returns:
        Clean Python source code

    Raises:
        ValueError: If no valid Python code found
    """
    code = _extract_code_block(response_text, 'python')
    if not code or not _is_code_like(code):
        raise ValueError("No valid Python code found in Ollama response")
    return code


def extract_bash_code(response_text: str) -> str:
    """Extract executable bash code from Ollama markdown response.

    Args:
        response_text: Ollama response that may contain ```bash...``` blocks

    Returns:
        Clean bash source code

    Raises:
        ValueError: If no valid bash code found
    """
    code = _extract_code_block(response_text, 'bash')
    if not code or not _is_code_like(code):
        raise ValueError("No valid bash code found in Ollama response")
    return code


def _extract_code_block(text: str, language: str) -> str:
    """Extract code block for given language from markdown.

    Handles:
    - ```python...``` markdown blocks
    - Concatenated language prefixes (pythonwith -> with)
    - Stripped newlines (import redef -> import re\ndef)
    - Multiple markdown markers
    """
    # Try to find markdown code block
    patterns = [
        rf'```{language}\n(.*?)\n```',
        rf'```{language}(.*?)```',
        rf'```(.*?)```',
    ]

    code = None
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = match.group(1)
            break

    if not code:
        # Fallback: look for code-like lines
        lines = text.split('\n')
        code_lines = [line for line in lines if _is_code_line(line)]
        if code_lines:
            code = '\n'.join(code_lines)

    if not code:
        return ""

    # Clean up
    code = _fix_corruption(code)
    return code.strip()


def _fix_corruption(code: str) -> str:
    """Fix common Ollama output corruptions."""
    # Remove language prefix if concatenated
    code = re.sub(r'^(python|bash)\s*', '', code)

    # Fix "import redef" -> "import re\ndef"
    code = re.sub(r'(import\s+\w+)(def|class)\s+', r'\1\n\2 ', code)

    # Fix "pythonwith" -> "with", etc.
    code = re.sub(r'\b(python|bash)(with|def|class|import|for|if|try)\b', r'\2', code)

    # Add newlines after closing parens before keywords
    code = re.sub(r'(\))\s+(def|class|import|from|if|for|while|with|try)\s+', r'\1\n\2 ', code)

    # Add newlines after colons for docstrings
    code = re.sub(r'(:\s+)(""")', r'\1\n  \2', code)

    # Normalize multiple spaces to single space
    code = re.sub(r'  +', ' ', code)

    return code


def _is_code_like(text: str) -> bool:
    """Check if text looks like actual code."""
    code_keywords = ('def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ',
                     'try:', 'with ', '#', '#!/')
    return any(keyword in text for keyword in code_keywords) or '=' in text


def _is_code_line(line: str) -> bool:
    """Check if a single line looks like code."""
    stripped = line.strip()
    if not stripped or stripped.startswith('Traceback'):
        return False
    return any(kw in stripped for kw in
               ('def ', 'class ', 'import ', 'return ', '=', '(', ')', '{', '}'))
