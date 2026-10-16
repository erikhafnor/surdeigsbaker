# Printliste – Surdeigsbaker v0

Generert av `hardware/cad/bygg.py`. STL-filene ligger i [`stl/`](stl/) og er allerede snudd til anbefalt printretning.

**Standardinnstillinger:** PETG, 0,2 mm lag, 4 perimetre, 30–40 % gyroid, 5 topp- og bunnlag. Bærende deler (lagerhus, motorplate, motorklemme og hengsler) skal ha **5 perimetre** og 40 % fyll. TPU-deler: 95A, 100 % fyll.

Ingen printede deler er i kontakt med deigen. Bollen og kroken er av rustfritt stål.

| Del | Antall | Materiale | Printretning | Volum (cm³) | Merknad |
|---|---|---|---|---|---|
| [hengsel_ramme](stl/hengsel_ramme.stl) | 2 | PETG | monteringsflaten ned | 18.0 | M6 × 45 hengselbolt med låsemutter. Venstre og høyre er like. |
| [hengsel_lokk](stl/hengsel_lokk.stl) | 2 | PETG | monteringsflaten ned | 13.2 |  |
| [lagerhus](stl/lagerhus.stl) | 1 | PETG | som modellert | 92.9 | 2 × 6000-2RS presses inn, ett fra hver side. Bruk 5 perimetre. |
| [motorplate](stl/motorplate.stl) | 1 | PETG | som modellert | 327.8 | 5 perimetre, 40 % gyroid |
| [motorklemme](stl/motorklemme.stl) | 1 | PETG | flensen ned | 116.8 | Indre ⌀ = motor.kropp_d + 0,6. Legg 1 mm gummi rundt motoren. |
| [motordeksel](stl/motordeksel.stl) | 1 | PETG | toppen ned | 110.5 |  |
| [kantpress_hus](stl/kantpress_hus.stl) | 3 | PETG | flensen ned | 16.1 |  |
| [kantpress_stempel](stl/kantpress_stempel.stl) | 3 | PETG | stående | 1.7 |  |
| [kantpress_tupp](stl/kantpress_tupp.stl) | 3 | TPU 95A | som modellert | 1.0 | Myk tupp som klemmer bollekanten. Kan erstattes med kjøpt silikonfot. |
| [sensorhus](stl/sensorhus.stl) | 1 | PETG | toppen ned | 33.0 |  |
| [hjemmeflagg](stl/hjemmeflagg.stl) | 1 | PETG | som modellert | 4.0 |  |
| [sensorarm](stl/sensorarm.stl) | 1 | PETG | toppen ned | 6.1 |  |
| [varmeplateholder](stl/varmeplateholder.stl) | 1 | PETG | som modellert | 45.6 | Holder aluminiumsplaten. Temperaturen holdes ≤ 45 °C, termostaten bryter ved 60 °C. |
| [bollestotte](stl/bollestotte.stl) | 2 | PETG | toppen ned | 132.6 | Silikonsnor ⌀3 mm i sporet gir friksjon mot bollen. |
| [bollestotte_foler](stl/bollestotte_foler.stl) | 1 | PETG | toppen ned | 130.5 | Med kanal for DS18B20-føleren som ligger mot bolleveggen. |
| [elektronikkplate](stl/elektronikkplate.stl) | 1 | PETG | som modellert | 150.1 |  |
| [plateholder_hoyre](stl/plateholder_hoyre.stl) | 1 | PETG | veggen ned | 43.8 |  |
| [plateholder_venstre](stl/plateholder_venstre.stl) | 1 | PETG | veggen ned | 43.8 |  |
| [kontrollpanel](stl/kontrollpanel.stl) | 1 | PETG | frontflaten ned | 48.6 |  |
| [bakpanelinnsats](stl/bakpanelinnsats.stl) | 1 | PETG | utsiden ned | 36.1 |  |
| [romfolerhus](stl/romfolerhus.stl) | 1 | PETG | som modellert | 4.8 |  |
| [fot](stl/fot.stl) | 4 | PETG + gummipute | som modellert | 6.2 |  |
| [bryterholder](stl/bryterholder.stl) | 1 | PETG | baksiden ned | 5.8 |  |
| [bryternese](stl/bryternese.stl) | 1 | PETG | baksiden ned | 7.4 |  |
| [styrekile](stl/styrekile.stl) | 2 | PETG | liggende | 0.9 |  |
| [kabelklemme](stl/kabelklemme.stl) | 6 | PETG | som modellert | 1.2 |  |
| [vinkel_2020](stl/vinkel_2020.stl) | 0 | PETG | som modellert | 4.7 | Valgfri. Kjøpte hjørnebeslag i aluminium anbefales (32 stk). |

Delene med antall 0 er valgfrie.
