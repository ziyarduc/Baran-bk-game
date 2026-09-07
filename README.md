# Bakirkoy BR — Son Çember (Battle Royale)

> 📍 **1:1 ÖLÇEKLİ GERÇEK BAKIRKÖY, İSTANBUL HARİTASI (1:1 SCALE REPLICA OF BAKIRKOY, ISTANBUL)**
>
> Oyun dünyası, İstanbul Bakırköy ilçesinin OpenStreetMap (OSM) topoğrafik GIS verilerinden **birebir 1:1 ölçekte** (1 Unreal Unit = 1 cm) Unreal Engine 5 koordinat sistemine aktarılmıştır.
> - **Merkez Datum Noktası:** Bakırköy Özgürlük Meydanı (40.98186° N, 28.87428° E, İrtifa: 25m)
> - **Gerçek Şehir Yapısı:** 2900+ gerçek bina ayak izi (Carousel AVM, Capacity AVM, Galleria, Bakırköy Belediyesi, Marmaray İstasyonu) ve 440+ gerçek cadde/sokak (İstanbul Cad., İncirli Cad., Ebuzziya Cad., Fahri Korutürk Cad.).
> - **Taktik Dikey Oynanış:** Binalar tamamen solid dış cephe blokları olarak üretilmiştir; çatılara erişim sağlayan harici yangın merdivenleri/ramplar ve sokak barikatları ile taktiksel dikey çatışma alanları sunar.

---

## Proje Genel Bakış & Teknoloji
- **Oyun Türü:** 100 Oyunculu, 3. Şahıs Taktiksel Battle Royale
- **Oyun Motoru:** Unreal Engine 5.5 (Nanite, Lumen, Chaos Physics)
- **Backend & Ağ:** C++ (Server-Authoritative, UE5 Networking, Sub-tick Hit Registration)
- **Harita & Çevre:** OpenStreetMap (OSM) tabanlı 1:1 ölçekli gerçek Bakırköy haritası
- **Karakterler & Animasyon:** UE5 Manny/Quinn tabanlı prosedürel faceless modeller ve `ABP_BRCharacter` AnimBlueprint lokomosyon/nişan sistemi
- **Silah & Çatışma:** Hibrit Hasar Sistemi (Assault Rifle: Hit-Scan + Rocket Launcher: Fizik tabanlı Projectile ve alan hasarı)
- **Oyun Modları:** Classic Battle Royale (Daralan Gaz/Fırtına Çemberi) ve Free-For-All Deathmatch

---

## 🛠️ Hazır Otomasyon Scriptleri (Automation Scripts)

Projede harita üretiminden paketlemeye kadar tüm süreci otomatikleştiren 6 adet ana üretim scripti bulunmaktadır:

| Script | Tür / Hedef | Açıklama |
|---|---|---|
| `fetch_osm_data.py` | Python 3 (CLI) | Bakırköy GIS verilerini Overpass API üzerinden çeker, WGS84 koordinatlarını UE5 sol-el santimetre sistemine projekte eder (`data/bakirkoy_level_data.json`). Offline fallback seed içerir. |
| `build_osm_level.py` | UE5 Python API / Standalone | İndirilen OSM verisini kullanarak 1:1 ölçekli `/Game/Maps/BakirkoyOSM.umap` haritasını üretir. OBB binalar, çift katmanlı yollar (Spline + Mesh), NavMesh, PlayerStart ve Loot noktaları oluşturur. |
| `setup_character_anims.py` | UE5 Python API / Standalone | Prosedürel faceless materyalleri (`M_BRFacelessPlaceholder`, `MI_BRFacelessManny`) ve lokomosyon/zıplama/nişan destekli `ABP_BRCharacter` AnimBP'sini `BP_BRCharacter` ve `BP_BRAIBotCharacter` aktörlerine bağlar. |
| `generate_map.py` | UE5 Python API / Standalone | 200m x 200m boyutunda taktiksel graybox test arenası (`/Game/Maps/BakirkoyMap.umap`), çevre duvarları, binalar, ramplar, NavMeshBoundsVolume ve 10 PlayerStart üretir. |
| `setup_blueprints.py` | UE5 Python API / Standalone | C++ sınıflarına dayalı tüm temel Blueprint'leri (`BP_BRGameMode`, `BP_BRGameMode_Deathmatch`, `BP_BRCharacter`, `BP_BRAIBotCharacter`, silahlar, HUD ve Kill Feed UI) oluşturup derler. |
| `package_game.ps1` | PowerShell (RunUAT) | Unreal Automation Tool (UAT) ile projeyi derler, cook eder, paketler ve Windows 64-bit `.exe` Release paketi üretir. |

---

## 🚀 Çalıştırma Talimatları (Execution Guide)

Tüm Python scriptleri hem **Unreal Engine 5 içinde** (Headless Commandlet veya Editor Python Console) hem de Unreal Engine kurulu olmayan CI/CD ortamlarında **Standalone / Dry-Run** modunda çalışabilecek şekilde tasarlanmıştır.

