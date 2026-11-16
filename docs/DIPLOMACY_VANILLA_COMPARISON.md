# Diplomacy comparison

Installed baseline: **EU4 v1.37.5.0 Inca (491d)**

Semantic comparison ignores comments and field order, preserves record multiplicity.
Merged files use exact-name overrides; different filenames add records. No replace_path is assumed.
Ownership screen evaluates province history on the relation start date only. It does not prove later existence, event releases or engine behavior.

| File | Records | Mode | Removed vanilla records | Added RIP records |
|---|---|---|---|---|
| Baltic_alliances.txt | 16 | override | 2 | 0 |
| KyivanProtection.txt | 1 | addition | 0 | 1 |
| Russian_alliances.txt | 49 | override | 2 | 1 |
| VolynHalich.txt | 5 | addition | 0 | 5 |
| ZaporizhiaHetmanate.txt | 20 | addition | 0 | 20 |

## Every local record

| File / record index | Type | Direction | Interval | Vanilla match | No province owner at start |
|---|---|---|---|---|---|
| Baltic_alliances.txt#1 | vassal | POL → MAZ | 1444.1.1–1526.3.9 | same | — |
| Baltic_alliances.txt#2 | guarantee | POL → MOL | 1444.1.1–1447.12.12 | same | — |
| Baltic_alliances.txt#3 | march | POL → MOL | 1447.12.12–1497.12.31 | same | — |
| Baltic_alliances.txt#4 | vassal | POL → TEU | 1466.10.19–1525.1.1 | same | — |
| Baltic_alliances.txt#5 | vassal | POL → PRU | 1525.1.1–1569.7.1 | same | PRU |
| Baltic_alliances.txt#6 | vassal | PLC → PRU | 1569.7.1–1618.8.28 | same | — |
| Baltic_alliances.txt#7 | vassal | PLC → BRA | 1618.8.28–1657.9.19 | same | — |
| Baltic_alliances.txt#8 | vassal | POL → KUR | 1561.11.28–1569.7.1 | same | — |
| Baltic_alliances.txt#9 | vassal | PLC → KUR | 1569.7.1–1795.3.28 | same | — |
| Baltic_alliances.txt#10 | union | PLC → SWE | 1592.1.1–1598.9.17 | same | — |
| Baltic_alliances.txt#11 | union | POL → LIT | 1386.7.1–1444.11.10 | same | — |
| Baltic_alliances.txt#12 | union | POL → LIT | 1447.6.25–1569.7.1 | same | — |
| Baltic_alliances.txt#13 | alliance | POL → NOV | 1470.11.8–1471.8.11 | same | — |
| Baltic_alliances.txt#14 | alliance | PLC → BRA | 1655.1.1–1656.1.17 | same | — |
| Baltic_alliances.txt#15 | vassal | LIT → TVE | 1449.8.31–1454.1.1 | same | — |
| Baltic_alliances.txt#16 | alliance | POL → GOL | 1472.1.1–1481.1.6 | same | — |
| KyivanProtection.txt#1 | guarantee | LIT → KIE | 1444.11.1–1471.1.1 | RIP | — |
| Russian_alliances.txt#1 | vassal | MOS → PSK | 1444.1.1–1503.4.1 | same | — |
| Russian_alliances.txt#2 | vassal | RUS → PSK | 1503.4.2–1510.1.19 | same | — |
| Russian_alliances.txt#3 | vassal | MOS → YAR | 1444.1.1–1463.1.1 | same | — |
| Russian_alliances.txt#4 | vassal | MOS → BLO | 1444.1.1–1486.1.1 | same | — |
| Russian_alliances.txt#5 | vassal | MOS → RSO | 1444.1.1–1474.1.1 | same | — |
| Russian_alliances.txt#6 | vassal | MOS → QAS | 1445.7.7–1503.4.1 | same | QAS |
| Russian_alliances.txt#7 | vassal | RUS → QAS | 1503.4.2–1681.1.1 | same | — |
| Russian_alliances.txt#8 | vassal | MOS → PRM | 1444.11.11–1503.4.1 | RIP | — |
| Russian_alliances.txt#9 | vassal | RUS → PRM | 1503.4.1–1505.4.1 | same | — |
| Russian_alliances.txt#10 | royal_marriage | MOS → TVE | 1452.6.4–1467.4.22 | same | — |
| Russian_alliances.txt#11 | vassal | MOS → TVE | 1454.1.1–1485.1.1 | same | — |
| Russian_alliances.txt#12 | vassal | MOS → NOV | 1456.2.1–1470.11.8 | same | — |
| Russian_alliances.txt#13 | vassal | MOS → RYA | 1456.1.1–1503.4.1 | same | — |
| Russian_alliances.txt#14 | vassal | RUS → RYA | 1503.4.2–1521.1.1 | same | — |
| Russian_alliances.txt#15 | royal_marriage | MOS → RYA | 1464.1.1–1483.1.7 | same | — |
| Russian_alliances.txt#16 | vassal | MOS → NOV | 1471.8.11–1477.10.9 | same | — |
| Russian_alliances.txt#17 | alliance | RUS → CRI | 1503.4.2–1505.10.27 | same | — |
| Russian_alliances.txt#18 | vassal | MOS → KAZ | 1487.7.9–1503.4.1 | same | — |
| Russian_alliances.txt#19 | vassal | RUS → KAZ | 1503.4.2–1505.6.24 | same | — |
| Russian_alliances.txt#20 | alliance | MOS → DAN | 1493.11.8–1503.1.1 | same | — |
| Russian_alliances.txt#21 | royal_marriage | MOS → LIT | 1494.2.5–1500.3.1 | same | — |
| Russian_alliances.txt#22 | alliance | RUS → SWE | 1567.2.16–1568.9.29 | same | — |
| Russian_alliances.txt#23 | alliance | RUS → SWE | 1609.2.28–1610.7.19 | same | — |
| Russian_alliances.txt#24 | alliance | RUS → PLC | 1686.5.6–1696.6.17 | same | — |
| Russian_alliances.txt#25 | alliance | RUS → PLC | 1699.11.21–1706.9.26 | same | — |
| Russian_alliances.txt#26 | alliance | RUS → SAX | 1699.11.21–1706.9.26 | same | — |
| Russian_alliances.txt#27 | alliance | RUS → DAN | 1700.4.30–1700.8.18 | same | — |
| Russian_alliances.txt#28 | alliance | RUS → PLC | 1709.10.9–1721.9.10 | same | — |
| Russian_alliances.txt#29 | alliance | RUS → SAX | 1709.10.9–1721.9.10 | same | — |
| Russian_alliances.txt#30 | alliance | RUS → DAN | 1709.10.11–1721.9.10 | same | — |
| Russian_alliances.txt#31 | alliance | RUS → PRU | 1713.9.18–1721.9.10 | same | — |
| Russian_alliances.txt#32 | alliance | RUS → HAN | 1715.1.1–1721.9.10 | same | — |
| Russian_alliances.txt#33 | vassal | RUS → KZH | 1732.1.1–1847.1.1 | same | — |
| Russian_alliances.txt#34 | alliance | RUS → SAX | 1733.8.14–1738.11.18 | same | — |
| Russian_alliances.txt#35 | union | RUS → SHL | 1762.1.5–1773.1.1 | same | — |
| Russian_alliances.txt#36 | alliance | RUS → PRU | 1762.6.19–1762.7.17 | same | — |
| Russian_alliances.txt#37 | alliance | RUS → PRU | 1764.4.11–1788.5.1 | same | — |
| Russian_alliances.txt#38 | vassal | RUS → GEO | 1783.8.4–1801.9.12 | same | — |
| Russian_alliances.txt#39 | alliance | RUS → GBR | 1798.12.24–1800.11.22 | same | — |
| Russian_alliances.txt#40 | alliance | RUS → HAB | 1798.12.24–1800.11.22 | same | — |
| Russian_alliances.txt#41 | alliance | RUS → NAP | 1798.12.24–1800.11.22 | same | — |
| Russian_alliances.txt#42 | alliance | RUS → POR | 1798.12.24–1800.11.22 | same | — |
| Russian_alliances.txt#43 | alliance | RUS → TUR | 1798.12.24–1800.11.22 | same | — |
| Russian_alliances.txt#44 | alliance | RUS → BAV | 1799.1.1–1800.11.22 | same | — |
| Russian_alliances.txt#45 | alliance | RUS → PRU | 1800.12.6–1801.3.24 | same | — |
| Russian_alliances.txt#46 | alliance | RUS → SWE | 1800.12.6–1801.3.24 | same | — |
| Russian_alliances.txt#47 | alliance | RUS → DAN | 1800.12.6–1801.3.24 | same | — |
| Russian_alliances.txt#48 | alliance | RUS → FRA | 1807.7.7–1810.1.1 | same | — |
| Russian_alliances.txt#49 | alliance | RUS → SAX | 1813.10.18–1814.11.10 | same | — |
| VolynHalich.txt#1 | union | HLC → VLN | 1439.11.1–1490.3.30 | RIP | — |
| VolynHalich.txt#2 | march | HUN → UZH | 1444.1.1–1825.1.1 | RIP | — |
| VolynHalich.txt#3 | alliance | HUN → LIT | 1438.7.1–1526.8.30 | RIP | — |
| VolynHalich.txt#4 | dependency | GOL → MOS | 1444.1.1–1480.11.11 | RIP | — |
| VolynHalich.txt#5 | alliance | MOS → CRI | 1474.4.1–1478.4.30 | RIP | — |
| ZaporizhiaHetmanate.txt#1 | vassal | LIT → ZAZ | 1555.1.1–1569.7.1 | RIP | — |
| ZaporizhiaHetmanate.txt#2 | vassal | PLC → ZAZ | 1569.7.1–1648.1.1 | RIP | — |
| ZaporizhiaHetmanate.txt#3 | vassal | RUS → ZAZ | 1654.1.8–1657.7.27 | RIP | — |
| ZaporizhiaHetmanate.txt#4 | vassal | PLC → ZAZ | 1658.9.16–1659.6.17 | RIP | — |
| ZaporizhiaHetmanate.txt#5 | vassal | RUS → ZAZ | 1659.6.18–1663.10.18 | RIP | — |
| ZaporizhiaHetmanate.txt#6 | vassal | TUR → ZAZ | 1669.1.1–1676.10.27 | RIP | — |
| ZaporizhiaHetmanate.txt#7 | vassal | RUS → ZAZ | 1686.5.6–1708.11.1 | RIP | — |
| ZaporizhiaHetmanate.txt#8 | alliance | SWE → ZAZ | 1708.11.1–1709.7.8 | RIP | — |
| ZaporizhiaHetmanate.txt#9 | vassal | RUS → ZAZ | 1709.7.9–1711.7.21 | RIP | — |
| ZaporizhiaHetmanate.txt#10 | alliance | ZAZ → CRI | 1648.3.1–1654.1.8 | RIP | — |
| ZaporizhiaHetmanate.txt#11 | alliance | ZAZ → CRI | 1624.1.1–1629.1.1 | RIP | — |
| ZaporizhiaHetmanate.txt#12 | vassal | RUS → HET | 1654.1.8–1708.11.1 | RIP | HET |
| ZaporizhiaHetmanate.txt#13 | alliance | SWE → HET | 1708.11.1–1709.7.8 | RIP | HET |
| ZaporizhiaHetmanate.txt#14 | vassal | RUS → HET | 1709.7.9–1764.11.10 | RIP | HET |
| ZaporizhiaHetmanate.txt#15 | alliance | ZAZ → HET | 1654.1.8–1663.1.1 | RIP | HET |
| ZaporizhiaHetmanate.txt#16 | alliance | ZAZ → HET | 1687.1.1–1709.7.8 | RIP | HET |
| ZaporizhiaHetmanate.txt#17 | guarantee | RUS → ZAZ | 1667.1.30–1686.5.6 | RIP | — |
| ZaporizhiaHetmanate.txt#18 | guarantee | PLC → ZAZ | 1667.1.30–1686.5.6 | RIP | — |
| ZaporizhiaHetmanate.txt#19 | vassal | TUR → ZAZ | 1711.7.21–1734.6.1 | RIP | — |
| ZaporizhiaHetmanate.txt#20 | vassal | RUS → ZAZ | 1734.6.1–1775.6.5 | RIP | — |

