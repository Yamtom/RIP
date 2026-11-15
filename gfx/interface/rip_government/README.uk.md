# Графіка державних механік, реформ і фракцій (`gfx/interface/rip_government`)

Каталог `gfx/interface/rip_government/` містить **76 активних текстур `.dds`**, зареєстрованих у **6 файлах `.gfx`**, а також вихідні мальовані матеріали й контакт-аркуші попереднього перегляду в підкаталозі `source/`. Кожна кнопка державної механіки, емблема шкали влади та фракція у моді має власну унікальну текстуру без дублювання.

---

## 1. Порівняння зі специфікаціями ванільної EU4 1.37.5

| Категорія UI | Ванільний еталон EU4 1.37.5 | Розмір / кадри / формат DDS | Конвенція RIP у `gfx/interface/rip_government/` |
| :--- | :--- | :--- | :--- |
| **Кнопки державних механік (82×82)** | `gfx/interface/government_mechanics/**/*.dds` (*devshirme*, *iqta*, *council_of_ten*, *mamluk*) | `82×82`, 1 кадр, 32-bit uncompressed BGRA (`A8R8G8B8`), `alpha[0,0] = 0`, `alpha[center] = 255` | **50 спрайтів**: одна характерна симетрична форма золотої/емалевої оправи на механіку (`round`, `octagon`, `arch`, `shield`, `hex`, `keep`), усередині — **рівно один чіткий мальований фокусний об’єкт** на гладкому радіальному оксамитовому тлі або цілісна мальована сцена без процедурних векторних накладок |
| **Кнопки та емблеми шкал руських князівств і Гетьманщини (72×72)** | `cossacks_ability_{adm,dip,mil}.dds`, `shogunate/*.dds`, `russian_ability_*.dds` | `72×72`, 1 кадр, 32-bit uncompressed RGBA/BGRA, медальйон `bbox=(1, 1, 70, 70)` (`~71%` непрозорих пікселів) | **15 спрайтів**: 12 круглих кнопок у золотій оправі (`r_outer = 32.5`, `r_halo_out = 34.5`) та 3 вільні емблеми шкал влади (`concord`, `prosperity`, `het_authority`) |
| **Іконки державних реформ (57×57)** | `gfx/interface/government_reform_icons/*.dds` | `57×57`, 1 кадр, 32-bit uncompressed BGRA без міпмапів (`13 124` байти), суцільний альфа-канал (`alpha = 255`), зовнішня 3px рамка | **2 спрайти** (`uzh_palanok_captaincy_reform.dds`, `captaincy_reform.dds`): мальована сцена `51×51` з кольорокорекцією у ванільний діапазон реформ (`pull_into_band`) у медіанній 3px рамці ванільної іконки реформи |
| **Двокадрові смуги States General** | `republic_icon_strip.dds` (`54×19`, 2×`27×19`), `monarchism_icon_strip.dds` (`46×25`, 2×`23×25`) | `noOfFrames = 2`, однаковий альфа-силует обох кадрів (`alpha_max_diff = 0`, `alpha[0,0] = 0`), кадр 1 приглушений, кадр 2 золотий | **4 спрайти** (`uzh_partia_soymu.dds` `54×19`, `uzh_partia_kapitaniv.dds` `46×25`) + **3 спрайти** Тристанової ради (`kru_rada_{knyazi,boyary,starshyna}.dds` `46×25`) |
| **Емблеми фракцій (104×104)** | `gfx/interface/*_icon.dds` (`guilds_icon.dds`, `aristocrats_icon.dds`, `traders_icon.dds`) | `104×104`, 1 кадр, 32-bit RGBA з прозорим тлом у кутах, парний фон `faction_*_frame.tga` | **5 спрайтів** (`faction_knyazi.dds`, `faction_boyary.dds`, `faction_starshyna.dds`, `faction_rep_knyazi.dds`, `faction_rep_boyary.dds`) |

---

## 2. Реєстр усіх 76 спрайтів за генераторами та `.gfx`-файлами

