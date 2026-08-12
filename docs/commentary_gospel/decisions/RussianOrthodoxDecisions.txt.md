# Commentary Gospel ? RussianOrthodoxDecisions.txt

- Source: `decisions/RussianOrthodoxDecisions.txt`
- Extraction date: 2026-03-02
- Extracted descriptive comments: 4

## Canonical Excerpts

| Original line | Commentary |
|---:|---|
| 1 | ========================================================================= |
| 3 | ========================================================================= |
| 242 | COMMENTED OUT: These decisions have scope issues and need to be rewritten |
| 243 | They reference province-level triggers in a country-level decision context |

## Supplemental Excerpts (2026-03-02)

| Current line | Commentary |
|---:|---|
| 1 | RUSSIAN ORTHODOX DECISIONS |
| 5 | Convert to Russian Orthodox (Third Rome) |
| 55 | Establish Moscow Patriarchate |
| 87 | Launch Russification Campaign |
| 122 | Establish Orthodox Inquisition |
| 154 | Gathering of Russian Lands |
| 184 | Establish Symphonia of Powers |
| 210 | Proclaim Orthodox Empire |
| 240 | force_convert_province_decision = { |
| 241 | potential = { |
| 242 | NOT = { religion = russian_orthodox } |
| 243 | } |
| 244 |  |
| 245 | provinces_to_highlight = { |
| 246 | province_id = THIS |
| 247 | } |
| 248 |  |
| 249 | allow = { |
| 250 | owner = { |
| 251 | religion = russian_orthodox |
| 252 | adm_power = 50 |
| 253 | mil_power = 25 |
| 254 | } |
| 255 | } |
| 256 |  |
| 257 | effect = { |
| 258 | owner = { |
| 259 | add_adm_power = -50 |
| 260 | add_mil_power = -25 |
| 261 | } |
| 262 | change_religion = russian_orthodox |
| 263 | } |
| 264 |  |
| 265 | ai_will_do = { |
| 266 | factor = 1 |
| 267 | modifier = { |
| 268 | factor = 0 |
| 269 | owner = { |
| 270 | NOT = { local_autonomy = 50 } |
| 271 | } |
| 272 | } |
| 273 | modifier = { |
| 274 | factor = 2 |
| 275 | owner = { |
| 276 | has_country_modifier = orthodox_inquisition |
| 277 | } |
| 278 | } |
| 279 | } |
| 280 | } |
| 282 | Russify Province - COMMENTED OUT |
| 283 | russify_province_decision = { |
| 284 | potential = { |
| 285 | owner = { |
| 286 | religion = russian_orthodox |
| 287 | primary_culture = russian |
| 288 | } |
| 289 | NOT = { culture_group = east_slavic } |
| 290 | NOT = { has_province_modifier = russian_settlement } |
| 291 | is_city = yes |
| 292 | } |
| 293 |  |
| 294 | provinces_to_highlight = { |
| 295 | province_id = THIS |
| 296 | } |
| 297 |  |
| 298 | allow = { |
| 299 | owner = { |
| 300 | adm_power = 75 |
| 301 | has_country_modifier = forced_russification |
| 302 | } |
| 303 | nationalism = 0 |
| 304 | } |
| 305 |  |
| 306 | effect = { |
| 307 | owner = { |
| 308 | add_adm_power = -75 |
| 309 | } |
| 310 | russify_province_effect = yes |
| 311 | } |
| 312 |  |
| 313 | ai_will_do = { |
| 314 | factor = 1 |
| 315 | modifier = { |
| 316 | factor = 0.1 |
| 317 | development = 20 |
| 318 | } |
| 319 | modifier = { |
| 320 | factor = 2 |
| 321 | development = 10 |
| 322 | } |
| 323 | } |
| 324 | } |
