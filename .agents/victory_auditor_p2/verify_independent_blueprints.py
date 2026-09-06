import os
import re

cpp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Source/BakirkoyBR'))
if not os.path.exists(cpp_dir):
    cpp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../BakirkoyBR/Source/BakirkoyBR'))

print(f"[AUDIT] Verifying C++ source ground truth in: {cpp_dir}")
assert os.path.exists(cpp_dir), f"C++ directory not found: {cpp_dir}"

headers = {}
for root, _, files in os.walk(cpp_dir):
    for f in files:
        if f.endswith('.h') or f.endswith('.cpp'):
            full_path = os.path.join(root, f)
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as fp:
                headers[f] = fp.read()

print(f"  [+] Found {len(headers)} C++ header/source files.")

# 1. Verify GameMode properties
br_gm_header = headers.get('BRGameMode_BattleRoyale.h', '')
assert 'RequiredBotCount' in br_gm_header, "RequiredBotCount not found in BRGameMode_BattleRoyale.h"
assert 'BotPawnClass' in br_gm_header, "BotPawnClass not found in BRGameMode_BattleRoyale.h"
assert 'StormCircleClass' in br_gm_header, "StormCircleClass not found in BRGameMode_BattleRoyale.h"
print("  [PASS] BRGameMode_BattleRoyale C++ properties verified.")

ffa_gm_header = headers.get('BRGameMode_FFA.h', '')
assert 'ScoreLimit' in ffa_gm_header, "ScoreLimit not found in BRGameMode_FFA.h"
assert 'MatchTimeLimit' in ffa_gm_header, "MatchTimeLimit not found in BRGameMode_FFA.h"
assert 'RespawnDelay' in ffa_gm_header, "RespawnDelay not found in BRGameMode_FFA.h"
assert 'RequiredBotCount' in ffa_gm_header, "RequiredBotCount not found in BRGameMode_FFA.h"
print("  [PASS] BRGameMode_FFA C++ properties verified.")

hud_header = headers.get('BRHUD.h', '')
assert 'MainHUDClass' in hud_header or 'MainHUDWidget' in hud_header, "MainHUDClass not found in BRHUD.h"
print("  [PASS] BRHUD C++ properties verified.")

# 2. Verify AI Controller loot tags
ai_ctrl_cpp = headers.get('BRAIController.cpp', '')
assert '"Loot"' in ai_ctrl_cpp and '"WeaponPickup"' in ai_ctrl_cpp, "Tags 'Loot' and 'WeaponPickup' not in BRAIController.cpp"
print("  [PASS] BRAIController loot search tags ('Loot', 'WeaponPickup') verified in C++.")

# 3. Verify Weapons classes
assert 'BRWeapon_HitScan.h' in headers, "BRWeapon_HitScan.h missing"
assert 'BRWeapon_Projectile.h' in headers, "BRWeapon_Projectile.h missing"
assert 'BRProjectileRocket.h' in headers, "BRProjectileRocket.h missing"
print("  [PASS] Weapon and Projectile C++ headers verified.")

print("[ALL BLUEPRINT TO C++ GROUND TRUTH CHECKS PASSED]")