### 1. `fetch_osm_data.py` — Bakırköy OSM Verisi İndirme & Projeksiyon
Bakırköy'ün gerçek bina ve yol geometrisini çeker ve normalize eder:

```bash
# Standart çalıştırma (Overpass API üzerinden canlı veri):
python fetch_osm_data.py --mode district --output data/bakirkoy_level_data.json --verbose

# İnternet bağlantısı veya API limiti durumunda gömülü offline Bakırköy seed verisiyle çalıştırma:
python fetch_osm_data.py --offline-seed --output data/bakirkoy_level_data.json

# Yalnızca ilçe merkezi (Özgürlük Meydanı & AVM'ler çevresi) için:
python fetch_osm_data.py --mode center
```

### 2. `build_osm_level.py` — 1:1 Bakırköy Haritasını İnşa Etme
Topolojik verileri UE5 aktörlerine, yollara, binalara ve NavMesh'e dönüştürür:

```bash
# Yöntem A: Unreal Engine Headless Commandlet (Önerilen CLI):
UnrealEditor-Cmd.exe BakirkoyBR.uproject -run=pythonscript -script="build_osm_level.py"

# Yöntem B: UE5 Editörü içindeki Python Konsolunda:
import build_osm_level
build_osm_level.build_osm_level()

# Yöntem C: Bağımsız / Dry-Run Modu (UE5 olmadan test ve doğrulama):
python build_osm_level.py --dry-run --verbose
```

### 3. `setup_character_anims.py` — Karakter & Animasyon Kurulumu
Manny/Quinn skeletal mesh'leri, faceless placeholder materyalleri ve `ABP_BRCharacter` AnimBP kurulumunu yapar:

```bash
# Yöntem A: Unreal Engine Headless Commandlet:
UnrealEditor-Cmd.exe BakirkoyBR.uproject -run=pythonscript -script="setup_character_anims.py"

# Yöntem B: UE5 Editörü içindeki Python Konsolunda:
import setup_character_anims
setup_character_anims.setup_character_anims()

# Yöntem C: Bağımsız / Dry-Run Modu:
python setup_character_anims.py --dry-run --verbose
```

### 4. `generate_map.py` — Graybox Test Haritası Üretimi
Hızlı oynanış testleri için 200m x 200m kentsel graybox arenası üretir:

```bash
# Yöntem A: Unreal Engine Headless Commandlet:
UnrealEditor-Cmd.exe BakirkoyBR.uproject -run=pythonscript -script="generate_map.py"

# Yöntem B: UE5 Editörü içindeki Python Konsolunda:
import generate_map
generate_map.generate_map()

# Yöntem C: Bağımsız / Dry-Run Modu:
python generate_map.py --dry-run --verbose
```

### 5. `setup_blueprints.py` — Blueprint & Arayüz (UI) Kurulumu
GameMode, Karakter, Kontrolcü, Silah ve Kill Feed arayüz Blueprint'lerini oluşturur:

```bash
# Yöntem A: Unreal Engine Headless Commandlet:
UnrealEditor-Cmd.exe BakirkoyBR.uproject -run=pythonscript -script="setup_blueprints.py"

# Yöntem B: UE5 Editörü içindeki Python Konsolunda:
import setup_blueprints
setup_blueprints.setup_blueprints()

# Yöntem C: Bağımsız Doğrulama / Simülasyon:
python setup_blueprints.py
```

### 6. `package_game.ps1` — Windows Release Paketleme (RunUAT)
Oyunu paketleyip `Saved/Packages/` klasörüne bağımsız çalıştırılabilir Windows `.exe` olarak çıkarır:

```powershell
# Standart Shipping Build (Win64):
.\package_game.ps1 -Configuration Shipping -Platform Win64

# Geliştirici / Debug Build'i:
.\package_game.ps1 -Configuration Development -Platform Win64

# Derleme yapmadan proje yapılandırmasını ve komut planını doğrulamak için (Dry-Run):
.\package_game.ps1 -DryRun
.\package_game.ps1 -ValidateOnly

# Özel Unreal Engine yolu ile önceki artıkları temizleyerek paketleme:
.\package_game.ps1 -EnginePath "C:\Program Files\Epic Games\UE_5.5" -Clean
```

---

## 📌 Temel Kurallar ve Kısıtlar (Design Constraints)
1. **İç Mekan Yasağı (Rule C1 - Exterior Only):** Binaların iç mekanları kesinlikle kapalıdır (katı bloklar). Oynanış sokaklar, meydanlar ve çatı katlarında (dikey taktiksel alanlar) geçer.
2. **NavMesh Bütünlüğü:** Sokaklar ile çatılar arasındaki harici yangın merdivenleri ve rampalar NavMesh ile tam bağlantılıdır; botlar sokaktan çatıya kesintisiz tırmanabilir.
3. **10 Bot AI Sınırı:** İlk oynanabilir demo için AI bot sayısı tam olarak 10 adetle sınırlandırılmıştır (`BP_BRAIBotCharacter` + `ABRAIController`).
4. **Hibrit Silah Havuzu:** 1 Adet Hit-Scan Piyade Tüfeği (AR) ve 1 Adet Projectile Roketatar.
