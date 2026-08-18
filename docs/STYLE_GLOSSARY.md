# Глосарій стилю й топонімів

> **Цей документ виконується, а не лише читається.** `tests/check_glossary.py`
> перевіряє англійську локалізацію проти розділів 1 і 3 і завершується з
> кодом 1 при порушенні, тож його можна ставити на гейт злиття.
>
> Звірено 2026-08-17: п'ять правил розділу 1 - Halych/Galich, Kamianets,
> Vilnius/Wilno, Kraków/Cracow і «the Porte» - були в таблиці, але тест їх не
> перевіряв. Саме тому в `ZAZ_HET_missions` уціліло «neither Moscow nor
> Istanbul». Виправлено, правила додано до тесту.

Написання й терміни нижче — це те, що мод уже вживає в переважній більшості
випадків. Файл записує вибір, щоб наступний автор не виводив його наново, а
рецензент відрізняв свідомий варіант від описки. Числа — кількість входжень в
англійській локалізації на час запису.

Мова-джерело — англійська. Французька, німецька й іспанська перенесені з неї
(див. `localisation/replace/zzz_RIP_untranslated_l_*.yml`), тож будь-яка зміна
починається в англійській і доходить до решти трьох лише тоді, коли її візьме
перекладач.

---

## 1. Топоніми

Українські форми для місць на власній території мода; усталені англійські —
для річок і для того, що поза нею. Саме тому *Kyiv* стоїть поруч із *Dnieper*
без суперечності: місто наше й нам його називати, а річка має англійську назву
старшу за мод.

| Вживати | Не вживати | Примітка |
|---|---|---|
| Kyiv | Kiev | 156 : 4 до цього проходу; поодинокі виправлено |
| Lviv | Lwów, Lemberg | 24 : 0 |
| Chernihiv | Chernigov | 77 : 0 |
| Kharkiv | Kharkov | у прозі. **Назва країни KHK лишається «Kharkov Host»** — див. §4 |
| Halych | Galich | 24 : 0 |
| Kamianets | Kamieniec, Kamenets | 13 : 0 |
| Podillia | Podolia | у прозі. **Назва країни POD лишається «Podolia»** — див. §4 |
| Volhynia | Volyn | у прозі. **Назва країни VLN лишається «Volyn»** — див. §4 |
| Bratslav | Braclaw | польську форму прибрано |
| Zaporozhia | Zaporizhia, Zaporizhzhia | за `ZAZ:0 "Zaporozhian Host"` |
| Dnieper | Dnipro | усталена англійська назва річки |
| Vilnius | Wilno, Vilna | 19 : 0 |
| Kraków | Cracow | 17 : 0 |
| the Porte | Sublime Porte, Istanbul | про османський уряд |

## 2. Інституції та уряди

Не перекладайте це англійською абстракцією. «The Rada elects the hetman» несе
світ; «democratic traditions» — ні. Саме така підміна була найбільшою вадою
тону в моді, і через неї цей розділ існує.

| Термін | Означає | Примітка |
|---|---|---|
| **Kish** | військо як ціле, табір за порогами | сама установа |
| **Kosh Otaman** | його виборний голова | завжди *Kosh*, ніколи *Kish Otaman* |
| **Rada** | рада; **Sich Rada**, **General Rada**, **Great Rada** | |
| **bulava** | гетьманська булава, а отже й сам уряд | «the bulava passes by acclamation» |
| **starshyna** | старшина, що переростає у шляхту | |
| **sotnia** | сотня і округа, з якої вона набирається | не *sotnya* |
| **register** | королівський реєстр платних козаків | головний важіль козацької політики |
| **sloboda** | оселя, вільна від панщини; мн. *slobodas* | |
| **palanka**, **zimovnyk** | січова паланка; зимівник | |
| **chaika**, мн. **chaiky** | січові річкові човни | |
| **otaman** | виборний старшина | не *ataman* |
| **voivode**, **voivodeship** | воєвода, воєводство | |
| **sejmik** | місцевий сеймик | з малої; **Sejm** — з великої |
| **szlachta**, **magnate** | шляхта Речі Посполитої та її магнатські роди | |
| **starosta** | королівський староста | чия влада уривається біля Січі |
| **Magdeburg law** | міський привілей | «chartered towns», а не «urban self-government» |
| **yasyr** | бранці, узяті в набігу | |
| **metropolitan**, **brotherhood** | київська митрополія; братства зі школами й друкарнями | |

## 3. Регістр

Взірцем є описи реформ VLN і HLC:

> Chartered towns exercise municipal self-government under the protections of
> Magdeburg law.
>
> The Sich Rada still gathers to guard Cossack privileges, yet the hetman's
> bulava now commands lasting authority.

Одне-два речення. Названа установа замість розряду. Сухе твердження замість
присуду. Звідси п'ять правил:

1. **Називайте річ.** Не «democratic traditions», а «the Rada elects the
   hetman, and the bulava passes by acclamation». Конкретна подробиця коштує
   стільки ж знаків, а світ із неї виростає.
2. **Жодних дат, за які текст не ручається.** Подія, що оголошує 1596 рік, а
   настає 1631-го, ламає власну рамку. Минулу дію назвати роком можна («the
   oath of 1573»), теперішню — ніколи.
3. **Наслідок, а не оцінка.** Не «this brings civilization and prestige», а:

   > at Kraków our sons learn Latin and law; they come home in Polish dress,
   > and some come home Catholic
4. **Кінчайте сухим застереженням.** Почерк Paradox — тінь сумніву, а не
   фанфари:

   > Whether the parishes will hear it that way is another matter.
   > A list serves whoever holds it.
   > Two of the three usually suffice.
