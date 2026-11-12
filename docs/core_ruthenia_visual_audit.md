# Візуальний аудит основної Русі

Обсяг: ZAZ, HET, Козацьке Військо, CHR, UZH, KIE, а також спільні флейворні
гачки Південної України й Києва, що вже є в моді, і вміст єврейських
купецьких привілеїв міщанського стану та їхніх подій, уже вбудований у руський
геймплей. Цей аудит
фіксує лише ті ресурси, що не пройшли критерії й тому потребують або нового
гачка, або семантичної переробки.

Примітка: локалізацію місій CHR та UZH, що показувала заглушки, теж вичищено,
тож заблоковані слоти гілок більше не показують видимого тексту-заглушки.


## Бракує

| категорія | тип ресурсу | ключ вмісту | джерело | поточна графіка | проблема | запропонований ID | ціль гачка | стан |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| missing | mission icon | `uz_identity_branching_1` | `missions/Zakarpatta_Missions.txt :: uz_identity_branching_1` | `mission_unknown_mission` | Explicit placeholder icon on a locked identity branch slot. | `rip_gfx_mission_uzh_identity_branch_locked_1_icon` | `interface/rip_mission_icons.gfx :: rip_gfx_mission_uzh_identity_branch_locked_1_icon` | НЕ підключено: interface/rip_mission_icons.gfx не існує, DDS немає, місія й далі вживає ванільний mission_unknown_mission |
| missing | mission icon | `uz_identity_branching_2` | `missions/Zakarpatta_Missions.txt :: uz_identity_branching_2` | `mission_unknown_mission` | Explicit placeholder icon on a chained locked identity branch slot. | `rip_gfx_mission_uzh_identity_branch_locked_2_icon` | `interface/rip_mission_icons.gfx :: rip_gfx_mission_uzh_identity_branch_locked_2_icon` | НЕ підключено: interface/rip_mission_icons.gfx не існує, DDS немає, місія й далі вживає ванільний mission_unknown_mission |
| missing | mission icon | `uz_identity_branching_3` | `missions/Zakarpatta_Missions.txt :: uz_identity_branching_3` | `mission_unknown_mission` | Explicit placeholder icon on the terminal locked identity branch slot. | `rip_gfx_mission_uzh_identity_branch_locked_3_icon` | `interface/rip_mission_icons.gfx :: rip_gfx_mission_uzh_identity_branch_locked_3_icon` | НЕ підключено: interface/rip_mission_icons.gfx не існує, DDS немає, місія й далі вживає ванільний mission_unknown_mission |
| missing | mission icon | `chr_identity_branching_1` | `missions/Chernihiv_Missions.txt :: chr_identity_branching_1` | `mission_unknown_mission` | Explicit placeholder icon on a locked frontier-identity branch slot. | `rip_gfx_mission_chr_identity_branch_locked_1_icon` | `interface/rip_mission_icons.gfx :: rip_gfx_mission_chr_identity_branch_locked_1_icon` | НЕ підключено: interface/rip_mission_icons.gfx не існує, DDS немає, місія й далі вживає ванільний mission_unknown_mission |
| missing | mission icon | `chr_identity_branching_2` | `missions/Chernihiv_Missions.txt :: chr_identity_branching_2` | `mission_unknown_mission` | Explicit placeholder icon on a chained frontier-identity branch slot. | `rip_gfx_mission_chr_identity_branch_locked_2_icon` | `interface/rip_mission_icons.gfx :: rip_gfx_mission_chr_identity_branch_locked_2_icon` | НЕ підключено: interface/rip_mission_icons.gfx не існує, DDS немає, місія й далі вживає ванільний mission_unknown_mission |
| missing | mission icon | `chr_identity_branching_3` | `missions/Chernihiv_Missions.txt :: chr_identity_branching_3` | `mission_unknown_mission` | Explicit placeholder icon on the terminal frontier-identity branch slot. | `rip_gfx_mission_chr_identity_branch_locked_3_icon` | `interface/rip_mission_icons.gfx :: rip_gfx_mission_chr_identity_branch_locked_3_icon` | НЕ підключено: interface/rip_mission_icons.gfx не існує, DDS немає, місія й далі вживає ванільний mission_unknown_mission |

## Переробити

