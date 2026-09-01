# Локальна LLM: контракт і ROI

`local_llm.py` працює з локальним llama.cpp через OpenAI-сумісний
`http://localhost:8080/v1/chat/completions`. На цій машині це
Codestral-22B-v0.1 Q3_K_M: чотири слоти, близько 3 ток/с на слот і контекст
8192 токени. Сервер не має tool calling. Це генератор дешевих чернеток, не
автор, рев'юер чи джерело фактів.

## Універсальна інструкція

Додавайте до кожної задачі цей контракт або збирайте його через
`constrained_prompt()`:

```text
You generate one short draft only from the facts below.
Do not verify facts, find errors, or invent missing information.
Return only the requested format, with no explanation.
If the format cannot be met, return REJECT.

Task: <one atomic job>
Facts: <only verified facts needed for this item>
Answer contract: <exact length, vocabulary, and output shape>
```

Одна задача означає один незалежний рядок. Не передавайте корпус файлів,
історичні припущення, помилки перевірок або попередню невдалу відповідь.
Кожна відповідь мусить пройти механічний валідатор, потім огляд людини, і лише
після цього відповідний гейт мода. Модель ніколи не редагує `.txt` чи `.yml`.

## Коли це окупається

Використовуйте для щонайменше десятків, а краще сотень однотипних незалежних
чернеток: англійські назви modifiers, короткі option-тексти подій, допустимі
ключі локалізації з заданим префіксом, один вибір із закритого списку. Формат
можна перевірити кодом; зміст та історичність перевіряє людина.

Не використовуйте для аудиту скрипту, scope, ID провінцій, ванільних правил,
досяжності подій, пошуку багів або вільних багатореченнєвих текстів. Модель
галюцинує саме відсутність фактів; ці задачі вже мають детерміновані перевірки.

## Бібліотека

```python
from local_llm import Task, all_of, constrained_prompt, forbid, one_line, run_batch, title_case, word_count

checks = all_of(one_line, word_count(2, 5), title_case, forbid("identity", "democracy", "!"))
tasks = [
    Task(
        key="het_grain_trade",
        source="common/opinion_modifiers/het_opinion_modifiers.txt",
        prompt=constrained_prompt(
            "Name an EU4 opinion modifier",
            "The Hetmanate sells grain down the Dnieper.",
            "Title Case English noun phrase, two to five words, no quotes.",
        ),
        check=checks,
        max_tokens=16,
        metadata={"kind": "opinion_modifier"},
    ),
]
ok, rejected = run_batch(
    tasks,
    cache_path="tests/dev_tools/local_llm_cache.jsonl",
    report_path="tests/dev_tools/local_llm_report.jsonl",
)
```

`preflight(tasks)` перевіряє сервер і консервативно відхиляє задачу, що не
влізе в контекст. Викликайте її перед великим запуском. `run_batch()` повторює
відхилену відповідь рівно раз із температурою 0, відкидає дублікати після
`normalizer`, пише JSONL-звіт і за бажанням перевикористовує тільки вже
прийняті відповіді з кешу.

Після ручного внесення нової локалізації запускайте
`python tests/check_glossary.py`; після зміни скрипту — його вузький чек та
`python tests/check_clausewitz_braces.py`. Кеш і звіти є тимчасовими файлами
розробки: не додавати їх до мода чи коміту.

> Заміряні межі моделі, правило маршрутизації задач і пастки харнеса —
> `.claude/skills/local-llm/SKILL.md`. Цей файл лишається довідкою по API.
