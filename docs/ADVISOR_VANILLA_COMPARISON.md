# Advisor comparison snapshot

Vanilla: `D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV`

Installed version: **EU4 v1.37.5.0 Inca (491d)**

RIP records: **152**; {'vanilla identical': 89, 'RIP addition': 54, 'RIP changed': 9}.

Comparison ignores comments, whitespace and field order. Decoding: UTF-8, falling back to Windows-1252 for diagnosis. Non-UTF-8 RIP files are reported explicitly.

This is a structural comparison, not a historical certificate or a runtime test. Definition lookup checks identifier existence, not engine semantics.

## Vanilla SHA-256

- `PolandRussia.txt`: `377db0051bc12b37a0a3c06af0651559e492ac005cd25a2f924c94027b7c1053`
- RIP `PolandRussia.txt`: `0dd30abcdf2f3727773ddb2a07a28cef5a715fae5bac56bfd12ae2328c3b1634`

## Structural errors

history\advisors\PolandRussia.txt: not valid UTF-8; decoded as Windows-1252 for diagnosis only

## Review warnings

common\cultures\00_cultures.txt: not valid UTF-8; decoded as Windows-1252 for diagnosis only

## Changed vanilla fields

| ID | Name | Vanilla → RIP |
|---|---|---|
| 994 | Nil Sorsky | location: 306 → 295 |
| 1020 | Konstanty Ostrohski | culture: — → ruthenian; name: Konstanty Ostrogski → Konstanty Ostrohski; religion: — → orthodox |
| 1024 | Ivan Fedorov | culture: — → ruthenian; location: 295 → 2961; name: Ivan Fyodorov → Ivan Fedorov; religion: — → orthodox |
| 1025 | Pyotr Mstislavets | culture: — → byelorussian |
| 1040 | Epifany Slavinetsky | culture: — → ruthenian; religion: — → orthodox |
| 1054 | Theophan Prokopovich | culture: — → ruthenian; religion: — → orthodox |
| 1064 | Alexei Razumovsky | culture: — → ruthenian; name: Aleksei Razumovsky → Alexei Razumovsky |
| 1072 | Kirill Razumovsky | culture: — → ruthenian |
| 1083 | Vasily Kapnist | culture: — → ruthenian |

## Complete RIP inventory

