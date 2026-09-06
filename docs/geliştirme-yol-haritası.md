# Geliştirme Yol Haritası — Bakırköy: Son Çember

## Milestone 1: Temel Altyapı (Mevcut Faz)
- [x] Sistem Tasarım Dokümanı (STD) v1.0
- [x] Agent takım yapısı ve skill tanımları
- [x] UE5 proje iskeleti
- [x] Proje kuralları ve kodlama standartları

## Milestone 2: Core Systems
- [ ] GameMode / GameState / PlayerState implementasyonu
- [ ] Karakter hareketi (3rd Person, Sprint, Crouch, Jump)
- [ ] Sağlık sistemi (HP + Shield modeli)
- [ ] Temel ağ replikasyonu

## Milestone 3: Silah Sistemi
- [ ] WeaponBase sınıfı ve silah değiştirme
- [ ] Hit-Scan silahlar (SMG, AR, Sniper, Shotgun)
- [ ] Projectile silahlar (Rocket Launcher)
- [ ] Hasar modeli ve damage falloff
- [ ] ADS, spray pattern, reload mekaniği

## Milestone 4: İnşa Sistemi
- [ ] 3 malzeme toplama mekaniği
- [ ] Duvar / Rampa / Zemin / Yarım Duvar dikme
- [ ] Build preview (ghost mesh)
- [ ] Yapı edit sistemi
- [ ] Yapı yıkılma ve HP sistemi

## Milestone 5: Oyun Döngüsü
- [ ] Daralan çember (Storm Circle) sistemi
- [ ] Akıllı çember algoritması (Bakırköy sokaklarına uyarlama)
- [ ] Loot spawn ve tier sistemi
- [ ] Skydiving mekaniği (paraşüt + rüzgâr)
- [ ] Maç fazları (Lobby → Skydive → Active → PostGame)

## Milestone 6: Bot AI
- [ ] FSM durum makinesi (6 durum)
- [ ] Algı sistemi (görsel + işitsel)
- [ ] NavMesh pathfinding (A* uyarlaması)
- [ ] RVO2 crowd avoidance
- [ ] Agent rolleri (Assault, Sniper, Support)
- [ ] AI Skills (Flanking, HighGround, Suppression)
- [ ] Zorluk seviyeleri (Easy → Elite)

## Milestone 7: Ağ ve Sunucu
- [ ] Server-authoritative mimari
- [ ] Hit validation (Server Rewind)
- [ ] Client prediction ve interpolation
- [ ] Anti-cheat temel kontrolleri

## Milestone 8: Harita
- [ ] Bakırköy blockout (graybox)
- [ ] POI yerleşimi (15+ nokta)
- [ ] NavMesh oluşturma (sokak + çatı katmanları)
- [ ] Cover node yerleşimi
- [ ] Destructible objeler

## Milestone 9: Polish & Test
- [ ] HUD / UI
- [ ] Ses efektleri ve müzik
- [ ] Performans optimizasyonu
- [ ] 100 oyuncu stres testi
- [ ] Bug fixing
