# Як підключити `eu4-mod-auditor` у новому чаті

Skill збережено в репозиторії тут:

`.agents/skills/eu4-mod-auditor/`

Він призначений для аудиту, виправлення й перевірки EU4/Clausewitz-модів:
events, missions, decisions, CB, claims, scope, province IDs, localisation,
документації та runtime evidence.

## Варіант 1 — новий чат у цьому репозиторії

1. Завершіть або оновіть поточний чат.
2. Відкрийте новий Codex-чат із робочою директорією в корені RIP або будь-якій
   вкладеній папці цього Git-репозиторію.
3. Codex автоматично просканує `.agents/skills` до кореня репозиторію.
4. У першому повідомленні викличте skill явно:

   `$eu4-mod-auditor перевір [назва системи або файли] і виправ знайдені дефекти`

Якщо skill не з'явився у списку, перезапустіть Codex і перевірте командою
`/skills` або введіть `$eu4-mod-auditor`.

## Варіант 2 — зробити skill глобальним на Windows

Скопіюйте всю папку `eu4-mod-auditor` у користувацький каталог skills:

```powershell
$source = "D:\Users\Yamtom\Documents\Paradox Interactive\Europa Universalis IV\mod\RIP\.agents\skills\eu4-mod-auditor"
$targetRoot = Join-Path $HOME ".agents\skills"
New-Item -ItemType Directory -Force -Path $targetRoot
Copy-Item -Recurse -Force -LiteralPath $source -Destination $targetRoot
```

Після копіювання відкрийте новий чат або перезапустіть Codex. Глобальна копія
буде доступна в інших репозиторіях також.

## Варіант 3 — перенесення на інший комп'ютер

1. Заархівуйте папку `.agents/skills/eu4-mod-auditor` разом з усіма
   `references/`.
2. На іншому комп'ютері розпакуйте її як:
   `$HOME/.agents/skills/eu4-mod-auditor/`.
3. Переконайтеся, що файл лежить саме за адресою
   `$HOME/.agents/skills/eu4-mod-auditor/SKILL.md`.
4. Перезапустіть Codex і викличте `$eu4-mod-auditor`.

## Приклади запитів у новому чаті

```text
$eu4-mod-auditor перевір, чи повністю реалізована Ottoman reaction, і якщо ні — заверши та протестуй.
```

```text
$eu4-mod-auditor зроби read-only аудит KIE/KRU claim pacing; нічого не змінюй.
```

```text
$eu4-mod-auditor перевір Border/Qasim event chains, province IDs, CB semantics і синхронність документації.
```

```text
$eu4-mod-auditor виконай startup smoke, але не називай його observer run і збережи шлях до артефактів.
```

Skill також може активуватися автоматично за відповідним описом задачі, але
явний `$eu4-mod-auditor` у першому повідомленні дає найпередбачуваніший результат.

Довідка OpenAI: <https://learn.chatgpt.com/docs/build-skills>