| категорія | тип ресурсу | ключ вмісту | джерело | поточна графіка | проблема | запропонований ID | ціль гачка | стан |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| redesign | government reform icon | `rip_cossacks_reform` | `common/government_reforms/RIP_shared_cossack_government_reforms.txt :: rip_cossacks_reform` | `horde_riding` | Reads as a generic nomad reform rather than the institutional Cossack Host. | `rip_gfx_reform_cossack_host_icon` | `interface/rip_government_reform_icons.gfx :: government_reform_rip_gfx_reform_cossack_host_icon` | підключено з запасним DDS, власна графіка в черзі |
| redesign | government reform icon | `zaz_sich_brotherhood_reform` | `common/government_reforms/RIP_ZAZ_government_reforms.txt :: zaz_sich_brotherhood_reform` | `fist_in_air` | Too abstract and modern-feeling for a Sich brotherhood frame. | `rip_gfx_reform_zaz_sich_brotherhood_icon` | `interface/rip_government_reform_icons.gfx :: government_reform_rip_gfx_reform_zaz_sich_brotherhood_icon` | підключено з запасним DDS, власна графіка в черзі |
| redesign | government reform icon | `het_starshyna_oligarchy_reform` | `common/government_reforms/RIP_HET_government_reforms.txt :: het_starshyna_oligarchy_reform` | `soldiers_6` | Misreads as rank-and-file infantry instead of a starshyna council regime. | `rip_gfx_reform_het_starshyna_oligarchy_icon` | `interface/rip_government_reform_icons.gfx :: government_reform_rip_gfx_reform_het_starshyna_oligarchy_icon` | підключено з запасним DDS, власна графіка в черзі |
| redesign | government reform icon | `het_academy_enlightenment_reform` | `common/government_reforms/RIP_HET_government_reforms.txt :: het_academy_enlightenment_reform` | `merchant_ship` | Commercial shipping icon obscures the educational and intellectual identity of the reform. | `rip_gfx_reform_het_academy_enlightenment_icon` | `interface/rip_government_reform_icons.gfx :: government_reform_rip_gfx_reform_het_academy_enlightenment_icon` | підключено з запасним DDS, власна графіка в черзі |
| redesign | government reform icon | `zaz_free_host_reform` | `common/government_reforms/RIP_ZAZ_government_reforms.txt :: zaz_free_host_reform` | `horde_riding` | Repeats the generic horse-archer silhouette instead of a distinct free-host Cossack elite identity. | `rip_gfx_reform_zaz_free_host_icon` | `interface/rip_government_reform_icons.gfx :: government_reform_rip_gfx_reform_zaz_free_host_icon` | підключено з запасним DDS, власна графіка в черзі |
| redesign | government reform icon | `zaz_last_sich_reform` | `common/government_reforms/RIP_ZAZ_government_reforms.txt :: zaz_last_sich_reform` | `mountain_fort` | Fortress icon implies alpine defense rather than the last autonomous Sich on the steppe frontier. | `rip_gfx_reform_zaz_last_sich_icon` | `interface/rip_government_reform_icons.gfx :: government_reform_rip_gfx_reform_zaz_last_sich_icon` | підключено з запасним DDS, власна графіка в черзі |
| redesign | estate privilege icon | `estate_jewish_tax_farmers` | `common/estate_privileges/RIP_shared_jewish_privileges.txt :: estate_jewish_tax_farmers` | `privilege_ducats` | Generic coin icon obscures the chartered tax-farming role of kahal financiers. | `rip_gfx_privilege_jewish_tax_farmers_icon` | `interface/rip_privilege_icons.gfx :: rip_gfx_privilege_jewish_tax_farmers_icon` | підключено з запасним DDS, власна графіка в черзі |
| redesign | estate privilege icon | `estate_jewish_loan_banks` | `common/estate_privileges/RIP_shared_jewish_privileges.txt :: estate_jewish_loan_banks` | `privilege_loan_interaction` | Functional but too generic to distinguish communal credit networks from normal borrowing tools. | `rip_gfx_privilege_jewish_loan_banks_icon` | `interface/rip_privilege_icons.gfx :: rip_gfx_privilege_jewish_loan_banks_icon` | підключено з запасним DDS, власна графіка в черзі |
| redesign | estate privilege icon | `estate_jewish_kahal_autonomy` | `common/estate_privileges/RIP_shared_jewish_privileges.txt :: estate_jewish_kahal_autonomy` | `privilege_autonomy` | Generic autonomy symbol hides the specific kahal self-governance identity. | `rip_gfx_privilege_jewish_kahal_autonomy_icon` | `interface/rip_privilege_icons.gfx :: rip_gfx_privilege_jewish_kahal_autonomy_icon` | підключено з запасним DDS, власна графіка в черзі |
| redesign | estate privilege icon | `estate_jewish_black_sea_network` | `common/estate_privileges/RIP_shared_jewish_privileges.txt :: estate_jewish_black_sea_network` | `privilege_caravans` | Caravan icon reads broadly and misses the maritime-diaspora brokerage angle. | `rip_gfx_privilege_jewish_black_sea_network_icon` | `interface/rip_privilege_icons.gfx :: rip_gfx_privilege_jewish_black_sea_network_icon` | підключено з запасним DDS, власна графіка в черзі |
| redesign | event picture | `south_ukraine_history.7` | `events/RIP_shared_steppe_SouthUkraineHistorical.txt :: south_ukraine_history.7` | Козаки й посланець обговорюють хартію | Умовна сцена до рішення, не документальний портрет. | `rip_gfx_event_south_ukraine_zaporozhian_autonomy_charter_art_eventPicture` | `interface/rip_eventpictures.gfx :: rip_gfx_event_south_ukraine_zaporozhian_autonomy_charter_art_eventPicture` | власний DDS; у грі не перевірено |
| redesign | event picture | `south_ukraine_history.12` | `events/RIP_shared_steppe_SouthUkraineHistorical.txt :: south_ukraine_history.12` | Посадовці над картою степу | Умовний план прикордоння, не історична карта. | `rip_gfx_event_south_ukraine_imperial_frontier_reform_eventPicture` | `interface/rip_eventpictures.gfx :: rip_gfx_event_south_ukraine_imperial_frontier_reform_eventPicture` | власний DDS; у грі не перевірено |
| redesign | event picture | `het_flavor.12` | `events/RIP_HET_HetmanateFlavor.txt :: het_flavor.12` | Імперські чиновники й старшина за столом | Художня інтерпретація колегії, не реконструкція засідання чи герба. | `rip_gfx_event_hetmanate_little_russian_collegium_eventPicture` | `interface/rip_eventpictures.gfx :: rip_gfx_event_hetmanate_little_russian_collegium_eventPicture` | власний DDS; у грі не перевірено |
| redesign | event picture | `kyiv_dnieper_history.10` | `events/RIP_shared_ruthenian_KyivDnieperHistorical.txt :: kyiv_dnieper_history.10` | Друкарський верстат і православний чернець | Умовна майстерня, не реконструкція конкретної київської друкарні. | `rip_gfx_event_kyiv_orthodox_printing_press_eventPicture` | `interface/rip_eventpictures.gfx :: rip_gfx_event_kyiv_orthodox_printing_press_eventPicture` | власний DDS; у грі не перевірено |
| redesign | event picture | `rip_jewish.1` | `events/RIP_shared_estates_JewishEstate.txt :: rip_jewish.1` | Купець і посадовець обговорюють охоронну грамоту | Умовна сцена без заяви про конкретних осіб або вже ухвалене рішення. | `rip_gfx_event_jewish_estate_invite_merchants_eventPicture` | `interface/rip_eventpictures.gfx :: rip_gfx_event_jewish_estate_invite_merchants_eventPicture` | власний DDS; у грі не перевірено |

