"""Archive evidence and derive a report from observed counters only."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parent
RUN=ROOT/'run3'
subprocess.run([sys.executable,'-B',str(ROOT/'analyze.py'),'run3'],check=True,stdout=subprocess.DEVNULL)
obs=json.loads((RUN/'observations.json').read_text(encoding='utf-8'))
assert obs['target_reached'], 'Cannot certify a campaign before target save'
for base in (ROOT,ROOT/'run2',RUN):
    logs=base/'evidence_logs';logs.mkdir(exist_ok=True)
    for name in ('game.log','error.log','setup.log','system.log'):
        p=base/'userdir/logs'/name
        if p.exists():shutil.copy2(p,logs/name)
    manifest=json.loads((base/'manifest.json').read_text(encoding='utf-8'))
    manifest['status']='completed_target_save' if base==RUN else 'incomplete_early_process_exit'
    manifest['finalized_utc']=datetime.now(timezone.utc).isoformat()
    if base!=ROOT:manifest['source_parent']='../source_inventory.json (original frozen snapshot)'
    if base==RUN:
        manifest['observed_save_date']=obs['save_date']
        manifest['game_version']='EU4 v1.37.5.0 Inca (game.log)'
        inv=json.loads((RUN/'source_inventory.json').read_text())
        changed=[name for name,digest in inv.items() if hashlib.sha256((RUN/'snapshot'/name).read_bytes()).hexdigest()!=digest]
        manifest['snapshot_unchanged']=not changed
        assert not changed,changed
        source=RUN/'userdir/save games'/obs['save']
        # Save remains local/ignored, alongside its SHA-256 in observations.json.
        shutil.copy2(source,RUN/'userdir/save games/checkpoint_1465.eu4')
    (base/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
rows=[]
for tag,data in obs['cohorts'].items():
    c=data['counters'];n=c['n']
    pct=lambda k:f"{100*c.get(k,0)/n:.1f}%"
    rows.append('| '+tag+' | '+str(int(n))+' | '+pct('icon_locked')+' | '+pct('icon_low')+' | '+pct('icon_ready')+' | '+pct('synod_locked')+' | '+pct('synod_low')+' | '+pct('synod_ready')+' | '+f"{float(data['native']['patriarch_authority'])*100:.0f}"+' |')
report='''# Кампанійна перевірка темпу УГКЦ

Контрольний прогін `run3`: EU4 1.37.5.0, зерно 1001, 1444.11.11–'''+obs['save_date']+'''.
Цільове збереження отримане; три греко-католицькі держави керувалися ШІ.
Це один штучний сценарій із трьома державами, не три незалежні зерна і не ручне проходження.

| Держава | Спостережень | Ікона діє | Ікона відсутня, HC < 20 | Ікона доступна | Синод діє | Синод відсутній, HC < 20 | Синод доступний | HC наприкінці |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+'''

Частки обчислено з лічильників рушія, які накопичуються раз на 30 ігрових днів.
Відсутні лічильники трактуються як нулі. Частки ікони та синоду перекриваються,
тому їх не слід додавати. Активний ефект дає бонуси й не є простоєм.
Окремий `synod_other` у JSON позначає достатній ресурс при інших невиконаних умовах.

Перші ікони закінчилися 1449.11.11, перші установи — 1454.11.11.
До 1451 року ШІ повторно активував ікони в усіх трьох державах, зокрема
MOS та POL змінили початковий вибір на милостиню. Проміжна контрольна точка
`run3/observations_1451.1.1.json` показує 1–4 спостереження вільного доступного
слота до повторного використання. Після цього простій потрібно відрізняти
від дефіциту спільного ресурсу, а не автоматично називати cooldown.

За кодом після завершення ефектів немає додаткового строку очікування:
ікона вимагає 20 HC та вільного слота; синод також вимагає грошей і миру.
Безперервне оновлення обох ефектів коштує в середньому 6 HC на рік, без
інших витрат. Скорочення строків за незмінної ціни підвищить цю потребу.

Рекомендація: спершу перевіряти надходження HC, ціни й резервування ресурсу
ШІ, зберігаючи обмеження одним ефектом кожного типу. Оцінку того, чи цікаво
гравцю чекати та чи потрібна дострокова зміна політики, цей прогін не доводить.
Для неї потрібне ручне проходження зі зміною обставин у середині строку.
Ігрові ціни, тривалості й ефекти в межах цього тесту не змінювалися.

Артефакти: `run3/manifest.json`, `run3/launch.json`, `run3/exit.json`,
`run3/observations.json`, `run3/evidence_logs/`, `run3/source_inventory.json`.
Незмінна копія джерел і повне контрольне збереження залишені локально в
ігнорованих `snapshot/` та `userdir/`; SHA-256 збереження записано у JSON.

Перші два запуски завершилися до першого циклу й не є успішними кампаніями.
Перший мав надто довгий рядок журналу; другий — звернення до невстановлених
нульових змінних. У `run3` ці діагностичні помилки прибрано. Їхній причинний
зв'язок із завершенням попередніх процесів не встановлений. Загальний журнал
містить також інші помилки мода; завершення кампанії не означає їх відсутності.
'''
(ROOT/'REPORT.uk.md').write_text(report,encoding='utf-8')
print(report.split('Перші ікони')[0])
