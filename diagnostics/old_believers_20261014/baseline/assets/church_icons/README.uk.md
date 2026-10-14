# Джерела церковних ікон

2 жовтня 2026. Три нові растрові образи створено вбудованим `imagegen`
за стилістичним зразком штатного `russian_icons_strip.dds` з EU4 1.37.5.
Це декоративні образи для ігрових бонусів, без прив'язки до конкретного
історичного святого чи твердження про канонічний статус.

Оригінали: `gc_icon_liturgy.png`, `gc_icon_learning.png`,
`gc_icon_charity.png`. Гра використовує відповідні 64×64 DDS у
`gfx/interface/rip_church/`. Скрипт `tools/build_gc_devotional_icons.py`
лише зменшує зображення й кодує legacy RGBA DDS; `--check` перевіряє
відповідність джерелам. Сюжет і малюнок скрипт не змінює.

## Спільний запит

```text
Use case: stylized-concept. Asset type: one square painted Eastern Christian devotional icon for a Europa Universalis IV game UI. Input image is STYLE REFERENCE ONLY: a strip of five vanilla Orthodox icons; create ONE icon, never a strip. Match the restrained flat medieval icon painting, earthy red robes, muted gold halo and ochre background, dark reddish wooden panel with a narrow gold inner rim. One centered square panel, straight front view, entire panel visible, fills the square canvas. Broad readable shapes and a strong face/prop silhouette; this will be downsampled to only 42x42 pixels. No star-shaped medal, no generic modifier emblem, no gradients or 3D rendering, no photorealism, no letters, labels, numerals, inscriptions, UI text or watermarks. Keep composition simple and crisp. Opaque background inside the wooden panel.
```

До спільного запиту окремо додано сюжет кожного образу:

```text
Liturgy: Subject: a haloed Eastern bishop in ivory and crimson liturgical vestments, waist-up and facing the viewer, solemn face, holding a prominent gold Eucharistic chalice centrally at chest height. Clear ceremonial Christian liturgy theme.

Learning: Subject: a haloed Eastern monastic scholar wearing a deep crimson mantle, waist-up and facing the viewer, holding a large OPEN illuminated gospel book centrally at chest height. The open pale gold pages and dark binding must be clearly recognizable. No written text on the pages. Clear sacred learning theme.

Almsgiving: Subject: a haloed Eastern bishop in ivory and ochre robes, waist-up, extending a large round loaf of bread and a small gold alms coin to a humble recipient in a dark earthy robe in the lower-right foreground. Only two figures, the bishop dominant; charitable hand gesture and bread clearly visible. Clear Christian almsgiving theme.
```

Формат генерації: окремий непрозорий квадрат для кожної ікони.
Підписи, ціна, тривалість і доступність накладаються самим інтерфейсом.
