import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

PROJECT_ROOT = r'C:\Users\silver\Desktop\bakirkoy-br'
VERIFY_SCRIPT = os.path.join(PROJECT_ROOT, 'scripts', 'verify-rules.ps1')

print("=" * 70)
print("Bakirkoy BR — Independent Victory Auditor Forensic Mutation Suite")
print("=" * 70)

def setup_mock_project(tmpdir):
    rules_dir = os.path.join(tmpdir, '.agents', 'rules')
    src_dir = os.path.join(tmpdir, 'BakirkoyBR', 'Source', 'BakirkoyBR')
    os.makedirs(rules_dir, exist_ok=True)
    os.makedirs(src_dir, exist_ok=True)

    for item in os.listdir(os.path.join(PROJECT_ROOT, '.agents', 'rules')):
        shutil.copy(os.path.join(PROJECT_ROOT, '.agents', 'rules', item), rules_dir)
    shutil.copy(os.path.join(PROJECT_ROOT, '.agents', 'AGENTS.md'), os.path.join(tmpdir, '.agents', 'AGENTS.md'))
    return src_dir

# -------------------------------------------------------------
# Test 1: Raw Pointer Mutation (AActor* BadActor = nullptr;)
# -------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmpdir:
    src = setup_mock_project(tmpdir)
    with open(os.path.join(src, 'TestMutation.h'), 'w', encoding='utf-8') as f:
        f.write('#pragma once\n#include "CoreMinimal.h"\n#include "TestMutation.generated.h"\n\nUCLASS()\nclass ATestMutation : public AActor\n{\n    GENERATED_BODY()\n    UPROPERTY()\n    AActor* BadActor = nullptr;\n};\n')
    
    res = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', VERIFY_SCRIPT, '-ProjectRoot', tmpdir], capture_output=True, text=True)
    print(f"Test 1 [Raw Pointer]: Return Code = {res.returncode}")
    assert res.returncode == 1, f"Expected 1, got {res.returncode}"
    assert "No Raw UObject Pointer (TObjectPtr Enforced)" in res.stdout, "Rule C failed to trigger"
    print("  -> PASSED: Raw pointer violation caught correctly.")

# -------------------------------------------------------------
# Test 2: STL in .cpp Mutation (std::vector<int> V;)
# -------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmpdir:
    src = setup_mock_project(tmpdir)
    with open(os.path.join(src, 'TestMutation.h'), 'w', encoding='utf-8') as f:
        f.write('#pragma once\n#include "CoreMinimal.h"\n#include "TestMutation.generated.h"\nUCLASS()\nclass ATestMutation : public AActor { GENERATED_BODY() };\n')
    with open(os.path.join(src, 'TestMutation.cpp'), 'w', encoding='utf-8') as f:
        f.write('#include "TestMutation.h"\n#include <vector>\nstd::vector<int> V;\n')
    
    res = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', VERIFY_SCRIPT, '-ProjectRoot', tmpdir], capture_output=True, text=True)
    print(f"Test 2 [STL in .cpp]: Return Code = {res.returncode}")
    assert res.returncode == 1, f"Expected 1, got {res.returncode}"
    assert "No Standard Library STL in Source" in res.stdout, "Check 4.8 failed to trigger"
    print("  -> PASSED: STL in .cpp caught correctly.")

# -------------------------------------------------------------
# Test 3: Turkish 4th Material Mutation (Ahsap / Ahşap)
# -------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmpdir:
    src = setup_mock_project(tmpdir)
    with open(os.path.join(src, 'TestMaterial.h'), 'w', encoding='utf-8') as f:
        f.write('#pragma once\n#include "CoreMinimal.h"\n#include "TestMaterial.generated.h"\nenum class EBRMaterialType : uint8 { Moloz, Tugla, Celik, Ahsap };\n')
    
    res = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', VERIFY_SCRIPT, '-ProjectRoot', tmpdir], capture_output=True, text=True)
    print(f"Test 3 [Turkish Material]: Return Code = {res.returncode}")
    assert res.returncode == 1, f"Expected 1, got {res.returncode}"
    assert "No Forbidden 4th Material in Header" in res.stdout, "Check 4.6 failed to trigger"
    print("  -> PASSED: Turkish 4th material caught correctly.")

