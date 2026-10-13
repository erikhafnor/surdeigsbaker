# 09 – Budsjett og handleliste

> Prisene er **grove anslag i NOK** (oktober 2026), basert på typiske priser for hobbykomponenter og bruktmarkedet. Sjekk dagens priser før du bestiller. Mye kan kjøpes brukt (Finn.no), og noe har du kanskje allerede. Legg inn ca. **30 % buffer** for feilkjøp og nye iterasjoner.

## Sammendrag

| Fase | Innhold | Anslag (kr) |
|---|---|---|
| 0 | Måleverktøy for referansebrød | 1 450–3 850 (650–1 350 uten pH-meter) |
| 1 | Måleoppsett og hevekasse | 3 300–7 350 (inkl. valgfri CO₂-sensor) |
| 2 | Gangbart skjelett (brødmaskin) | 1 450–3 400 |
| 3–4 | Prototype v1 | 6 900–19 000 |
| **Totalt** | | **ca. 13 000–34 000** |

## Fase 0 – måleverktøy (kjøp nå)

| Vare | Til | Anslag (kr) |
|---|---|---|
| Presisjonsvekt 0,1 g (opptil 500 g) | Salt, surdeig, levain | 150–300 |
| Raskt stikktermometer | Deig, vann, kjernetemperatur | 200–500 |
| Smale, graderte glass (aliquot jar) og glass til surdeig | Bulkheving og levain | 100–150 |
| Energimåler for stikkontakt | Energi per baking (E08, E13) | 150–300 |
| Hirse- eller rapsfrø | Volummåling med frøfortrengning | 50–100 |
| *Valgfritt:* pH-meter med stikkelektrode for mat | pH i levain, deig og krumme | 800–2 500 |

Har allerede (antagelig): kjøkkenvekt (1 g), jerngryte, hevekurv, bakeskraper og kjøkkenmaskin.

## Fase 1 – måleoppsett og hevekasse

| Vare | Til | Anslag (kr) |
|---|---|---|
| ESP32-S3-utviklingskort × 2 | Måleoppsett og hevekasse ([ADR-002](beslutninger/ADR-002-plattform-maaleoppsett.md)) | 300–500 |
| ToF-sensorer: VL6180X × 2 (glass) og VL53L1X × 1 (bolle) | Hevekurver (E02, E14) | 300–600 |
| DS18B20 vanntette temperaturfølere × 5 | Deig, vann og kammer | 150–250 |
| SHT4x romklimasensor | Romtemperatur og luftfuktighet | 100–200 |
| Lastcelle 5 kg og NAU7802- eller HX711-forsterker | Vekt og dosering | 100–200 |
| Koblingsbrett, ledninger, kontakter og koblingsboks | | 150–300 |
| Sous vide-pinne og kasse | Vannbad med stabil temperatur (E02) | 600–1 200 |
| Brukt lite vinkjøleskap med **kompressor** (Finn) | Hevekasse med kjøling ([arkitektur, avsnitt 4](07-arkitektur.md#4-termikk-grove-tall)) | 500–1 500 |
| Varmekilde (varmekabel eller PTC-element) og SSR eller relé for styring | Varme i hevekassen | 300–600 |
| Sertifisert strømforsyning (5 V/12 V) og bærbar jordfeilbryter | Sikkerhet | 300–500 |
| *Valgfritt:* CO₂-sensor for høye nivåer (STC31 eller SprintIR) | E03 | 500–1 500 |

> **Sikkerhet:** Vinkjøleskapet skal ikke bygges om på 230 V-siden. Styr det eksternt med en sertifisert smartplugg eller et relé i egen godkjent boks, slik BrewPi-oppsett gjør. Selve kjølekretsen skal du ikke åpne.

## Fase 2 – gangbart skjelett

| Vare | Anslag (kr) |
|---|---|
| Brukt brødmaskin (Finn) | 200–600 |
| Nullgjennomgangs-SSR med kjøleribbe | 150–300 |
| Topolet relé eller kontaktor (sikkerhetsfrakobling) | 150–400 |
| Termosikring (engangs) og termostat med manuell tilbakestilling | 100–300 |
| PT1000 og MAX31865 | 200–400 |
| Styring av AC-motor (relé, triac-modul eller ny girmotor) | 200–400 |
| Sertifisert strømforsyning og apparatinntak | 150–300 |
| Høytemperaturledning (silikon eller PTFE), kabelsko og strekkavlastning | 100–300 |
| Kabinett eller koblingsboks for elektronikken | 200–400 |

## Fase 3–4 – prototype v1 (grovt)

| Delsystem | Innhold | Anslag (kr) |
|---|---|---|
| Gryte | 24 cm emaljert jerngryte eller lettere gryte av karbonstål (du har kanskje allerede en) | 0–2 500 |
| Stekemodul | Varmeelementer, steinull eller AES-ull, plater og sikringer | 800–2 000 |
| Kjøling av bollen | Kompressorenhet eller Peltier-sett med kjøleribber og vifter | 800–2 500 |
| Elte- og hevemodul | Bolle i rustfritt stål, krok, girmotor (100–200 W) og driver | 1 000–2 500 |
| Aktuatorer | Steppere eller lineæraktuatorer til vipp og lokk, endebrytere | 500–1 500 |
| Dosering (N3) | Melsnegle med omrører, to peristaltiske pumper og tank | 800–2 000 |
| Ramme og kabinett | Aluminiumsprofiler, platearbeid og festemidler | 1 000–2 500 |
| Elektronikk | Raspberry Pi, MCU-kort, sikkerhetsvakt og eventuelt eget kretskort | 1 000–2 000 |
| Diverse | Ledninger, kontakter, matgodkjent silikon og skruer | 1 000–1 500 |

## Verktøy og tilgang

Disse trenger du ikke eie, men du trenger tilgang til dem:

- 3D-skriver (bare for deler utenfor matkontakt og varmesoner)
- Loddestasjon og multimeter
- Bor og gjengeverktøy
- Gjerne et makerspace med platebearbeiding

## Innkjøpsrutine

1. Kjøp bare det **neste fase** trenger. Planen vil endre seg underveis.
2. Hver bestilling noteres i `hardware/innkjop.csv` (opprettes ved første kjøp) med dato, vare, leverandør, pris og hvilket delsystem den hører til. Det blir grunnlaget for stykklisten (BOM) til DIY-versjonen.