5. **Варіанти — це голос ради.** Коротко й наказово: «Let the Sich stand
   surety for the old rite», а не «Support the Orthodox resistance». Серединна
   довжина варіанта в моді — чотири слова; тримайтеся її.

Уникайте: `identity`, `democracy`/`democratic`, `ethnic`, `ideology` — це
соціологія XX століття, і кожне слово траплялося в 15-70 разів частіше, ніж у
ванілі, доки їх не замінили. Уникайте знаків оклику в описах: ваніль уживає їх
у 7,8% рядків, мод тепер менше. Жодних згадок про те, що поза добою.

## 3a. Назви реформ

Взірцем є ваніль, а не власна вигадка. Три її звички варто перейняти:

1. **Кожне значуще слово з великої.** «Boyar Rada», не «Boyar elite». Ваніль
   не знає назв у стилі речення; мод мав дев'ять таких.
2. **Рідний термін лишається неперекладеним, коли він і є установою.** Ваніль
   пише `Iqta`, `Devshirme System`, `Tysyatsky Office`, `Namestnik Office`,
   `Legislative Sejm`, `Veche Republic` — і вже має `Sich Rada` та
   `Ruthenian Tsardom`. Отже `Rada`, `veche`, `udil`, `Cesarstvo` не
   потребують англійського відповідника — і не варто міняти їх на ближчий
   англійський синонім, як це сталося з «Kyivan Cesarstvo».
3. **Чужа доба й чужий світ не позичаються.** Механіка може повторювати
   сьоґунат, назва — ні. І жодних слів, молодших за добу: комісар, прем'єр,
   народна республіка.

Перейменування 18 серпня 2026 — механіку не змінено, лише назви:

| Ключ | Було | Стало | Чому |
|---|---|---|---|
| `kyivan_shogunate_reform` | Kyivan Shogunate | Kyivan Seniorate | японський термін на руському дворі; сеньйорат — саме той лад, який механіка й описує |
| `uzh_palatial_ruthenian_reform` | Triatomic Palatinate | Palatinate of Three Nations | triatomic — слово про молекули; ідеться про три нації |
| `ruthenian_principality_reform` | Ruthenian principality | Ruthenian Principality | регістр |
| `elected_assemblies_reform` | Elective assemblies | Veche Assemblies | названо установу: віче, а не розряд зборів |
| `boyar_elite_reform` | Boyar elite | Boyar Rada | боярська дума — установа Москви; тут князеві радить рада |
| `sacred_regulation_reform` | Sacred law | Sacred Law | регістр |
| `patriarch_engagement_reform` | Choose of Saints | Blessing of the Patriarch | «Choose of Saints» — зламана англійська |
| `merchant_nobility_reform` | Merchant nobility | Merchant Nobility | регістр |
| `open_trading_ports_reform` | Open trading ports | Open Trading Ports | регістр |
| `assembly_houses_reform` | Residents' assembly | Burgher Assemblies | названо станову громаду міщан, а не «мешканців» |
| `considerable_bloodline_reform` | Great Dynasty | Unbroken Dynasty | ідеться про безперервність лінії, а не про велич роду |
| `representation_monarchy_reform` | Representation in the monarchy | Crown and Estates | корона й стани — те, що реформа справді врівноважує |
| `legislative_rada_reform` | Legislative Viche Reformed | Legislative Rada | за взірцем ванільного Legislative Sejm; «Reformed» ні до чого |

**Однакова назва буває навмисною.** Три `ruthenian_factional_empire_*` звуться
однаково, бо це один уряд, що підміняє сам себе, коли змінюється панівна пара;
пару називає опис, не заголовок. Перш ніж розрізняти назви, перевірте, чи
реформи не є станами однієї механіки.

Разом із назвами пішли й титули правителів: `SHOGUN` став `SENIOR_KNIAZ`,
`KYIVAN_SHOGUNATE` — `KYIVAN_SENIORATE`, і так усі дев'ять ключів сходинки.
Подільські «People's Commissar», «Premier» і «Supreme Commissar» стали
«Citizen-Voivode», «First Consul» і «Consul of the Republic».

**Ключ `PRINCIPALITY` належить ванілі.** Мод перекривав його на «The
Principalities», а отже перейменовував ранг кожного ванільного руського
князівства. Тепер рангова назва мода зветься `RUTHENIAN_PRINCIPALITY`, а
ваніль знову каже «Principality».

## 4. Свідомі винятки

Це має вигляд непослідовності, але нею не є. Не чіпайте, доки не переглядають
саму систему назв.

| Ключ | Значення | Чому |
|---|---|---|
| `VLN` | Volyn | відрізняє князівство від `VOL` «Halycia-Volhynia» |
| `POD` | Podolia | усталена назва тега |
| `KHK` | Kharkov Host | власна назва історичного війська |
| `*_mechanic_desc` | порожньо | ваніль не описує базові урядові механіки |

## 5. Де записано рішення

- Перелік із 284 відхилених формулювань, що програли пізнішому файлові під час
  зведення, лежав у `docs/localisation_duplicate_variants.md`. Файл видалено:
  його замінила перевірка повторених ключів у `tests/check_script_layer.py`,
  яка ловить розбіжність одразу, а не постфактум. Кілька варіантів звідти варто
  було б переглянути ще раз (`Viyt` замість `POSADNYK`, `Osavul` замість
  `STARSHYNA_MARSHAL`) — шукайте їх в історії git.
- `tests/dev_tools/` — те, що навмисно тримають поза теками, які завантажує гра.