### Перегляд ілюстрацій подій: 11 листопада 2026

П'ять наявних DDS у [event_pictures_rip](../gfx/event_pictures/event_pictures_rip/)
були ванільними заглушками: двічі `REFORM`, а також `COURT`,
`UNIVERSITY` і `MERCHANTS_TALKING`. Вони мають 512 × 132 пікселі, DXT1
без mipmaps; такий самий формат є і серед базових зображень ванілі. В інших
переглянутих ванільних ресурсах трапляються mipmaps та 32-бітний формат, тому
сама різниця не доводить помилки.

Після порівняння з ванільною вибіркою створено п'ять нових ілюстрацій:
чорнильний контур, штрихування й теплий пергамент збережено як спільний
художній напрям. Це згенеровані інтерпретації, а не свідчення вигляду
конкретних людей, споруд чи документів. Особливості одягу, карти та дрібної
геральдики потребують авторської історичної перевірки.

Джерела PNG збережено в [assets/event_pictures](../assets/event_pictures/),
остаточні промпти — в [документі промптів](core_ruthenia_visual_prompts.md).
[Генератор DDS](../tools/build_event_pictures.py) пропорційно кадрує
зображення до 512 × 132 і записує непрозорий 32-бітний DDS без DX10;
`python -B tools/build_event_pictures.py --check` перевіряє відповідність
вихідним PNG. Нові картинки показуються незалежно від DLC.

Усі п'ять старих локальних DDS збережено. Старий спрайт хартії далі
використовує `russian_orthodox.17`; сама хартія отримала окремий спрайт, щоб
не змінювати церковну подію. Раніше помічений нестандартний шлях локального
архіву Rights of Man тепер не впливає на зображення київської події.
Відображення жодної нової картинки безпосередньо в грі ще не перевірялося.
