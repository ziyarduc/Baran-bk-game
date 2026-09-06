#!/usr/bin/env python3
"""Audit all skills in .agents/skills/"""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] # .agents/skills
SKILLS_DIR = ROOT

skill_dirs = sorted([d for d in SKILLS_DIR.iterdir() if d.is_dir() and d.name not in ("assets", "scripts")])
print(f"Total candidate skill directories: {len(skill_dirs)}")

results = []
for sd in skill_dirs:
    skill_md = sd / "SKILL.md"
    has_md = skill_md.exists()
    raw = skill_md.read_bytes() if has_md else b""
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8", errors="replace")
    
    # Parse YAML frontmatter
    fm = None
    fm_name = None
    fm_desc = None
    fm_cat = None
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            for line in fm_text.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k == "name":
                        fm_name = v
                    elif k == "description":
                        fm_desc = v
                    elif k == "category":
                        fm_cat = v

    # Check constraints mentions
    has_constraints = "Bakırköy BR Core Constraints" in text or "Core Constraints" in text
    
    # Check upstream origin
    origin = "unknown"
    if sd.name.startswith("ue5-"):
        origin = "UnrealXu/UnrealEngine5-Skills"
    elif sd.name.startswith("worker-") or sd.name in ("orchestrator", "qa-reviewer", "integrator"):
        origin = "BakirkoyBR-Agents"
    else:
        origin = "kevinpbuckley/unreal-engine-skills"

    results.append({
        "dir": sd.name,
        "origin": origin,
        "has_md": has_md,
        "has_bom": has_bom,
        "fm_name": fm_name,
        "name_match": (fm_name == sd.name),
        "desc_len": len(fm_desc) if fm_desc else 0,
        "has_constraints": has_constraints,
        "size_bytes": len(raw),
        "lines": len(text.splitlines())
    })

print(f"Audited {len(results)} skills.")
missing_md = [r["dir"] for r in results if not r["has_md"]]
name_mismatch = [r["dir"] for r in results if not r["name_match"]]
bom = [r["dir"] for r in results if r["has_bom"]]
no_desc = [r["dir"] for r in results if r["desc_len"] == 0]
with_constraints = [r["dir"] for r in results if r["has_constraints"]]

print(f"Missing SKILL.md: {len(missing_md)}")
print(f"Name mismatch: {len(name_mismatch)}")
print(f"Has BOM: {len(bom)}")
print(f"Missing description: {len(no_desc)}")
print(f"Already has constraints: {len(with_constraints)}")

by_origin = {}
for r in results:
    by_origin.setdefault(r["origin"], []).append(r["dir"])

for orig, lst in by_origin.items():
    print(f"  {orig}: {len(lst)} skills")
