import re
import os
from pathlib import Path

def clean_python_code(content: str) -> str:
    """Strips comments, docstrings, and redundant whitespaces from Python code."""
    # Remove multi-line string docstrings (triple quotes)
    content = re.sub(r'"""[\s\S]*?"""', '', content)
    content = re.sub(r"'''[\s\S]*?'''", '', content)
    
    clean_lines = []
    for line in content.splitlines():
        # Remove comments
        line_clean = re.sub(r'#.*$', '', line).rstrip()
        if line_clean:
            clean_lines.append(line_clean)
    return "\n".join(clean_lines)

def clean_js_ts_code(content: str) -> str:
    """Strips comments and redundant whitespaces from Javascript/TypeScript code."""
    # Remove block comments
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    
    clean_lines = []
    for line in content.splitlines():
        # Remove single-line comments
        line_clean = re.sub(r'//.*$', '', line).rstrip()
        if line_clean:
            clean_lines.append(line_clean)
    return "\n".join(clean_lines)

def extract_structural_metadata(file_path: Path, max_kb: int = 15) -> str:
    """
    Reads a file up to max_kb, cleans comments/whitespaces, 
    and extracts class and function signatures.
    """
    suffix = file_path.suffix.lower()
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(max_kb * 1024)
            
        if suffix == ".py":
            clean_content = clean_python_code(content)
            # Find signatures
            signatures = []
            for line in clean_content.splitlines():
                if line.strip().startswith(("def ", "class ", "async def ")):
                    signatures.append(line)
            return "\n".join(signatures) if signatures else "[No class/function definitions found]"
            
        elif suffix in (".js", ".ts", ".jsx", ".tsx"):
            clean_content = clean_js_ts_code(content)
            signatures = []
            for line in clean_content.splitlines():
                stripped = line.strip()
                if stripped.startswith(("class ", "function ", "export class ", "export function ", "const ", "let ")) and ("(" in stripped or "class" in stripped):
                    signatures.append(line)
            return "\n".join(signatures) if signatures else "[No class/function/variable definitions found]"
            
        else:
            # Fallback: Just return a trimmed version of the content with comments removed
            if suffix in (".json", ".toml", ".yaml", ".yml"):
                return content[:2000] # Standard config files
            
            clean_lines = []
            for line in content.splitlines():
                if not line.strip().startswith(("#", "//", "/*", "*")):
                    clean_lines.append(line)
            return "\n".join(clean_lines[:100]) # First 100 non-comment lines
            
    except Exception as e:
        return f"Error analyzing file structure: {str(e)}"
