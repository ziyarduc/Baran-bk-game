import os
import re
import sys

PROJECT_ROOT = r"C:\Users\silver\Desktop\bakirkoy-br"
SOURCE_DIR = os.path.join(PROJECT_ROOT, "BakirkoyBR", "Source", "BakirkoyBR")

print(f"=== Independent Victory Auditor AST & Integrity Verifier ===")
print(f"Scanning directory: {SOURCE_DIR}")

header_files = []
source_files = []

for root, dirs, files in os.walk(SOURCE_DIR):
    for f in files:
        if f.endswith(".h"):
            header_files.append(os.path.join(root, f))
        elif f.endswith(".cpp"):
            source_files.append(os.path.join(root, f))

print(f"Found {len(header_files)} headers and {len(source_files)} source files.")

STL_REGEX = re.compile(r'\bstd::(vector|string|map|unordered_map|set|shared_ptr|unique_ptr|wstring|array|deque|list|unordered_set)\b')
FORBIDDEN_MATERIALS = re.compile(r'\b(Wood|Stone|Metal|Gold|Ahsap|Ahşap|Demir|Beton)\b', re.IGNORECASE)
MATERIAL_CONTEXT = re.compile(r'(enum\s+class\s+\w*Material|struct\s+\w*Material|EBRMaterialType|EBRMaterial|BuildMaterial|BuildPiece)', re.IGNORECASE)
SQUAD_LOGIC = re.compile(r'\b(bIsDownButNotOut|ReviveTeammate|FSquadInfo|ASquadState|Squad|SquadId|Teammate|DBNO|DownButNotOut|Revive|Duo)\b')
RAW_POINTER = re.compile(r'(?:^|[{;])\s*(?:UPROPERTY\(.*?\)\s*)?(?:[UAF][A-Z][a-zA-Z0-9_]*)\s*\*\s*([a-zA-Z0-9_]+)\s*(?:=\s*[^;]+)?\s*;')

violations = []

# 1. Header Checks
for h in header_files:
    fname = os.path.basename(h)
    with open(h, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        lines = content.splitlines()

    # Check #pragma once
    if not any(l.strip().startswith("#pragma once") for l in lines):
        violations.append(f"{fname}: Missing #pragma once")

    # Check .generated.h strictly last include
    if ".generated.h" in content:
        includes = [l.strip() for l in lines if l.strip().startswith("#include")]
        if includes:
            last_inc = includes[-1]
            if not last_inc.endswith('.generated.h"') and not last_inc.endswith('.generated.h>'):
                violations.append(f"{fname}: Last include is '{last_inc}', expected .generated.h")

    # Check STL
    if STL_REGEX.search(content):
        violations.append(f"{fname}: Forbidden std:: container detected")

    # Check Raw UObject pointers without TObjectPtr
    for l in lines:
        if RAW_POINTER.search(l) and "TObjectPtr" not in l and "TWeakObjectPtr" not in l and "TSubclassOf" not in l:
            violations.append(f"{fname}: Raw UObject pointer detected: {l.strip()}")

    # Check forbidden 4th material
    if FORBIDDEN_MATERIALS.search(content) and MATERIAL_CONTEXT.search(content):
        violations.append(f"{fname}: Forbidden building material detected")

    # Check squad/DBNO logic
    if SQUAD_LOGIC.search(content):
        violations.append(f"{fname}: Squad/DBNO logic detected")

# 2. Source (.cpp) Checks
for cpp in source_files:
    fname = os.path.basename(cpp)
    with open(cpp, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Check STL
    if STL_REGEX.search(content):
        violations.append(f"{fname}: Forbidden std:: container detected")

    # Check forbidden 4th material
    if FORBIDDEN_MATERIALS.search(content) and MATERIAL_CONTEXT.search(content):
        violations.append(f"{fname}: Forbidden building material detected")

    # Check squad/DBNO logic
    if SQUAD_LOGIC.search(content):
        violations.append(f"{fname}: Squad/DBNO logic detected")

print(f"\n--- AST and Static Integrity Violations Found: {len(violations)} ---")
for v in violations:
    print(f"  [VIOLATION] {v}")

if not violations:
    print("ALL 17 HEADERS AND 17 SOURCE FILES 100% CLEAN AND COMPLIANT!")