## Merged overlap findings

- multiple overlords [inherited vanilla pair]: Baltic_alliances.txt#7 / Scandinavian_alliances.txt#36; 1656-01-17–1656-11-20

## Reference/date findings


## Override changes and hashes

### Baltic_alliances.txt

RIP SHA256: `9a40d8ee27120622abd6e2c22128dab2b775d6c86011290cd44751aca8375736`

Vanilla SHA256: `0f0f1ea8339cf0d3c3c07f90cc9ddec661b42bb48a441ffc77a881da0a6061bf`

- Removed (1): `vassal {'end_date': '1569.7.1', 'first': 'POL', 'second': 'ZAZ', 'start_date': '1555.1.1'}`
- Removed (1): `vassal {'end_date': '1648.1.1', 'first': 'PLC', 'second': 'ZAZ', 'start_date': '1569.7.1'}`
### KyivanProtection.txt

RIP SHA256: `64770db6d8d36c7817b323452a476106e48d32e7ad22ea0cbde499597c898cfc`

### Russian_alliances.txt

RIP SHA256: `a586fca7660d17b2f534bdf52dc24e5f46035a774407171edae50808e4fec974`

Vanilla SHA256: `2c29c816b6e4d87d898a182f4b5aa7b6ec73b7ff5d3cb5786a0e94481dfd115a`

- Removed (1): `vassal {'end_date': '1503.4.1', 'first': 'MOS', 'second': 'PRM', 'start_date': '1444.1.1'}`
- Removed (1): `vassal {'end_date': '1775.8.3', 'first': 'RUS', 'second': 'ZAZ', 'start_date': '1654.1.8'}`
- Added (1): `vassal {'end_date': '1503.4.1', 'first': 'MOS', 'second': 'PRM', 'start_date': '1444.11.11'}`
### VolynHalich.txt

RIP SHA256: `9396a6329f7403bdf6b3e2daedc8b4a6c33d1f9c254f50f6835a75328ff2eb2f`

### ZaporizhiaHetmanate.txt

RIP SHA256: `3c1f796618c8e33f293a1cb40c302bf0d740ab6aa2b4ee1f24ced4aee0e63c08`

