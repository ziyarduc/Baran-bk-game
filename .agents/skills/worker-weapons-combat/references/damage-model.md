# Damage Model

## Health System
- HP: 0–100 (no natural regen)
- Shield: 0–100 (persists until damaged)
- Total Effective HP: 200
- Damage priority: Shield absorbs first → remaining hits HP

## Damage Calculation Pipeline
```
1. Base Damage = Weapon.BodyDamage
2. If headshot: Damage *= Weapon.HeadshotMultiplier
3. Apply distance falloff:
   if distance > FalloffStart:
     falloff_ratio = (distance - FalloffStart) / (FalloffFloorDistance - FalloffStart)
     falloff_ratio = Clamp(falloff_ratio, 0, 1)
     Damage *= Lerp(1.0, FalloffFloorMultiplier, falloff_ratio)
4. Apply to target:
   ShieldDamage = Min(Damage, Target.Shield)
   Target.Shield -= ShieldDamage
   RemainingDamage = Damage - ShieldDamage
   Target.HP -= RemainingDamage
5. If Target.HP <= 0: Eliminate
```

## Shotgun Specifics
- 9 pellets, each traces independently
- Each pellet does BodyDamage/9 = ~12.2 HP
- Cone spread: 5° half-angle (ADS), 10° half-angle (hip-fire)
- Headshot multiplier reduced to ×1.5 (vs ×2.0 for other weapons)

## Rocket Launcher Splash
- Direct hit: 120 HP
- Splash uses inverse-linear falloff from impact point
- At 3m: 80 HP, At 5m: 40 HP, Beyond 5m: 0
- Self-damage if shooter within 3m of impact: 60 HP
