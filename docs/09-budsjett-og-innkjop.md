# 09 – Budsjett og handleliste

> Prisene er **grove anslag i NOK** (oktober 2026), basert på typiske priser for hobbykomponenter og bruktmarkedet. Sjekk dagens priser før du bestiller. Mye kan kjøpes brukt (Finn.no), og noe har du kanskje allerede. Legg inn ca. **30 % buffer** for feilkjøp og nye iterasjoner.

## Sammendrag

> **Oppdatert 2026-10-17:** v0 bygges ikke. Prosjektet går rett på prototype v1 ([ADR-010](beslutninger/ADR-010-v1-arkitektur.md)). Den fullstendige stykklisten med antall, spesifikasjon og søkeord ligger i [`hardware/v1/stykkliste.csv`](../hardware/v1/stykkliste.csv). Hevekabinettet (K3) og brødmaskinskjelettet (K1) er valgfrie, og kjøling trengs ikke ([ADR-007](beslutninger/ADR-007-ingen-kjoling.md)).

| Fase | Innhold | Anslag (kr) |
|---|---|---|
| 0 | Måleverktøy for referansebrød | 1 450–3 850 (650–1 350 uten pH-meter) |
| 1 | Måleoppsett for eksperimentene (uten hevekabinett) | 1 000–3 000 |
| **2** | **Prototype v1 ([stykkliste](../hardware/v1/stykkliste.csv))** | **ca. 17 800 + frakt og ca. 30 % buffer = 21 000–24 000** |
| 3–4 | Kalibrering, reservedeler og forbedringer (f.eks. kretskort) | 2 000–5 000 |
| **Totalt** | | **ca. 25 000–35 000** |

Fordi stekingen skjer i vanlig ovn ([ADR-006](beslutninger/ADR-006-steking-i-vanlig-ovn.md)) og den kalde hevingen i ditt eget kjøleskap ([ADR-007](beslutninger/ADR-007-ingen-kjoling.md)), trengs verken stekemodul, gryte, varmeelementer for høy temperatur eller kjøling.

## Fase 2 – prototype v1 (kjøp nå)

Fra [`hardware/v1/stykkliste.csv`](../hardware/v1/stykkliste.csv):

| Gruppe | Ca. pris (kr) |
|---|---|
| Ramme: 2020-profiler, ACM-plater og aluminiumsplater kappet etter DXF, XPS, dørpakning | 4 600 |
| Form og drivverk: brukt Panasonic-brødmaskin (giver), girmotor 120 W, reimskiver og reim, aksel, lager, lastcelle | 3 000 |
| Dosering: steppere, rustfrie aksler og lager, servoer, peristaltisk pumpe, slanger, vanntank | 2 300 |
| Varme: silikonmatte 60 W, kjøleprofil, vifte, KSD301, termosikringer | 700 |
| Elektronikk: Mean Well GST220A24, ESP32-S3, Pololu G2, TMC2209, DRV8871, reléer, sikringer, nødstopp, sensorer, OLED, ledninger | 4 800 |
| Kamera: Pi Zero 2 W, Camera Module 3 Wide, kabel, minnekort, lys | 900 |
| Festemidler og filament (PETG ca. 1,2 kg, derav naturfarget for matkontakt) | 1 500 |
| **Sum** | **ca. 17 800** |