| ID | Name | Role / skill | Province ID: current map name | Availability fields | Culture / religion | Comparison |
|---|---|---|---|---|---|---|
| 988 | Andrei Rublev | artist / 1 | 295: Moskva | 1399.1.1 — 1430.12.31 | inherited / inherited | vanilla identical |
| 989 | Zbigniew Olesnicki | theologian / 2 | 262: Krakow | 1410.1.1 — 1455.4.1 | inherited / inherited | vanilla identical |
| 990 | Grzegorz of Sanok | philosopher / 1 | 260: Lublin | 1454.1.1 — 1477.1.29 | inherited / inherited | vanilla identical |
| 991 | Jan Ostroróg | statesman / 2 | 254: Poznan | 1455.1.1 — 1501.1.1 | inherited / inherited | vanilla identical |
| 992 | Jan Dlugosz | artist / 2 | 262: Krakow | 1455.1.1 — 1480.1.1 | inherited / inherited | vanilla identical |
| 993 | Filip Callimachus | spymaster / 1 | 262: Krakow | 1468.1.1 — 1497.1.1 | tuscan / catholic | vanilla identical |
| 994 | Nil Sorsky | theologian / 3 | 295: Moskva | 1473.1.1 — 1508.1.1 | inherited / inherited | RIP changed |
| 995 | Fioravanti | artist / 2 | 295: Moskva | 1475.1.1 — 1486.1.1 | romagnan / catholic | vanilla identical |
| 996 | Wojciech z Brudzewa | natural_scientist / 1 | 262: Krakow | 1475.1.1 — 1497.1.1 | inherited / inherited | vanilla identical |
| 997 | Wit Stwosz | artist / 2 | 262: Krakow | 1477.1.1 — 1533.9.20 | swabian / catholic | vanilla identical |
| 998 | Andrzej Boryszewski | theologian / 1 | 254: Poznan | 1480.1.1 — 1510.1.1 | inherited / inherited | vanilla identical |
| 999 | Jan Laski | statesman / 2 | 262: Krakow | 1490.1.1 — 1531.5.19 | inherited / inherited | vanilla identical |
| 1000 | F. Jagiellonczyk | theologian / 2 | 262: Krakow | 1493.1.1 — 1503.1.1 | inherited / inherited | vanilla identical |
| 1001 | Jan F. Tarnowski | statesman / 1 | 259: Sandomierz | 1494.1.1 — 1507.1.1 | inherited / inherited | vanilla identical |
| 1002 | Jan Boner | treasurer / 2 | 262: Krakow | 1500.1.1 — 1523.1.1 | burgundian / catholic | vanilla identical |
| 1003 | Vassian Patrikeyev | statesman / 2 | 295: Moskva | 1503.1.1 — 1540.1.1 | inherited / inherited | vanilla identical |
| 1004 | Nicolaus Copernicus | natural_scientist / 3 | 257: Warszawa | 1504.1.1 — 1543.5.24 | prussian / catholic | vanilla identical |
| 1005 | Piotr Tomicki | diplomat / 1 | 262: Krakow | 1506.1.1 — 1535.1.1 | inherited / inherited | vanilla identical |
| 1006 | Hans Dürer | artist / 1 | 262: Krakow | 1515.1.1 — 1538.1.1 | franconian / catholic | vanilla identical |
| 1007 | Maksim Grek | theologian / 1 | 295: Moskva | 1515.1.1 — 1556.1.1 | greek / orthodox | vanilla identical |
| 1008 | Bartolomeo Berecci | artist / 2 | 262: Krakow | 1516.1.1 — 1537.1.1 | tuscan / catholic | vanilla identical |
| 1009 | Seweryn Boner | treasurer / 1 | 262: Krakow | 1520.1.1 — 1549.1.1 | burgundian / catholic | vanilla identical |
| 1010 | Iosif Volotsky | theologian / 2 | 295: Moskva | 1470.1.1 — 1515.9.9 | inherited / inherited | vanilla identical |
| 1011 | Qolsärif | artist / 1 | 1082: Kazan | 1530.1.1 — 1552.1.1 | inherited / inherited | vanilla identical |
| 1012 | Francesco Lismanini | theologian / 2 | 258: Lodz | 1534.1.1 — 1566.4.1 | greek / reformed | vanilla identical |
| 1013 | Metropolitan Philip | theologian / 1 | 295: Moskva | 1537.12.12 — 1569.12.12 | inherited / inherited | vanilla identical |
| 1014 | Waclaw z Szamotul | artist / 1 | 254: Poznan | 1538.1.1 — 1560.1.1 | inherited / inherited | vanilla identical |
| 1015 | S. Orzechowski | artist / 2 | 260: Lublin | 1540.1.1 — 1566.1.1 | inherited / inherited | vanilla identical |
| 1016 | Andrzej Modrzewski | philosopher / 2 | 254: Poznan | 1541.1.1 — 1572.1.1 | inherited / inherited | vanilla identical |
| 1017 | Qosçaq | statesman / 2 | 1082: Kazan | 1546.1.1 — 1551.1.1 | inherited / inherited | vanilla identical |
| 1018 | Aleksandr Gorbaty-Shuisky | colonial_governor / 2 | 307: Vladimir | 1544.1.1 — 1566.1.1 | inherited / inherited | vanilla identical |
| 1019 | Nikita Zakharyin-Yuryev | statesman / 2 | 295: Moskva | 1547.1.1 — 1586.4.23 | inherited / inherited | vanilla identical |
| 1020 | Konstanty Ostrohski | statesman / 1 | 279: Volhynia | 1556.1.1 — 1608.1.1 | ruthenian / orthodox | RIP changed |
| 1021 | Jan Laski | theologian / 2 | 257: Warszawa | 1556.1.1 — 1560.1.1 | inherited / reformed | vanilla identical |
| 1022 | Giorgio Biandrata | natural_scientist / 1 | 257: Warszawa | 1558.1.1 — 1588.5.5 | piedmontese / catholic | vanilla identical |
| 1023 | Andrei Kurbsky | statesman / 2 | 308: Yaroslavl | 1558.1.1 — 1583.1.1 | inherited / inherited | vanilla identical |
| 1024 | Ivan Fedorov | trader / 1 | 2961: Lwow | 1564.3.1 — 1583.12.14 | ruthenian / orthodox | RIP changed |
| 1025 | Pyotr Mstislavets | trader / 1 | 293: Smolensk | 1564.3.1 — 1576.1.1 | byelorussian / inherited | RIP changed |
| 1026 | Malyuta Skuratov | spymaster / 3 | 295: Moskva | 1569.1.1 — 1573.1.1 | inherited / inherited | vanilla identical |
| 1027 | Bogdan Belsky | statesman / 1 | 295: Moskva | 1571.1.1 — 1611.1.1 | inherited / inherited | vanilla identical |
| 1028 | Jan Zamoyski | statesman / 3 | 257: Warszawa | 1572.3.1 — 1605.1.1 | inherited / inherited | vanilla identical |
| 1029 | Patriarch Iov | theologian / 2 | 295: Moskva | 1575.1.1 — 1607.6.19 | inherited / inherited | vanilla identical |
| 1030 | Piotr Poweski | philosopher / 1 | 257: Warszawa | 1579.1.1 — 1612.9.27 | inherited / inherited | vanilla identical |
| 1031 | Lew Sapieha | statesman / 2 | 272: Lithuania | 1589.1.1 — 1633.1.1 | inherited / inherited | vanilla identical |
| 1032 | Dionysius II | theologian / 1 | 295: Moskva | 1581.1.1 — 1591.1.1 | inherited / inherited | vanilla identical |
| 1033 | Patriarch Ignatius | spymaster / 1 | 301: Ryazan | 1595.1.1 — 1620.1.1 | inherited / inherited | vanilla identical |
| 1034 | Adam Wisniowiecki | spymaster / 1 | 257: Warszawa | 1596.1.1 — 1622.1.1 | inherited / inherited | vanilla identical |
| 1035 | Michal Wisniowiecki | statesman / 1 | 257: Warszawa | 1600.1.1 — 1616.1.1 | inherited / inherited | vanilla identical |
| 1036 | Rafal Leszczynski | trader / 2 | 258: Lodz | 1619.1.1 — 1636.3.29 | inherited / inherited | vanilla identical |
| 1037 | Patriarch Filaret | statesman / 3 | 295: Moskva | 1619.6.2 — 1633.10.1 | inherited / inherited | vanilla identical |
| 1038 | Boris Morozov | treasurer / 1 | 295: Moskva | 1620.1.1 — 1661.1.1 | inherited / inherited | vanilla identical |
| 1039 | Szymon Starowolski | philosopher / 1 | 262: Krakow | 1621.1.1 — 1650.1.1 | inherited / inherited | vanilla identical |
| 1040 | Epifany Slavinetsky | theologian / 2 | 280: Kiev | 1630.1.1 — 1675.1.1 | ruthenian / orthodox | RIP changed |
| 1041 | Patriarch Nikon | theologian / 3 | 306: Nijni-Novgorod | 1635.1.1 — 1681.8.17 | inherited / inherited | vanilla identical |
| 1042 | Ordin-Nashchokin | statesman / 3 | 274: Pskov | 1642.1.1 — 1680.1.1 | inherited / inherited | vanilla identical |
| 1043 | Fyodor Rtishchev | treasurer / 1 | 295: Moskva | 1650.1.1 — 1673.1.1 | inherited / inherited | vanilla identical |
| 1044 | Artamon Matveev | diplomat / 2 | 295: Moskva | 1654.1.1 — 1682.1.1 | inherited / inherited | vanilla identical |
| 1045 | Patriarch Adrian | theologian / 1 | 295: Moskva | 1657.10.2 — 1700.10.16 | inherited / inherited | vanilla identical |
| 1046 | Vasily Golitsyn | army_reformer / 2 | 295: Moskva | 1673.1.1 — 1714.4.21 | inherited / inherited | vanilla identical |
| 1047 | Boris Golitsyn | statesman / 1 | 295: Moskva | 1684.1.1 — 1714.1.1 | inherited / inherited | vanilla identical |
| 1048 | Dmitriy Golitsyn | statesman / 1 | 295: Moskva | 1695.1.1 — 1737.4.14 | inherited / inherited | vanilla identical |
| 1049 | Cornelius Cruys | naval_reformer / 3 | 295: Moskva | 1698.1.1 — 1727.1.1 | inherited / inherited | vanilla identical |
| 1050 | Aleksandr Menshikov | statesman / 2 | 295: Moskva | 1699.1.1 — 1727.5.17 | inherited / inherited | vanilla identical |
| 1051 | Pyotr Shafirov | diplomat / 3 | 295: Moskva | 1700.1.1 — 1739.1.1 | inherited / inherited | vanilla identical |
| 1052 | Vasily Dolgorukov | statesman / 2 | 310: Novgorod | 1702.1.1 — 1739.11.8 | inherited / inherited | vanilla identical |
| 1053 | Lestocq | natural_scientist / 1 | 33: Neva | 1709.1.1 — 1767.6.12 | cosmopolitan_french / catholic | vanilla identical |
| 1054 | Theophan Prokopovich | theologian / 2 | 280: Kiev | 1709.1.1 — 1736.9.19 | ruthenian / orthodox | RIP changed |
| 1055 | Anikita Repnin | statesman / 2 | 295: Moskva | 1710.1.1 — 1726.6.3 | inherited / inherited | vanilla identical |
| 1056 | Ph. von Strahlenberg | natural_scientist / 1 | 1074: Sibir | 1711.1.1 — 1747.1.1 | swedish / protestant | vanilla identical |
| 1057 | Vasily Tatishchev | natural_scientist / 2 | 274: Pskov | 1716.1.1 — 1750.7.15 | inherited / inherited | vanilla identical |
| 1058 | Andrei Osterman | statesman / 2 | 295: Moskva | 1716.6.19 — 1747.5.31 | hessian / catholic | vanilla identical |
| 1059 | António de Vieira | statesman / 2 | 33: Neva | 1718.1.1 — 1745.1.1 | portugese / jewish | vanilla identical |
| 1060 | Artemy Volynsky | colonial_governor / 2 | 295: Moskva | 1719.1.1 — 1740.1.1 | inherited / inherited | vanilla identical |
| 1061 | Aleksandr Buturlin | statesman / 1 | 313: Soroka | 1720.1.1 — 1767.8.30 | inherited / inherited | vanilla identical |
| 1062 | Aleksei Bestuzhev-Ryumin | diplomat / 2 | 295: Moskva | 1730.1.1 — 1768.4.21 | inherited / inherited | vanilla identical |
| 1063 | Bartolomeo Rastrelli | artist / 2 | 33: Neva | 1730.1.1 — 1771.1.1 | inherited / inherited | vanilla identical |
| 1064 | Alexei Razumovsky | statesman / 1 | 289: Chernigov | 1732.1.1 — 1771.7.6 | ruthenian / inherited | RIP changed |
| 1065 | Burkhard von Münnich | army_reformer / 2 | 33: Neva | 1732.1.1 — 1767.10.16 | hessian / protestant | vanilla identical |
| 1066 | Aleksandr Shuvalov | spymaster / 2 | 313: Soroka | 1740.1.1 — 1771.1.1 | inherited / inherited | vanilla identical |
| 1067 | Pyotr Shuvalov | treasurer / 1 | 313: Soroka | 1741.1.1 — 1762.1.1 | inherited / inherited | vanilla identical |
| 1068 | Mikhail Vorontsov | statesman / 2 | 295: Moskva | 1741.12.6 — 1767.1.1 | inherited / inherited | vanilla identical |
| 1069 | Mikhail Lomonosov | natural_scientist / 3 | 313: Soroka | 1743.1.1 — 1765.4.15 | inherited / inherited | vanilla identical |
| 1070 | Nikita Panin | diplomat / 2 | 295: Moskva | 1748.1.1 — 1783.3.31 | inherited / inherited | vanilla identical |
| 1071 | Ivan Shuvalov | treasurer / 2 | 295: Moskva | 1749.6.1 — 1797.11.14 | inherited / inherited | vanilla identical |
| 1072 | Kirill Razumovsky | statesman / 1 | 289: Chernigov | 1750.1.1 — 1803.1.1 | ruthenian / inherited | RIP changed |
| 1073 | Dmitry Mikhailovich | diplomat / 1 | 33: Neva | 1751.1.1 — 1793.1.1 | inherited / inherited | vanilla identical |
| 1074 | Fyodor Volkov | artist / 1 | 308: Yaroslavl | 1752.1.1 — 1763.1.1 | inherited / inherited | vanilla identical |
| 1075 | Ivan Dmitrievsky | artist / 1 | 308: Yaroslavl | 1752.1.1 — 1821.1.1 | inherited / inherited | vanilla identical |
| 1076 | Grigory Orlov | statesman / 2 | 310: Novgorod | 1762.1.1 — 1783.1.1 | inherited / inherited | vanilla identical |
| 1077 | Grigory Potemkin | statesman / 3 | 293: Smolensk | 1762.1.1 — 1791.10.5 | inherited / inherited | vanilla identical |
| 1078 | Fyodor Rokotov | artist / 1 | 289: Chernigov | 1766.1.1 — 1809.1.1 | inherited / inherited | vanilla identical |
| 1079 | Caspar F. Wolff | natural_scientist / 2 | 33: Neva | 1767.1.1 — 1794.2.22 | saxon / protestant | vanilla identical |
| 1080 | Fedot Shubin | artist / 2 | 313: Soroka | 1770.1.1 — 1805.1.1 | inherited / inherited | vanilla identical |
| 1081 | Tommaso Traetta | artist / 1 | 307: Vladimir | 1772.1.1 — 1779.4.6 | neapolitan / catholic | vanilla identical |
| 1082 | Poniatowski | statesman / 1 | 256: Plock | 1776.1.1 — 1794.1.1 | inherited / inherited | vanilla identical |
| 1083 | Vasily Kapnist | artist / 1 | 280: Kiev | 1788.2.23 — 1823.11.9 | ruthenian / inherited | RIP changed |
| 1084 | Platon Zubov | statesman / 3 | 307: Vladimir | 1789.1.1 — 1822.1.1 | inherited / inherited | vanilla identical |
| 1085 | Karl Nesselrode | diplomat / 2 | 295: Moskva | 1807.1.1 — 1862.3.23 | prussian / protestant | vanilla identical |
| 15601 | Dmytro Vyshnevetsky | army_reformer / 3 | 283: Zaporozhia | 1550.1.1 — 1563.1.1 | ruthenian / inherited | RIP addition |
| 15602 | Severyn Nalyvaiko | army_reformer / 2 | 283: Zaporozhia | 1594.1.1 — 1597.4.1 | ruthenian / inherited | RIP addition |
| 15603 | Bohdan Khmelnytsky | statesman / 3 | 290: Poltava | 1648.1.1 — 1657.8.6 | ruthenian / inherited | RIP addition |
| 15604 | Ivan Vyhovsky | diplomat / 3 | 290: Poltava | 1648.1.1 — 1664.1.1 | ruthenian / inherited | RIP addition |
| 15605 | Ivan Sirko | army_reformer / 3 | 283: Zaporozhia | 1660.1.1 — 1680.8.11 | ruthenian / inherited | RIP addition |
| 15606 | Petro Doroshenko | statesman / 2 | 289: Chernigov | 1665.1.1 — 1698.11.19 | ruthenian / inherited | RIP addition |
| 15607 | Ivan Mazepa | statesman / 3 | 290: Poltava | 1687.1.1 — 1709.9.21 | ruthenian / inherited | RIP addition |
| 15608 | Pylyp Orlyk | philosopher / 2 | 283: Zaporozhia | 1710.1.1 — 1742.5.24 | ruthenian / inherited | RIP addition |
| 15609 | Petro Kalnyshevsky | statesman / 2 | 283: Zaporozhia | 1762.1.1 — 1803.1.1 | ruthenian / inherited | RIP addition |
| 15610 | Hryhorii Poletyka | philosopher / 2 | 290: Poltava | 1760.1.1 — 1784.1.1 | ruthenian / inherited | RIP addition |
| 15611 | Hryhorii Bolharynovych | theologian / 2 | 280: Kiev | 1458.1.1 — 1473.1.1 | ruthenian / orthodox | RIP addition |
| 15612 | Mykhailo Olelkovych | statesman / 2 | 280: Kiev | 1470.1.1 — 1481.8.30 | ruthenian / orthodox | RIP addition |
| 15613 | Yurii Drohobych | natural_scientist / 3 | 4541: Drohobycz | 1478.1.1 — 1494.2.4 | ruthenian / catholic | RIP addition |
| 15614 | Shvaipolt Fiol | artist / 2 | 262: Krakow | 1483.1.1 — 1525.5.16 | franconian / catholic | RIP addition |
| 15615 | Vasyl Shemiachych | statesman / 2 | 1945: Novgorod-Seversky | 1495.1.1 — 1529.5.1 | ruthenian / orthodox | RIP addition |
| 15616 | Kostiantyn Ostrozky | grand_captain / 3 | 279: Volhynia | 1497.1.1 — 1530.8.8 | ruthenian / orthodox | RIP addition |
| 15617 | Mykhailo Hlynsky | commandant / 2 | 1941: Turov | 1498.1.1 — 1534.9.15 | ruthenian / orthodox | RIP addition |
| 15618 | Ostafii Dashkevych | fortification_expert / 2 | 1944: Cherkasy | 1514.1.1 — 1536.1.1 | ruthenian / orthodox | RIP addition |
| 15619 | Predslav Liantskoronsky | commandant / 2 | 281: Kamienec | 1516.1.1 — 1531.6.12 | ruthenian / catholic | RIP addition |
| 15620 | Francysk Skaryna | philosopher / 3 | 275: Polotsk | 1517.8.6 — 1551.1.29 | byelorussian / orthodox | RIP addition |
| 15621 | Mykola Husovsky | artist / 2 | 276: Minsk | 1522.1.1 — 1533.1.1 | byelorussian / catholic | RIP addition |
| 15622 | Bernard Pretwicz | fortification_expert / 2 | 1943: Bratslav | 1540.1.1 — 1563.1.1 | schlesian / catholic | RIP addition |
| 15623 | Mykhailo Vorotynsky | fortification_expert / 3 | 4116: Upper Oka | 1552.1.1 — 1573.6.12 | ruthenian / orthodox | RIP addition |
| 15624 | Ostafii Volovych | statesman / 2 | 277: Brest | 1561.1.1 — 1587.1.20 | byelorussian / reformed | RIP addition |
| 15625 | Symon Budny | theologian / 2 | 4537: Nowogrodek | 1562.1.1 — 1593.1.13 | byelorussian / reformed | RIP addition |
| 15626 | Hedeon Balaban | theologian / 2 | 2961: Lwow | 1569.1.1 — 1607.2.10 | ruthenian / orthodox | RIP addition |
| 15627 | Herasym Smotrytsky | philosopher / 2 | 2962: Rowne | 1576.1.1 — 1594.10.12 | ruthenian / orthodox | RIP addition |
| 15628 | Ivan Vyshensky | theologian / 2 | 261: Halicz | 1588.1.1 — 1620.1.1 | ruthenian / orthodox | RIP addition |
| 15629 | Ipatii Potii | theologian / 2 | 277: Brest | 1596.10.9 — 1613.7.18 | ruthenian / greek_catholic | RIP addition |
| 15630 | Yelysei Pletenetsky | artist / 2 | 280: Kiev | 1599.1.1 — 1624.10.29 | ruthenian / orthodox | RIP addition |
| 15631 | Petro Sahaidachny | grand_captain / 3 | 280: Kiev | 1606.1.1 — 1622.4.20 | ruthenian / orthodox | RIP addition |
| 15632 | Meletii Smotrytsky | philosopher / 3 | 2962: Rowne | 1610.1.1 — 1633.12.27 | ruthenian / orthodox | RIP addition |
| 15633 | Yosyf Veliamyn Rutsky | theologian / 2 | 4537: Nowogrodek | 1613.7.18 — 1637.2.5 | byelorussian / greek_catholic | RIP addition |
| 15634 | Petro Mohyla | theologian / 3 | 280: Kiev | 1627.1.1 — 1647.1.1 | ruthenian / orthodox | RIP addition |
| 15635 | Adam Kysil | diplomat / 2 | 279: Volhynia | 1630.1.1 — 1653.5.3 | ruthenian / orthodox | RIP addition |
| 15636 | Vasyl Tarasovych | theologian / 2 | 1952: Maramaros | 1634.1.1 — 1651.1.1 | rusyn / greek_catholic | RIP addition |
| 15637 | Inokentii Gizel | philosopher / 2 | 280: Kiev | 1646.1.1 — 1683.11.18 | ruthenian / orthodox | RIP addition |
| 15638 | Yurii Nemyrych | statesman / 3 | 1942: Zhytomyr | 1648.1.1 — 1659.8.1 | ruthenian / orthodox | RIP addition |
| 15639 | Avvakum Petrov | theologian / 3 | 306: Nijni-Novgorod | 1653.1.1 — 1682.4.14 | russian / old_believer | RIP addition |
| 15640 | Herasym Kondratiev | colonial_governor / 2 | 299: Voronezh | 1655.1.1 — 1701.1.1 | ruthenian / orthodox | RIP addition |
| 15641 | Lazar Baranovych | theologian / 2 | 289: Chernigov | 1657.3.8 — 1693.9.3 | ruthenian / orthodox | RIP addition |
| 15642 | Hryhorii Donets | fortification_expert / 2 | 291: Kharkov | 1668.1.1 — 1691.1.1 | ruthenian / orthodox | RIP addition |
| 15643 | Dmytro Tuptalo | theologian / 3 | 1945: Novgorod-Seversky | 1684.1.1 — 1709.10.28 | ruthenian / orthodox | RIP addition |
| 15644 | Samiilo Velychko | artist / 2 | 290: Poltava | 1690.1.1 — 1728.1.1 | ruthenian / orthodox | RIP addition |
| 15645 | Fedir Chuikevych | statesman / 2 | 4542: Lubnie | 1730.1.1 — 1764.1.1 | ruthenian / orthodox | RIP addition |
| 15646 | Manuil Olshavsky | theologian / 2 | 1952: Maramaros | 1743.1.1 — 1767.11.5 | rusyn / greek_catholic | RIP addition |
| 15647 | Ivan Hryhorovych-Barsky | artist / 2 | 280: Kiev | 1748.1.1 — 1791.9.10 | ruthenian / orthodox | RIP addition |
| 15648 | Hryhorii Skovoroda | philosopher / 3 | 291: Kharkov | 1753.1.1 — 1794.11.9 | ruthenian / orthodox | RIP addition |
| 15649 | Paisii Velychkovsky | theologian / 3 | 290: Poltava | 1754.1.1 — 1794.11.15 | ruthenian / orthodox | RIP addition |
| 15650 | Andrii Bachynsky | statesman / 3 | 1952: Maramaros | 1772.1.1 — 1809.11.19 | rusyn / greek_catholic | RIP addition |
| 15651 | Dmytro Bortniansky | artist / 3 | 289: Chernigov | 1779.1.1 — 1825.10.10 | ruthenian / orthodox | RIP addition |
| 15652 | Yosyp de Ribas | naval_reformer / 2 | 282: Yedisan | 1789.9.14 — 1800.12.2 | neapolitan / catholic | RIP addition |
| 15653 | Ivan Kotliarevsky | artist / 2 | 290: Poltava | 1798.1.1 — 1838.11.10 | ruthenian / orthodox | RIP addition |
| 15654 | Vasyl Karazin | natural_scientist / 3 | 291: Kharkov | 1802.1.1 — 1842.11.16 | ruthenian / orthodox | RIP addition |
