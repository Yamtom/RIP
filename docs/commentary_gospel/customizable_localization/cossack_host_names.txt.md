# Commentary Gospel ? cossack_host_names.txt

- Source: `customizable_localization/cossack_host_names.txt`
- Extraction date: 2026-03-02
- Extracted descriptive comments: 17

## Canonical Excerpts

| Original line | Commentary |
|---:|---|
| 1 | ========================================================================= |
| 3 | ========================================================================= |
| 5 | All major Cossack military formations used "Host" (вiйсько/войско) designation: |
| 12 | This reflects their military-administrative nature as autonomous armed forces |
| 13 | rather than traditional states. The term emphasized their status as permanent |
| 14 | military societies organized for frontier defense and raiding. |
| 17 | Uses EU4's customizable localization system to dynamically add "Host" suffix |
| 18 | to Cossack state names based on government reforms and culture. |
| 21 | - Brian Boeck, "Imperial Boundaries" (2009), Ch. 3 |
| 22 | - Shane O'Rourke, "Warriors and Peasants" (2000), pp. 15-45 |
| 23 | - Albert Seaton, "The Horsemen of the Steppes" (1985) |
| 24 | ========================================================================= |
| 43 | Hetmanate (special case - not called "Host" until late period) |
| 52 | Don Host (if tag exists in mod) |
| 64 | Kuban Host (if tag exists in mod) |
| 76 | Terek Host (if tag exists in mod) |
| 88 | Generic Cossack Host (fallback for any Cossack-governed state) |

## Supplemental Excerpts (2026-03-02)

| Current line | Commentary |
|---:|---|
| 1 | COSSACK STATES "HOST" NAMING SYSTEM |
| 2 | HISTORICAL CONTEXT: |
| 3 | - Zaporozhian Host (Військо Запорозьке) |
| 4 | - Don Host (Донское войско) |
| 5 | - Kuban Host (Кубанское войско) |
| 6 | - Terek Host (Терское войско) |
| 7 | - Black Sea Host (Черноморское войско) |
| 8 |  |
| 9 |  |
| 10 | IMPLEMENTATION: |
| 11 |  |
| 12 | REFERENCES: |
| 17 | Zaporozhian Host |
| 39 | text = { |
| 40 | trigger = { |
| 41 | tag = DON |
| 42 | OR = { |
| 43 | has_reform = cossacks_reform |
| 44 | has_reform = zaz_sich_brotherhood_reform |
| 45 | } |
| 46 | } |
| 47 | localisation_key = DON_HOST_NAME |
| 48 | } |
| 50 | text = { |
| 51 | trigger = { |
| 52 | tag = KUB |
| 53 | OR = { |
| 54 | has_reform = cossacks_reform |
| 55 | has_reform = zaz_sich_brotherhood_reform |
| 56 | } |
| 57 | } |
| 58 | localisation_key = KUBAN_HOST_NAME |
| 59 | } |
| 61 | text = { |
| 62 | trigger = { |
| 63 | tag = TRK |
| 64 | OR = { |
| 65 | has_reform = cossacks_reform |
| 66 | has_reform = zaz_sich_brotherhood_reform |
| 67 | } |
| 68 | } |
| 69 | localisation_key = TEREK_HOST_NAME |
| 70 | } |
| 84 | Default: regular country name |
| 90 | Rank-based titles for Cossack Hosts |
| 94 | Rank 1: Local Host |
| 106 | Rank 2: Great Host |
| 118 | Rank 3: Imperial Host |
| 136 | Host Commander Title |
| 140 | Zaporozhian Sich - Kosh Otaman |
| 149 | Hetmanate - Hetman |
| 157 | Don Host - Ataman (if tag exists) |
| 158 | text = { |
| 159 | trigger = { |
| 160 | tag = DON |
| 161 | has_reform = cossacks_reform |
| 162 | } |
| 163 | localisation_key = DON_ATAMAN_TITLE |
| 164 | } |
| 166 | Generic - Otaman |
