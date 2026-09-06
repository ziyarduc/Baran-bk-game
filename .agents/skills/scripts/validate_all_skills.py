#!/usr/bin/env python3
"""
Comprehensive validator for Bakırköy BR skills ecosystem.
Validates YAML frontmatters, required fields, UTF-8 encoding without BOM,
all 7 Core Constraints, MVP directives, and guards against formatting quirks,
syntax breaks, and semantic negations across all skills in .agents/skills/.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1] # .agents/skills
EXCLUDED_DIRS = {"assets", "scripts"}

REQUIRED_FRONTMATTER_KEYS = ("name", "description")

CORE_CONSTRAINT_PATTERNS = {
    "1. No Interior Spaces": [r"(?i)no interior", r"(?i)exterior-only"],
    "2. Solo BR Only": [r"(?i)solo br only", r"(?i)solo mode only"],
    "3. Server-Authoritative": [r"(?i)server-authoritative", r"(?i)dedicated server"],
    "4. 3rd Person Camera": [r"(?i)3rd person camera", r"(?i)over-the-shoulder"],
    "5. 3 Build Materials": [r"(?i)3 build materials", r"(?i)moloz"],
    "6. Hybrid Hit Detection": [r"(?i)hybrid hit detection", r"(?i)hit-scan"],
    "7. Mandatory BR Prefix": [r"(?i)br prefix", r"(?i)prefixed with `?br`?"],
}

MVP_DIRECTIVE_PATTERNS = {
    "MVP 1: 10 Bots Scenario": [r"(?i)10 bots", r"(?i)10-bot"],
    "MVP 2: 2 Weapon Prototypes": [r"(?i)2 weapon prototypes", r"(?i)assault rifle.*rocket launcher", r"(?i)hit-scan.*rocket launcher"],
    "MVP 3: Dual GameModes": [r"(?i)dual gamemodes", r"(?i)free-for-all.*battle royale", r"(?i)ffa.*classic br"],
    "MVP 4: Building System Paused": [r"(?i)building (system )?paused", r"(?i)paused for demo 1"],
}

SEMANTIC_NEGATION_PATTERNS = [
    (r"(?i)\b(?:it is (?:false|not true)|we reject|do not enforce|bypass|ignore)\s+.*?\b(?:no interior|exterior-only)", "Negation of No Interior constraint"),
    (r"(?i)\b(?:it is (?:false|not true)|we reject|do not enforce|bypass|ignore)\s+.*?\bsolo\b", "Negation of Solo BR constraint"),
    (r"(?i)\b(?:interiors? (?:are|is) allowed|allow(?:ing)? interiors?|indoor gameplay enabled)\b", "Interiors allowed violation"),
    (r"(?i)\b(?:squad|duo)\s+(?:and\s+duo\s+)?(?:logic\s+is\s+enabled|is\s+enabled|are\s+enabled|allowed|supported)\b", "Squad/Duo enabled violation"),
    (r"(?i)\b(?:we reject solo|squads are enabled|duos are enabled)\b", "Squads enabled violation"),
    (r"(?i)\b(?:dbno|revive)\s+(?:is\s+enabled|are\s+enabled|allowed|supported)\b", "DBNO/Revive enabled violation"),
    (r"(?i)\b(?:4|four)\s+build\s+materials\b", "4 build materials violation"),
    (r"(?i)\bclient-authoritative\b", "Client-authoritative architecture violation"),
    (r"(?i)\b(?:1st|first)\s+person\s+(?:only|mode\s+only|perspective\s+only)\b", "First person only camera violation"),
]

def has_utf8_bom(raw: bytes) -> bool:
    return raw.startswith(b"\xef\xbb\xbf")

def normalize_frontmatter_block(block: str) -> str:
    """
    Handle formatting quirks in skill frontmatters such as multiline unquoted description
    scalars containing unquoted colons or symbols, while preserving YAML mapping structure.
    """
    lines = block.splitlines()
    norm_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^([a-zA-Z0-9_-]+):\s*(.*)$", line)
        if m and not (line.startswith(" ") or line.startswith("\t")):
            key = m.group(1)
            val = m.group(2)
            if key == "description":
                desc_lines = []
                if val.strip():
                    desc_lines.append(val.strip())
                j = i + 1
                while j < len(lines):
                    if lines[j].strip() and not (lines[j].startswith(" ") or lines[j].startswith("\t")):
                        if re.match(r"^[a-zA-Z0-9_-]+:\s*", lines[j]):
                            break
                    if lines[j].strip():
                        desc_lines.append(lines[j].strip())
                    j += 1
                
                joined_desc = " ".join(desc_lines)
                escaped_desc = yaml.dump({key: joined_desc}, default_flow_style=False).strip()
                norm_lines.append(escaped_desc)
                i = j
                continue
        norm_lines.append(line)
        i += 1
    return "\n".join(norm_lines)

def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str, list[str]]:
    parse_errors: list[str] = []
    text_norm = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text_norm.startswith("---\n"):
        return None, text_norm, ["invalid or missing YAML frontmatter delimiters (missing opening '---')"]
    end = text_norm.find("\n---\n", 4)
    if end < 0:
        return None, text_norm, ["invalid or missing YAML frontmatter delimiters (missing closing '---')"]
    block = text_norm[4:end]
    body = text_norm[end + 5:]

    # Check for syntax breaks like unclosed brackets or braces
    for idx, line in enumerate(block.splitlines()):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        open_brackets = stripped.count("[") - stripped.count("]")
        open_braces = stripped.count("{") - stripped.count("}")
        if open_brackets > 0 or open_braces > 0:
            parse_errors.append(f"unclosed bracket/brace syntax on frontmatter line {idx + 1}: '{stripped}'")

    norm_block = normalize_frontmatter_block(block)
    try:
        data = yaml.safe_load(norm_block)
        if not isinstance(data, dict):
            parse_errors.append(f"YAML frontmatter root must be a mapping/dict, got {type(data).__name__}")
            return None, body, parse_errors
    except yaml.YAMLError as exc:
        parse_errors.append(f"YAML syntax error: {exc}")
        return None, body, parse_errors

    if parse_errors:
        return None, body, parse_errors

    str_data: dict[str, str] = {}
    for k, v in data.items():
        if isinstance(v, str):
            str_data[k] = v
        elif isinstance(v, (int, float, bool)):
            str_data[k] = str(v)
        else:
            str_data[k] = str(v)

    return str_data, body, []

def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"{skill_dir.name}: missing SKILL.md"]

    raw = skill_md.read_bytes()
    if has_utf8_bom(raw):
        errors.append(f"{skill_dir.name}: UTF-8 BOM detected")

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [f"{skill_dir.name}: UTF-8 decode error: {exc}"]

    fm, body, fm_errors = parse_frontmatter(text)
    if fm_errors:
        errors.extend([f"{skill_dir.name}: {e}" for e in fm_errors])

    if fm is not None:
        # Check required frontmatter keys
        for key in REQUIRED_FRONTMATTER_KEYS:
            val = fm.get(key, "").strip()
            if not val:
                errors.append(f"{skill_dir.name}: missing or empty frontmatter key '{key}'")

        # Name matching
        expected_name = skill_dir.name
        actual_name = fm.get("name", "").strip().strip("'\"")
        if actual_name != expected_name:
            errors.append(f"{skill_dir.name}: name mismatch (expected '{expected_name}', got '{actual_name}')")

        # Description quality check (must be at least 20 characters)
        desc = fm.get("description", "").strip()
        if len(desc) < 20:
            errors.append(f"{skill_dir.name}: description too short ({len(desc)} chars, expected >= 20)")

    # Check Bakırköy BR Core Constraints section
    if "Bakırköy BR Core Constraints" not in text and "Bakirkoy BR Core Constraints" not in text:
        errors.append(f"{skill_dir.name}: missing 'Bakırköy BR Core Constraints' section")

    # Verify each of the 7 core constraints
    for constraint_name, patterns in CORE_CONSTRAINT_PATTERNS.items():
        found = any(re.search(pat, text) for pat in patterns)
        if not found:
            errors.append(f"{skill_dir.name}: missing reference to constraint '{constraint_name}'")

    # Verify MVP directives
    for directive_name, patterns in MVP_DIRECTIVE_PATTERNS.items():
        found = any(re.search(pat, text) for pat in patterns)
        if not found:
            errors.append(f"{skill_dir.name}: missing reference to directive '{directive_name}'")

    # Check for semantic negations / contradictions
    for pat, desc in SEMANTIC_NEGATION_PATTERNS:
        m = re.search(pat, text)
        if m:
            errors.append(f"{skill_dir.name}: semantic negation / contradiction detected: '{m.group(0)}' ({desc})")

    return errors

def main() -> int:
    skill_dirs = sorted([d for d in ROOT.iterdir() if d.is_dir() and d.name not in EXCLUDED_DIRS])
    if not skill_dirs:
        print("ERROR: No skill directories found in", ROOT)
        return 2

    total_skills = len(skill_dirs)
    print(f"================================================================================")
    print(f" Bakırköy BR Skills Validator — Auditing {total_skills} Skills")
    print(f"================================================================================")

    all_errors: dict[str, list[str]] = {}
    passed_count = 0

    origin_counts = {"UnrealXu": 0, "kevinpbuckley": 0, "Bakırköy BR Agents": 0}

    for skill_dir in skill_dirs:
        if skill_dir.name.startswith("ue5-"):
            origin_counts["UnrealXu"] += 1
        elif skill_dir.name.startswith("worker-") or skill_dir.name in ("orchestrator", "qa-reviewer", "integrator"):
            origin_counts["Bakırköy BR Agents"] += 1
        else:
            origin_counts["kevinpbuckley"] += 1

        errs = validate_skill(skill_dir)
        if errs:
            all_errors[skill_dir.name] = errs
        else:
            passed_count += 1

    print(f"\nSkills Breakdown by Origin:")
    for orig, count in origin_counts.items():
        print(f"  • {orig}: {count} skills")

    print(f"\nVerification Results:")
    print(f"  • Total skills checked: {total_skills}")
    print(f"  • Passed with 100% compliance: {passed_count}")
    print(f"  • Failed: {len(all_errors)}")

    if all_errors:
        print(f"\n[FAIL] Found {len(all_errors)} skills with issues:")
        for skill_name, issues in all_errors.items():
            print(f"\n  [{skill_name}]:")
            for issue in issues:
                print(f"    - {issue}")
        return 1

    print(f"\n[SUCCESS] 100% COMPLIANCE VERIFIED!")
    print(f"  - All {total_skills} skills have valid YAML frontmatter without BOM.")
    print(f"  - All {total_skills} skills match their directory name.")
    print(f"  - All {total_skills} skills have complete descriptions.")
    print(f"  - All {total_skills} skills enforce the 7 Core Constraints.")
    print(f"  - All {total_skills} skills enforce the 4 Demo 1 MVP Directives.")
    print(f"================================================================================\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
