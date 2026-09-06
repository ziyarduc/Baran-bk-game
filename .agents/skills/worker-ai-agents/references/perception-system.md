# Perception System

## Visual Perception
| Parameter | Value |
|-----------|-------|
| FOV | 120° (front cone) |
| Max Range (open) | 80m |
| Max Range (narrow street) | 40m |
| Recognition Time (open) | 0.3s |
| Recognition Time (cluttered) | 0.6s |
| Stationary Target Penalty | ×2 recognition time |

## Audio Perception
| Sound Source | Detection Radius |
|-------------|------------------|
| Sprint | 25m |
| Gunfire (unsuppressed) | 60m |
| Gunfire (suppressed) | 20m |
| Building | 30m |
| Item Use | 10m |
| Crouch Walk | 8m |

## Threat List
- Each detected target gets a ThreatEntry
- ThreatEntry: TargetID, LastKnownPosition, LastSeenTime, ThreatScore, IsVisible
- ThreatScore = (1/Distance) × (1 + RecentDamageFromTarget/100)
- Primary Target = highest ThreatScore
- Entries expire after 15s without re-detection

## Implementation
- Use UE5 AIPerceptionComponent as base
- Custom sight config with 120° FOV
- Custom hearing config with per-stimulus radius
- ThreatList is a TArray<FBRThreatEntry> on the AIController
- Updated every perception tick (5 Hz)
