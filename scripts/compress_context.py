"""
Context Compression Utility for Bakirkoy BR Agents.
Extracts essential sections, strips markdown fluff, and compresses logs for token efficiency.
"""

import sys
import re
import argparse

def compress_markdown(content: str) -> str:
    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    # Collapse multiple blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    # Strip trailing whitespace on lines
    lines = [line.rstrip() for line in content.splitlines()]
    return '\n'.join(lines)

def extract_log_errors(content: str, max_lines: int = 25) -> str:
    lines = content.splitlines()
    error_patterns = [r'error', r'fail', r'fatal', r'exception', r'warning', r'rejected', r'request_changes']
    matched_lines = []
    
    for idx, line in enumerate(lines):
        if any(re.search(pat, line, re.IGNORECASE) for pat in error_patterns):
            matched_lines.append(f"L{idx+1}: {line.strip()}")
            if len(matched_lines) >= max_lines:
                matched_lines.append(f"... [Truncated: reached max {max_lines} error lines]")
                break
                
    if not matched_lines:
        return f"[LOG SUMMARY] 0 errors or warnings detected across {len(lines)} lines."
    return "\n".join(matched_lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compress files or logs for token optimization.")
    parser.add_argument("mode", choices=["markdown", "log"], help="Compression mode")
    parser.add_argument("file_path", help="Target file path")
    args = parser.parse_args()

    try:
        with open(args.file_path, "r", encoding="utf-8", errors="ignore") as f:
            raw = f.read()
            
        if args.mode == "markdown":
            compressed = compress_markdown(raw)
            print(f"[COMPRESSION] Reduced from {len(raw)} to {len(compressed)} characters ({(1 - len(compressed)/len(raw))*100:.1f}% reduction).")
            print(compressed[:500] + "...")
        elif args.mode == "log":
            print(extract_log_errors(raw))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