### 2.1. `tools/build_ruthenian_government_ui.py` → `interface/rip_ruthenian_government.gfx` (20 текстур)
- **Кнопки механік князівств і фракційного двору (`72×72`, золота кругла оправа)**:
  - `siversk_charter.dds` (`GFX_rip_siversk_charter`) — `source/charter.png`
  - `siversk_towns.dds` (`GFX_rip_siversk_towns`) — `source/towns.png`
  - `siversk_retinue.dds` (`GFX_rip_siversk_retinue`) — `source/atlas.png` `(2, 0)`
  - `kyiv_snem.dds` (`GFX_rip_kyiv_snem`) — `source/snem.png`
  - `kyiv_udil.dds` (`GFX_rip_kyiv_udil`) — `source/atlas.png` `(0, 1)`
  - `kyiv_druzhyna.dds` (`GFX_rip_kyiv_druzhyna`) — `source/druzhyna.png`
  - `kyiv_levy.dds` (`GFX_rip_kyiv_levy`) — `source/atlas.png` `(2, 1)`
  - `kyiv_rota.dds` (`GFX_rip_kyiv_rota`) — `source/atlas.png` `(3, 1)`
  - `kyiv_grants.dds` (`GFX_rip_kyiv_grants`) — `source/atlas.png` `(0, 2)`
  - `kru_court_knyazi.dds` (`GFX_rip_kru_court_knyazi`) — `source/atlas.png` `(1, 2)` у круглій золотій оправі кнопки
  - `kru_court_boyary.dds` (`GFX_rip_kru_court_boyary`) — `source/atlas.png` `(2, 2)` у круглій золотій оправі кнопки
  - `kru_court_starshyna.dds` (`GFX_rip_kru_court_starshyna`) — `source/atlas.png` `(3, 2)` у круглій золотій оправі кнопки
- **Емблеми шкал влади (`72×72`, без рамки, масштабуються у `.gui` з `scale = 0.5`)**:
  - `concord.dds` (`GFX_rip_concord`) — `source/concord.png`
  - `prosperity.dds` (`GFX_rip_prosperity`) — `source/prosperity.png`
  - `het_authority.dds` (`GFX_rip_het_authority`) — схрещені золота гетьманська булава й срібний старшинський пернач під червоною стрічкою (`disasters/source/hetman_succession_crisis.png`)
- **Емблеми фракцій (`104×104`)**:
  - `faction_knyazi.dds` (`GFX_faction_kru_knyazi`) — `source/atlas.png` `(1, 2)`
  - `faction_boyary.dds` (`GFX_faction_kru_boyary`) — `source/atlas.png` `(2, 2)`
  - `faction_starshyna.dds` (`GFX_faction_kru_starshyna`) — `source/atlas.png` `(3, 2)`
  - `faction_rep_knyazi.dds` (`GFX_faction_rep_knyazi`) — княжий вінець із соборною грамотою (`source/atlas.png` `(0, 1)`)
  - `faction_rep_boyary.dds` (`GFX_faction_rep_boyary`) — різьблені крісла боярської ради (`source/atlas.png` `(3, 0)`)

### 2.2. `tools/build_government_ability_icons.py` → `interface/rip_ability_icons.gfx` (37 текстур `82×82`)
- **Боярська рада Галичини (`round`, багряна емаль)**:
  - `boyar_office.dds`, `boyar_claimant.dds`, `boyar_example.dds`
- **Коронні ординації (`octagon`, чорно-золота емаль)**:
  - `chancery_ordinance.dds`, `settlement_ordinance.dds`, `cadastre_ordinance.dds`, `urbarial_ordinance.dds`, `toleration_ordinance.dds`, `frontier_ordinance.dds`
- **Інституційні постанови (`round`, бірюзова / фіолетова / бурштинова емаль)**:
  - `resolution_municipal_charters.dds`, `resolution_municipal_accounts.dds`, `resolution_chancery_service.dds`, `resolution_chancery_rights.dds`, `resolution_register_muster.dds`, `resolution_register_settlement.dds`
- **Волинський магнатський сенат (`arch`, синя емаль)**:
  - `senate_summon.dds`, `senate_buyoff.dds`, `senate_banners.dds`
- **Литовська Пани-Рада (`shield`, шарлатова емаль зі срібним кантом)**:
  - `rada_confirm.dds`, `rada_lord.dds`, `rada_retinues.dds`
- **Чернігово-Сіверське вічеве князівство (`arch`, золотисто-бурштинова емаль)**:
  - `rg_chr_bell.dds`, `rg_chr_staple.dds`, `rg_chr_militia.dds`
- **Закарпатська жупна автономія (`octagon`, смарагдово-зелена емаль)**:
  - `rg_uzh_salt.dds`, `rg_uzh_guides.dds`, `rg_uzh_pass.dds`