Bestill giveren, girmotoren, lastcella og strømforsyningen først. Formen og koblingen må måles før du printer (se [byggeveiledningen](../hardware/v1/README.md#3-skaff-en-giver-og-mål-delene)).

v0-stykklisten (ca. 8 900 kr) ligger fortsatt i [`hardware/v0/stykkliste.csv`](../hardware/v0/stykkliste.csv) som referanse.

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

## Fase 1 – måleoppsett og smart hevekabinett (K3)

> Hevekabinettet (vinkjøleskap, varme, SSR) er **valgfritt** etter ADR-008. Måleoppsettet for E02 og E03 er fortsatt nyttig.

| Vare | Til | Anslag (kr) |
|---|---|---|
| ESP32-S3-utviklingskort × 2 | Måleoppsett og hevekasse ([ADR-002](beslutninger/ADR-002-plattform-maaleoppsett.md)) | 300–500 |
| ToF-sensorer: VL6180X × 2 (glass) og VL53L1X × 1 (bolle) | Hevekurver (E02, E14) | 300–600 |
| DS18B20 vanntette temperaturfølere × 5 | Deig, vann og kammer | 150–250 |
| SHT4x romklimasensor | Romtemperatur og luftfuktighet | 100–200 |
| Lastcelle 5 kg og NAU7802- eller HX711-forsterker | Vekt og dosering | 100–200 |
| Koblingsbrett, ledninger, kontakter og koblingsboks | | 150–300 |
| Sous vide-pinne og kasse | Vannbad med stabil temperatur (E02) | 600–1 200 |
| Brukt lite vinkjøleskap med **kompressor** (Finn), med plass til bolle og hevekurv | Hevekabinettet (K3), som blir første trinn av maskinen ([arkitektur, avsnitt 4](07-arkitektur.md#4-termikk-grove-tall)) | 500–1 500 |
| Varmekilde (varmefolie, varmekabel eller PTC-element ≤ 100 W), termosikring og SSR eller relé | Varme i hevekabinettet | 300–600 |
| Sertifisert strømforsyning (5 V/12 V) og bærbar jordfeilbryter | Sikkerhet | 300–500 |
| *Valgfritt:* CO₂-sensor for høye nivåer (STC31 eller SprintIR) | E03 | 500–1 500 |

> **Sikkerhet:** Vinkjøleskapet skal ikke bygges om på 230 V-siden. Styr det eksternt med en sertifisert smartplugg eller et relé i egen godkjent boks, slik BrewPi-oppsett gjør. Selve kjølekretsen skal du ikke åpne.

## Valgfritt – brødmaskinskjelett (K1)

> Ikke lenger på den kritiske veien (ADR-008). Beholdt som en mulig «Surdeigsbaker Mini».

| Vare | Anslag (kr) |
|---|---|
| Brukt brødmaskin (Finn), for motor, drivverk og form | 200–600 |
| SSR med kjøleribbe (til den svake varmen) | 150–300 |
| Topolet relé (sikkerhetsfrakobling) | 150–400 |
| Termosikring (engangs) og termostat med manuell tilbakestilling | 100–300 |
| Temperaturfølere til deig og kammer (DS18B20/PT1000) | 100–300 |
| Styring av AC-motor (relé eller triac-modul) og strømmåling for overvåking av blokkering | 200–400 |
| Sertifisert strømforsyning og apparatinntak | 150–300 |
| Ledninger, kabelsko og strekkavlastning | 100–200 |
| Kabinett eller koblingsboks for elektronikken (utenfor kammeret) | 200–400 |
| Mekanisk tilpasning: brakett, gjennomføringer og tetninger i kabinettet | 200–500 |

## Opprinnelig anslag for prototype v1 (K2, utdatert)

> Skrevet før ADR-007, ADR-008 og ADR-010. Kjøling utgår, og den faktiske stykklisten for v1 står over. Tabellen er beholdt for sporbarhet.

| Delsystem | Innhold | Anslag (kr) |
|---|---|---|
| Elte- og hevemodul | Bolle i rustfritt stål, krok, girmotor (100–200 W) og driver, lastcelle | 1 000–2 500 |
| Kammer og kjøling | Kompressorenhet (fra vinkjøleskap eller kjøleboks) eller Peltier-sett, og isolasjon | 500–2 000 |
| Svak varme | Varmefolie eller PTC (≤ 100 W) og termosikring | 200–500 |
| Lokk og mekanikk | Hengsel eller løft til krok og lokk, brytere for lokk og bolle | 300–1 000 |
| Dosering (N3) | Melsnegle med omrører, to peristaltiske pumper og tank | 800–2 000 |
| Ramme og kabinett | Aluminiumsprofiler, platearbeid og festemidler | 800–2 000 |
| Elektronikk | Raspberry Pi eller Home Assistant-vert, MCU-kort, sikkerhetsvakt og eventuelt eget kretskort | 1 000–2 000 |
| Overlevering | Ekstra bolle og en hevekurv som passer i kammeret | 200–500 |
| Diverse | Ledninger, kontakter, matgodkjent silikon og skruer | 800–1 500 |

## Verktøy og tilgang

Disse trenger du ikke eie, men du trenger tilgang til dem:

- 3D-skriver med dyse av rustfritt stål (ingen printede deler berører deigen, men noen berører tørt mel og salt)
- Loddestasjon og multimeter
- Bor og gjengeverktøy
- Gjerne et makerspace med platebearbeiding

## Innkjøpsrutine

1. Kjøp bare det **neste fase** trenger. Planen vil endre seg underveis.
2. Hver bestilling noteres i `hardware/innkjop.csv` (opprettes ved første kjøp) med dato, vare, leverandør, pris og hvilket delsystem den hører til. Det blir grunnlaget for stykklisten (BOM) til DIY-versjonen.
