# Sjekkrapport – Surdeigsbaker v1

Generert automatisk av `hardware/cad/v1/bygg.py` fra `hardware/spec/v1.yaml`. Ikke rediger for hånd.

## 1. Passer delene på printeren?

Byggevolum: 250 × 210 × 220 mm (delene kan dreies 90° på platen).

| Del | Mål i printretning (mm) | OK |
|---|---|---|
| formholder | 140 × 129 × 35 | ✅ |
| lagersoyle | 80 × 80 × 35 | ✅ |
| kabelklemme | 24 × 12 × 9 | ✅ |
| krage | 88 × 88 × 32 | ✅ |
| trakt | 247 × 135 × 169 | ✅ |
| skruror | 85 × 48 × 48 | ✅ |
| fallror_mel | 52 × 52 × 29 | ✅ |
| melskrue | 28 × 28 × 155 | ✅ |
| tannhjul_skrue | 21 × 21 × 9 | ✅ |
| tannhjul_rorer | 57 × 57 × 9 | ✅ |
| melmotorfeste | 25 × 46 × 47 | ✅ |
| traktlokk | 242 × 136 × 26 | ✅ |
| saltboks | 97 × 59 × 169 | ✅ |
| saltlokk | 61 × 60 × 19 | ✅ |
| saltskrue | 9 × 9 × 90 | ✅ |
| fallror_salt | 26 × 26 × 29 | ✅ |
| takmodul | 180 × 160 × 23 | ✅ |
| klaff_mel | 38 × 60 × 3 | ✅ |
| klaff_salt | 16 × 52 × 3 | ✅ |
| varmekanal | 133 × 205 × 25 | ✅ |
| dorhengsel_ramme | 14 × 32 × 40 | ✅ |
| dorhengsel_dor | 54 × 14 × 40 | ✅ |
| dorhandtak | 16 × 70 × 28 | ✅ |
| bryternese | 18 × 20 × 10 | ✅ |
| bryterholder | 30 × 26 × 18 | ✅ |
| kontrollpanel | 110 × 100 × 6 | ✅ |
| bakpanelinnsats | 58 × 58 × 6 | ✅ |
| tankskuff | 114 × 103 × 169 | ✅ |
| elektronikkplate | 130 × 130 × 10 | ✅ |
| fot | 40 × 40 × 10 | ✅ |

**30 av 30 deler passer.**

## 2. Veiespalten

Alt som står på lastcella (plattformen, lagersøylen, formholderen, formen, akselen, reimskivene, reima og eltemotoren) skal gå fri av resten av maskinen. Ellers bærer noe av vekta seg selv, og doseringen blir feil.

- Minste spalte mellom det som veies og resten av maskinen: **4.0 mm** (formholder mot krage) ✅ (krav ≥ 3 mm)
- Minste spalte mellom det som veies og selve lastcella: **3.4 mm** (reim mot lastcelle)
- Overlaststoppene er satt **0.3 mm** under plattformen. Juster dem med følelermål etter montering.
- Ledningene til eltemotoren og deigføleren må henge i en myk sløyfe. Bruk tynne silikonledninger.

## 3. Formen tas ut

Formen dreies 15° for å løsne bajonetten, løftes 28 mm og trekkes ut gjennom døra (åpen 105°).

| Trinn | Minste klaring (mm) | Nærmest | Kollisjon med holderen (mm³) |
|---|---|---|---|
| dreie | 11.9 ✅ | vifte | 0.0 |
| løfte | 5.5 ✅ | klaff_salt | 0.0 |
| trekke | 5.5 ✅ | klaff_mel | – |

Knastene skal gli i sporene i holderen, så kollisjonen med holderen skal være 0.

## 4. Døra åpnes

- Minste klaring mellom døra og maskinen fra 5° til 105°: **0.4 mm** (panel_dor mot panel_hoyre, ved 5°) ✅
- Døra er hengslet på høyre side. Isolasjonspluggen i døra er skåret 2.7 mm skrått på venstre kant (innerst), ellers ville hjørnet gått inn i isolasjonen når døra åpnes.

## 5. Mel og salt

- Melbeholderen rommer **2.8 l**, dvs. ca. **1.5 kg** løst mel (0.55 g/cm³). Det er nok til 2 bakinger på 560 g.
- Innløpet langs skruen er 8.2 × skruediameteren (krav ≥ 4). Lukket rør før utløpet: 47 mm.
- Røreverket går **4.5 mm** fra skruen og **6.4 mm** fra veggene.
- Saltboksen rommer ca. **376 ml**, dvs. ca. 451 g fint salt (37 bakinger).

## 6. Deigen i formen

Formen rommer ca. 3.3 l. Deigen veier 1010 g (1.05 g/cm³).

| Heving | Deighøyde (mm) | Avstand ToF → deig (mm) |
|---|---|---|
| +0 % | 46 | 140 |
| +50 % | 68 | 118 |
| +75 % | 78 | 107 |
| +100 % | 90 | 96 |

VL53L0X måler 30–1 200 mm. Hele området er innenfor.

**Utløp og målepunkter, avstand innenfor formveggen ved kanten:**

| Punkt | Margin (mm) |
|---|---|
| fallrør mel | 8 ✅ |
| fallrør salt | 8 ✅ |
| vanndyse | 42 ✅ |
| ToF-punkt | 44 ✅ |
| IR-punkt | 38 ✅ |
| kamera | 54 ✅ |

## 7. Vekt og lastcelle

- Det som veies, uten deig: ca. **4.1 kg**. Med deig: ca. **5.1 kg** mot cellas **10 kg**.
- Tyngst: eltemotor 1.60 kg, plattform 1.18 kg, brodform 0.75 kg, formholder 0.14 kg.
- NAU7802 med 10 kg-celle gir ca. 0,02–0,08 g støy. Krypet etter 470 g vann er ca. 0,5 g. Maskinen tarer før hver tilsetning.

## 8. Reim

- Akseavstand 229.4 mm, 20 og 40 tenner (utveksling 2.0:1).
- Nødvendig lengde 610 mm. Valgt standardreim: **HTD 610-5M-15** (122 tenner). Motoren flyttes +0.0 mm i sporene for å stramme.

## 9. Effekt

- Verste tilfelle (alt på samtidig): **219 W** mot strømforsyningens **221 W**.
- Fastvaren slår av varmen og doseringen mens eltemotoren går. Da blir toppen ca. **131 W**.

## 10. Størrelse

- Kassa: **481 × 306 × 526 mm** (b × d × h, med føtter).
- Med håndtak, hengsler og lokkgrep: 492 × 334 × 540 mm.
- Melbeholderen fylles ovenfra. Står maskinen under et overskap, må den trekkes fram for å fylle mel.

## 11. Filament

- Massivt volum av alle printede deler: **1761 cm³**. Med vanlige innstillinger blir det ca. **1230 g PETG**.