# -------------------------------------------------------------
# Test 4: Squad / DBNO Logic Mutation (bIsDownButNotOut)
# -------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmpdir:
    src = setup_mock_project(tmpdir)
    with open(os.path.join(src, 'TestSquad.h'), 'w', encoding='utf-8') as f:
        f.write('#pragma once\n#include "CoreMinimal.h"\n#include "TestSquad.generated.h"\nUCLASS()\nclass ATestSquad : public AActor { GENERATED_BODY() UPROPERTY() bool bIsDownButNotOut = false; };\n')
    
    res = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', VERIFY_SCRIPT, '-ProjectRoot', tmpdir], capture_output=True, text=True)
    print(f"Test 4 [Squad/DBNO Logic]: Return Code = {res.returncode}")
    assert res.returncode == 1, f"Expected 1, got {res.returncode}"
    assert "No Forbidden Squad/Duo/DBNO Logic in Header" in res.stdout, "Check 4.7 failed to trigger"
    print("  -> PASSED: Forbidden Squad/DBNO logic caught correctly.")

# -------------------------------------------------------------
# Test 5: Angle Bracket Include Ordering Mutation (<...generated.h>)
# -------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmpdir:
    src = setup_mock_project(tmpdir)
    with open(os.path.join(src, 'TestInclude.h'), 'w', encoding='utf-8') as f:
        f.write('#pragma once\n#include <TestInclude.generated.h>\n#include "SomeOtherInclude.h"\n')
    
    res = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', VERIFY_SCRIPT, '-ProjectRoot', tmpdir], capture_output=True, text=True)
    print(f"Test 5 [Include Order]: Return Code = {res.returncode}")
    assert res.returncode == 1, f"Expected 1, got {res.returncode}"
    assert "Generated Header Is Last Include" in res.stdout, "Check 4.2 failed to trigger"
    print("  -> PASSED: Angle bracket include order caught correctly.")

# -------------------------------------------------------------
# Test 6: Skills Validator Semantic Negation & Corrupt YAML
# -------------------------------------------------------------
sys.path.insert(0, os.path.join(PROJECT_ROOT, '.agents', 'skills', 'scripts'))
from validate_all_skills import validate_skill

with tempfile.TemporaryDirectory() as tmpdir:
    skill_dir = Path(tmpdir) / 'test-skill'
    skill_dir.mkdir()
    
    # 6a: Corrupt YAML
    (skill_dir / 'SKILL.md').write_text('''---
name: test-skill
description: Valid description for test-skill.
corrupt: [malformed {{{{ syntax
---
## Bakırköy BR Core Constraints
- 1. No Interior Spaces
- 2. Solo BR Only
- 3. Server-Authoritative
- 4. 3rd Person Camera
- 5. 3 Build Materials
- 6. Hybrid Hit Detection
- 7. Mandatory BR Prefix
## Playable Demo MVP Directives
- MVP 1: 10 bots
- MVP 2: 2 weapon prototypes
- MVP 3: Dual gamemodes
- MVP 4: Building paused
''', encoding='utf-8')
    errs = validate_skill(skill_dir)
    print(f"Test 6a [Corrupt YAML]: Errors caught = {len(errs)}")
    assert any("YAML syntax error" in e or "unclosed bracket" in e for e in errs), "Corrupt YAML was not caught"
    print("  -> PASSED: Corrupt YAML syntax rejected.")

    # 6b: Semantic Negation ("interiors are allowed")
    (skill_dir / 'SKILL.md').write_text('''---
name: test-skill
description: Valid description for test-skill.
---
## Bakırköy BR Core Constraints
- 1. Interiors are allowed
- 2. Solo BR Only
- 3. Server-Authoritative
- 4. 3rd Person Camera
- 5. 3 Build Materials
- 6. Hybrid Hit Detection
- 7. Mandatory BR Prefix
## Playable Demo MVP Directives
- MVP 1: 10 bots
- MVP 2: 2 weapon prototypes
- MVP 3: Dual gamemodes
- MVP 4: Building paused
''', encoding='utf-8')
    errs = validate_skill(skill_dir)
    print(f"Test 6b [Semantic Negation]: Errors caught = {len(errs)}")
    assert any("Interiors allowed violation" in e for e in errs), "Semantic negation was not caught"
    print("  -> PASSED: Semantic negation rejected.")

print("=" * 70)
print("ALL 7 INDEPENDENT FORENSIC MUTATION TESTS PASSED WITH ZERO CIRCUMVENTION")
print("=" * 70)