- **Подільський прикордонний капітанат (`shield`, багряно-золота емаль)**:
  - `rg_pdl_patrol.dds`, `rg_pdl_charter.dds`, `rg_pdl_mobile.dds`
- **Переяславська лівобережна сторожа (`round`, кобальтово-синя емаль)**:
  - `rg_prl_patrol.dds`, `rg_prl_charter.dds`, `rg_prl_mobile.dds`
- **Чорноморський адміралтейський комісаріат Одеси (`octagon`, морська бірюзова емаль)**:
  - `rg_ods_freight.dds`, `rg_ods_corsairs.dds`
- **Гетьманська булава та Генеральна канцелярія (`shield`, пурпурово-золота емаль)**:
  - `het_rights.dds`, `het_chancery.dds`

### 2.3. `tools/build_uzh_states_general_icons.py` → `interface/rip_uzh_states_general.gfx` (3 текстури)
- `uzh_palanok_captaincy_reform.dds` (`57×57`, 1 кадр) — мальований замок Паланок (`great_projects/source/palanok_fortress.png`) у ванільній 3px рамці реформи
- `uzh_partia_soymu.dds` (`54×19`, 2 кадри по `27×19`) — мальований сеймовий статут і грамота з печаткою (`privileges/source/seimski_statutes.png`)
- `uzh_partia_kapitaniv.dds` (`46×25`, 2 кадри по `23×25`) — мальована замкова твердиня з червоним щитом (`source/atlas.png` `(3, 3)`)

### 2.4. `tools/build_kru_rada.py` → `interface/rip_kru_rada.gfx` (3 текстури `46×25`)
- `kru_rada_knyazi.dds`, `kru_rada_boyary.dds`, `kru_rada_starshyna.dds` (2 кадри по `23×25`, спільний альфа-силует з темним обідком у кадрі 0 та золотим підсвіченням у кадрі 1)

### 2.5. `tools/build_captaincy_icons.py` → `interface/rip_captaincy_icons.gfx` (7 текстур)
- **Карпатське капітанство (`82×82`, шестикутна оправа `hex`, лісова зелена емаль)**:
  - `captaincy_posts.dds`, `captaincy_salt.dds`, `captaincy_opryshky.dds`
- **Прикордонна сторожа (`82×82`, бастіонна оправа зі скошеними кутами `keep`, сланцево-синя емаль)**:
  - `watch_towers.dds`, `watch_patrols.dds`, `watch_settlers.dds`
- **Картка реформи (`57×57`)**:
  - `captaincy_reform.dds` (`government_reform_rip_gfx_reform_uzh_carpathian_captaincy_icon`) — мальований Верецький перевал зі сторожовою вежею та щитом (`missions/source/uzh_identity_branch_locked_2.png`) у ванільній 3px рамці реформи

### 2.6. `tools/build_faith_reform_icons.py` → `interface/rip_faith_reform_icons.gfx` (7 текстур `82×82`)
- **Свята опіка Війська Запорозького (`round`, синя емаль)**:
  - `zaz_monastery.dds`, `zaz_escort.dds`, `zaz_faithful.dds`, `zaz_zeal.dds` (емблема шкали Козацької ревності)
- **Полоцький Номоканон (`arch`, зелена емаль)**:
  - `plt_seal.dds`, `plt_guild.dds`, `plt_veto.dds`

---

## 3. Команди регенерації та перевірки

```powershell
python -B tools/build_ruthenian_government_ui.py
python -B tools/build_government_ability_icons.py
python -B tools/build_uzh_states_general_icons.py
python -B tools/build_kru_rada.py
python -B tools/build_captaincy_icons.py
python -B tools/build_faith_reform_icons.py
python -B tools/build_regional_governments.py
python -B tools/build_hetman_authority.py
python -B tools/build_core_ruthenia_icons.py

python -B tests/check_ruthenian_government_ui.py
python -B tests/check_government_ability_icons.py
python -B tests/check_regional_governments.py
python -B tests/check_hetman_authority.py
python -B tests/check_uzh_states_general.py
python -B tests/check_kru_rada.py
python -B tests/check_carpathian_captaincy.py
python -B tests/check_border_watch.py
python -B tests/check_file_encoding.py
python -B tests/check_clausewitz_braces.py
```
