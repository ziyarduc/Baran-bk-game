#!/usr/bin/env python3
"""Collect metadata from all 66 skills for SKILLS_CATALOG.md generation."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

skills = []
for d in sorted(ROOT.iterdir()):
    if not d.is_dir() or d.name in ("assets", "scripts"):
        continue
    skill_md = d / "SKILL.md"
    if not skill_md.exists():
        continue
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    
    # Extract frontmatter
    fm_lines = []
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm_lines = parts[1].strip().splitlines()
            body = parts[2].strip()
        else:
            body = text
    else:
        body = text
        
    data = {"dir": d.name, "raw_body": body[:500]}
    for line in fm_lines:
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip().strip("'\"")
            data[k] = v
            
    # Classify origin and category
    if d.name.startswith("ue5-"):
        data["origin"] = "UnrealXu/UnrealEngine5-Skills"
        data["category"] = "UnrealXu Architectural & Pipeline"
    elif d.name.startswith("worker-"):
        data["origin"] = "BakirkoyBR-Agents"
        data["category"] = "Bakırköy BR Specialized Workers"
    elif d.name in ("orchestrator", "qa-reviewer", "integrator"):
        data["origin"] = "BakirkoyBR-Agents"
        data["category"] = "Bakırköy BR Team Leads"
    else:
        data["origin"] = "kevinpbuckley/unreal-engine-skills"
        # Subcategorize kevinpbuckley skills
        name = d.name
        if name in ("cpp-fundamentals", "core-types-and-containers", "memory-and-gc", "timers-and-async", "delegates-and-events", "logging-and-assertions"):
            data["category"] = "Core C++ & Memory Architecture"
        elif name in ("coding-standards", "module-and-build-system", "plugins-and-modules", "project-structure", "navigating-engine-source"):
            data["category"] = "Build, Modular Plugins & Standards"
        elif name in ("gameplay-framework", "character-and-movement", "mover-movement-system", "actors-and-components", "gameplay-ability-system", "gameplay-tags", "gameplay-architecture-planning"):
            data["category"] = "Gameplay Framework & Movement"
        elif name in ("enhanced-input",):
            data["category"] = "Input & Control Systems"
        elif name in ("networking-and-replication",):
            data["category"] = "Networking & Replication"
        elif name in ("levels-and-world-partition", "landscape-and-foliage", "asset-management"):
            data["category"] = "World Partition & Open World"
        elif name in ("physics-and-chaos",):
            data["category"] = "Physics & Collision (Chaos)"
        elif name in ("ai-and-navigation",):
            data["category"] = "AI, Perception & Navigation"
        elif name in ("nanite-and-rendering", "materials-and-shaders", "lighting-and-lumen", "meshes-static-and-skeletal"):
            data["category"] = "Rendering, Nanite & Materials"
        elif name in ("animation-system", "control-rig-and-ik", "sequencer-and-cinematics"):
            data["category"] = "Animation, Control Rig & Cinematics"
        elif name in ("niagara-vfx", "audio-and-metasounds"):
            data["category"] = "VFX (Niagara) & Audio (MetaSounds)"
        elif name in ("umg-and-slate",):
            data["category"] = "UI Systems (UMG & Slate)"
        elif name in ("blueprint-fundamentals", "blueprint-cpp-integration"):
            data["category"] = "Blueprint & C++ Interop"
        elif name in ("debugging-techniques", "profiling-and-optimization", "game-thread-performance", "automation-and-testing"):
            data["category"] = "Profiling, Debugging & Automation"
        elif name in ("editor-scripting-and-python", "packaging-and-deployment", "importing-content"):
            data["category"] = "Editor Scripting & Packaging"
        elif name in ("save-and-load", "data-driven-design", "subsystems"):
            data["category"] = "Data Systems & Subsystems"
        else:
            data["category"] = "Core Systems"

    # Check for references dir
    ref_dir = d / "references"
    data["has_references"] = ref_dir.exists()
    if data["has_references"]:
        data["ref_files"] = [f.name for f in ref_dir.glob("*.md")]
    else:
        data["ref_files"] = []

    skills.append(data)

print(f"Parsed {len(skills)} skills.")
cats = {}
for s in skills:
    cats.setdefault(s["category"], []).append(s["dir"])

for c, items in sorted(cats.items()):
    print(f"{c}: {len(items)} skills")

with open(ROOT / "scripts" / "skills_meta.json", "w", encoding="utf-8") as f:
    json.dump(skills, f, indent=2)
print("Saved skills_meta.json")
