# Sjekkrapport – Surdeigsbaker v0

Generert automatisk av `hardware/cad/bygg.py` fra `hardware/spec/v0.yaml`. Ikke rediger for hånd.

## 1. Passer delene på printeren?

Byggevolum: 250 × 210 × 220 mm (delene kan dreies 90° på platen).

| Del | Mål i printretning (mm) | OK |
|---|---|---|
| hengsel_ramme | 40 × 29 × 43 | ✅ |
| hengsel_lokk | 40 × 29 × 29 | ✅ |
| lagerhus | 80 × 44 × 30 | ✅ |
| motorplate | 110 × 160 × 20 | ✅ |
| motorklemme | 98 × 110 × 40 | ✅ |
| motordeksel | 83 × 83 × 160 | ✅ |
| kantpress_hus | 56 × 20 × 40 | ✅ |
| kantpress_stempel | 10 × 10 × 32 | ✅ |
| kantpress_tupp | 14 × 14 × 8 | ✅ |
| sensorhus | 44 × 44 × 20 | ✅ |
| hjemmeflagg | 43 × 22 × 10 | ✅ |
| sensorarm | 24 × 44 × 32 | ✅ |
| varmeplateholder | 177 × 153 × 16 | ✅ |
| bollestotte | 63 × 76 × 75 | ✅ |
| bollestotte_foler | 81 × 40 × 75 | ✅ |
| elektronikkplate | 240 × 180 × 4 | ✅ |
| plateholder_hoyre | 24 × 170 × 45 | ✅ |
| plateholder_venstre | 24 × 170 × 45 | ✅ |
| kontrollpanel | 166 × 76 × 8 | ✅ |
| bakpanelinnsats | 132 × 66 × 8 | ✅ |
| romfolerhus | 30 × 32 × 16 | ✅ |
| fot | 30 × 30 × 10 | ✅ |
| bryterholder | 50 × 30 × 6 | ✅ |
| bryternese | 25 × 22 × 18 | ✅ |
| styrekile | 8 × 20 × 6 | ✅ |
| kabelklemme | 20 × 12 × 12 | ✅ |

**26 av 26 deler passer.**

## 2. Kroken i bollen

- Minste klaring mellom krok og bollevegg mens kroken roterer: **9.4 mm**
- Minste klaring mellom krok og bollebunn: **8.2 mm**
- Utbrettet lengde på krokstanga (senterlinje): **313 mm**. Kapp stanga til 350 mm.
- Modellen regner bollen som en rett kjegle. En ekte bolle har avrundet overgang mellom bunn og vegg, så **mål og sjekk klaringen med bollen din før du bøyer kroken**.

## 3. Lokket åpnes (0–100°)

Kroken parkeres med C-en mot hengselen (hjemmesensoren) før lokket åpnes.

- Minste klaring mot bollen under åpning: **3.9 mm** (kantpute, ved 3°)
- Kantputene er unntatt de første 3°, fordi de skal ligge mot bollekanten når lokket er lukket.

- Høyde med lukket lokk: **541 mm** over benken.
- Høyeste punkt under åpning: **694 mm** over benken. Bakerste punkt: **258 mm** bak maskinen.
- Høyere enn plassen under vanlige overskap: **trekk maskinen fram før du åpner lokket**, som med en kjøkkenmaskin.

- Hengselen stopper lokket ved ca. **104°**.

## 4. Effekt

- Verste tilfelle (motor + varme + elektronikk samtidig): **156 W** mot strømforsyningens **150 W**.
- Fastvaren slår av varmen mens motoren går, så det normale toppforbruket blir ca. motor + elektronikk.

## 5. Filament

- Massivt volum av alle printede deler: **1625 cm³**. Med vanlige innstillinger (4 perimetre, 30–40 % fyll) blir det ca. **1135 g PETG** pluss litt TPU.

