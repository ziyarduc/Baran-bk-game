# Bakırköy: Son Çember — 3D Battle Royale

100 oyunculu, 3. şahıs (3rd Person) Battle Royale oyunu. Harita: Bakırköy, İstanbul.

## Teknoloji
- **Motor:** Unreal Engine 5 (Nanite + Lumen)
- **Geliştirme:** Gemini AI Agent Orkestrasyon Sistemi
- **Modeller:** gemini-3.1-pro-preview (Şef) + gemini-3.8-flash (High Thinking - Tüm İşçiler)

## Proje Yapısı
- `.agents/` — AI Agent skill tanımları ve proje kuralları
- `BakirkoyBR/` — Unreal Engine 5 C++ projesi
- `docs/` — Tasarım dokümanları (Türkçe)

## Agent Takımı
| # | Agent | Rol | Model |
|---|-------|-----|-------|
| 0 | Orchestrator | Şef / Conductor | pro |
| 1 | MapWorld Worker | Harita & Dünya | flash |
| 2 | WeaponsCombat Worker | Silah & Savaş | flash |
| 3 | AIAgents Worker | Bot AI | flash |
| 4 | GameLoop Worker | Oyun Döngüsü | flash_lite |
| 5 | Building Worker | İnşa Sistemi | flash_lite |
| 6 | QA Reviewer | Kalite Kontrol | flash |
| 7 | Integrator | Entegrasyon | flash |

## Temel Kısıtlar
- Bina içi mekanlar (interior) yok — sadece dış mekan
- Solo BR modu (ilk prototip)
- Server-authoritative mimari
- Hybrid hit detection (Hit-Scan + Projectile)
