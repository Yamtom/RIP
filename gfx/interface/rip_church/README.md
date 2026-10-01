# Архієпископ для Hierarchical Capacity

`gc_archbishop_low.dds` і `gc_archbishop_high.dds`: прозорі RGBA DDS,
38×38 — штатний розмір кінцевих іконок Patriarch Authority. Видимі лише
для `greek_catholic`. Нативні православні зображення не замінено глобально.
PNG поряд — варіанти для перегляду; `gc_archbishop_source.png` — джерельний
аркуш, створений вбудованим imagegen 1 жовтня 2026. Для UI-читабельності
нижній індикатор охолоджено до синьо-срібного, верхній зігріто до золото-
бордового й горизонтально віддзеркалено, щоб єпископський жезл дивився до
шкали. Верхню іконку також посунуто ближче до шкали в
`interface/countryreligionview.gui`. Прозорість і розмір кінцевих DDS збережено.

Це символічний унійний архієпископ у східних ризах, не портрет конкретної
історичної особи й не Папа. Прев’ю: `diagnostics/church_gui_20261001/archbishop_preview.png`.

## Промпт генерації

Create a production game UI sprite sheet for Europa Universalis IV. Reference image shows the native patriarch authority endpoint busts enlarged 3x: use it ONLY as a style/scale reference, not as the character to copy. Output transparent PNG, 1024x512 or 2:1 aspect ratio. Two equal square cells side by side; one identical bust in each, fully contained with 10% transparent padding. Subject: a symbolic Ruthenian Greek Catholic UNION ARCHBISHOP, an Eastern-rite bishop in communion with Rome, not a pope. Front-facing elderly bishop bust, short grey beard, burgundy-red Eastern liturgical vestments, white omophorion with small dark crosses, a gold Byzantine domed mitre with a single small cross, slim Eastern episcopal crozier. No papal triple tiara, no coat of arms, no text, no frame, no background. Native EU4 miniature sprite aesthetic: hand-painted, restrained warm antique gold, dark fine silhouette, simplified facial features, high contrast readable at 38x38 pixels, slight worn oil-painted shading, NOT photorealistic, NOT glossy 3D, NOT cartoon. Left cell: identical bishop but cool blue-silver and muted grey/burgundy, symbolizing low capacity. Right cell: the same bishop in warmer gold and burgundy, mirrored horizontally so the crozier points inward toward the gauge, symbolizing high capacity. Maintain equal sprite sizes and aligned baselines. Transparent alpha background, no checkerboard baked in, no halos, no labels. Export the image to a local file if the tool provides file output.
