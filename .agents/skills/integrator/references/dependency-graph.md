# Module Dependency Graph

## Visual Representation
```
                    ┌──────────┐
                    │   Data   │ ← No dependencies (leaf node)
                    └────┬─────┘
                         │
                    ┌────┴─────┐
                    │   Core   │ ← Depends on: Data
                    └────┬─────┘
                         │
                    ┌────┴──────┐
                    │ Character │ ← Depends on: Core, Data
                    └────┬──────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
        ┌─────┴────┐ ┌──┴───┐ ┌───┴──────┐
        │ Weapons  │ │  AI  │ │ Building │
        └──────────┘ └──────┘ └──────────┘
         ← Char,Data  ← ALL   ← Char,Data
                         │
                    ┌────┴─────┐
                    │ GameLoop │ ← Depends on: Core, Char, Weapons, Building, AI, Data
                    └────┬─────┘
                         │
                    ┌────┴─────┐
                    │ Network  │ ← Depends on: Core, GameLoop, Char, Data
                    └──────────┘
```

## Dependency Matrix

|  | Data | Core | Character | Weapons | AI | Building | GameLoop | Network |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Data** | — | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Core** | ✓ | — | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Character** | ✓ | ✓ | — | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Weapons** | ✓ | ✗ | ✓ | — | ✗ | ✗ | ✗ | ✗ |
| **AI** | ✓ | ✗ | ✓ | ✓ | — | ✓ | ✗ | ✗ |
| **Building** | ✓ | ✗ | ✓ | ✗ | ✗ | — | ✗ | ✗ |
| **GameLoop** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✗ |
| **Network** | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | — |

✓ = Can include headers from | ✗ = Must NOT include headers from
