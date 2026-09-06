# Agent Takım Yapısı — Bakırköy: Son Çember

## Genel Bakış

Bu proje, 8 adet AI agent tarafından orkestrasyonlu şekilde geliştirilmektedir. Her agent, belirli bir sistem modülünden sorumludur ve kendi SKILL.md dosyasındaki talimatlara göre çalışır.

## Takım Hiyerarşisi

```
                    ┌─────────────────┐
                    │  ORCHESTRATOR   │
                    │  (gemini-3.1-pro)│
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────┴────┐         ┌────┴────┐         ┌────┴────┐
   │İŞÇİLER │         │   QA    │         │INTEGRA- │
   │ (5 adet)│         │REVIEWER │         │  TÖR    │
   └────┬────┘         └─────────┘         └─────────┘
        │
   ┌────┼────┬────┬────┐
   │    │    │    │    │
  W1   W2   W3   W4   W5
```

## Agent Detayları

### Orchestrator (Şef)
- **Model:** gemini-3.1-pro-preview
- **Görev:** Görev dağıtımı, bağımlılık yönetimi, kalite kapısı
- **Çalışma Şekli:** Tüm worker agent'lara görev atar, çıktılarını toplar, QA'ya gönderir

### Worker 1 — MapWorld (Harita & Dünya)
- **Model:** gemini-3.8-flash (High Thinking)
- **Modül:** `GameLoop/` (Storm Circle, Loot, SafeZone bölümleri)
- **Sorumluluk:** POI tanımları, çember sistemi, NavMesh konfigürasyonu

### Worker 2 — WeaponsCombat (Silah & Savaş)
- **Model:** gemini-3.8-flash (High Thinking)
- **Modül:** `Weapons/`
- **Sorumluluk:** 5 silah sınıfı, hasar modeli, ekipman sistemi

### Worker 3 — AIAgents (Bot AI)
- **Model:** gemini-3.8-flash (High Thinking)
- **Modül:** `AI/`
- **Sorumluluk:** FSM durum makinesi, 3 agent rolü, AI Skills, algı sistemi

### Worker 4 — GameLoop (Oyun Döngüsü & Backend)
- **Model:** gemini-3.8-flash (High Thinking)
- **Modül:** `Core/`, `Character/`, `Network/`
- **Sorumluluk:** GameMode, GameState, PlayerState, hit validation, skydiving

### Worker 5 — Building (İnşa Sistemi)
- **Model:** gemini-3.8-flash (High Thinking)
- **Modül:** `Building/`
- **Sorumluluk:** 3 malzeme, 4 yapı parçası, edit sistemi, Turbo Build

### QA Reviewer (Kalite Kontrol)
- **Model:** gemini-3.1-pro-preview (High Thinking)
- **Görev:** Her worker çıktısını review eder, bug tespit eder, UE5 best practice kontrolü yapar

### Integrator (Entegrasyon)
- **Model:** gemini-3.1-pro-preview (High Thinking)
- **Görev:** Modüller arası bağımlılıkları test eder, compile kontrolü yapar, entegrasyon haritası günceller

## İş Akışı

1. Orchestrator görev atar (task board üzerinden)
2. Worker agent görevi tamamlar, kodu üretir
3. QA Reviewer kodu inceler, onaylar veya geri gönderir
4. Integrator onaylanan kodu diğer modüllerle test eder
5. Orchestrator sonucu kaydeder, sonraki görevi atar
