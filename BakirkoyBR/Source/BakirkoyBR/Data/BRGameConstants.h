#pragma once

namespace BRConstants
{
    // ── Players ──
    constexpr int32 MAX_PLAYERS = 100;
    constexpr float DEFAULT_HEALTH = 100.f;
    constexpr float DEFAULT_SHIELD = 0.f;
    constexpr float MAX_HEALTH = 100.f;
    constexpr float MAX_SHIELD = 100.f;

    // ── Skydiving ──
    constexpr float FREEFALL_MAX_VERTICAL_SPEED = 60.f;   // m/s
    constexpr float FREEFALL_MAX_HORIZONTAL_SPEED = 25.f;  // m/s
    constexpr float GLIDE_VERTICAL_SPEED = 8.f;
    constexpr float GLIDE_HORIZONTAL_SPEED = 15.f;
    constexpr float PARACHUTE_AUTO_DEPLOY_HEIGHT = 10000.f; // 100m in UE units (cm)
    constexpr float QUICK_DROP_MIN_HEIGHT = 3000.f;         // 30m
    constexpr float LANDING_ANIMATION_TIME = 0.5f;
    constexpr float SPAWN_PROTECTION_TIME = 3.f;
    constexpr float WIND_BONUS_MULTIPLIER = 1.15f;
    constexpr float WIND_PENALTY_MULTIPLIER = 0.9f;

    // ── Building ──
    constexpr float BUILD_MODE_TOGGLE_TIME = 0.2f;
    constexpr float BUILD_TO_WEAPON_SWAP_TIME = 0.3f;
    constexpr float TURBO_BUILD_REDUCTION = 0.1f;
    constexpr float EDIT_ANIMATION_TIME = 0.4f;
    constexpr int32 WALL_COST = 10;
    constexpr int32 RAMP_COST = 10;
    constexpr int32 FLOOR_COST = 10;
    constexpr int32 HALFWALL_COST = 5;
    constexpr float BUILD_PIECE_SIZE = 300.f; // 3m in UE units (cm)

    // ── Server ──
    constexpr int32 SERVER_TICK_RATE = 60;
    constexpr float MAX_REWIND_TIME = 0.2f;          // 200ms
    constexpr float REWIND_SNAPSHOT_INTERVAL = 0.015f; // 15ms
    constexpr float REWIND_BUFFER_DURATION = 0.3f;     // 300ms

    // ── AI ──
    constexpr float AI_TICK_INTERVAL = 0.2f;           // 5 Hz
    constexpr float AI_VISUAL_FOV = 120.f;
    constexpr float AI_VISUAL_RANGE_OPEN = 8000.f;     // 80m
    constexpr float AI_VISUAL_RANGE_NARROW = 4000.f;   // 40m
    constexpr float AI_AGENT_RADIUS = 60.f;            // 0.6m
    constexpr float NARROW_STREET_THRESHOLD = 300.f;   // 3m

    // ── Combat ──
    constexpr float SHOTGUN_BUILD_DAMAGE_MULTIPLIER = 2.5f;  // 250%
    constexpr float ROCKET_SELF_DAMAGE = 60.f;
    constexpr float ROCKET_SELF_DAMAGE_RADIUS = 300.f; // 3m
}
