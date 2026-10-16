# Surdeigsbaker 🍞

**En åpen DIY-maskin på kjøkkenbenken som lager surdeigsdeigen for deg: blanding, elting og bulkheving med bretting, til deigen er klar for forming. Du former, lar den kaldheve i ditt eget kjøleskap og steker i din vanlige ovn.**

> **Status (oktober 2026): Første maskindesign (v0) er klart til bygging.** Ingenting er bygget ennå. [`hardware/v0/`](hardware/v0/README.md) har alt du trenger: STL-filer, kappefiler, stykkliste, koblingsskjema, fastvare og byggeveiledning. Følg med, eller bidra!

## Hvorfor?

Et godt surdeigsbrød krever få ingredienser, men mange små håndgrep på riktig tidspunkt over et døgn: mating, autolyse, elting, bretting, forming, heving og kald heving. Tidene endrer seg med årstiden. *Selve stekingen* tar under en time og fungerer utmerket i en vanlig ovn med jerngryte. Det tidkrevende er alt som skjer før. Brødmaskiner kan elte, men de bretter ikke, måler ikke hevingen og sier ikke fra når deigen er klar for forming. **Det nærmeste vi har funnet, er produkter som bare steller surdeigen.** Vi vil lage maskinen for resten, og vi gjør det åpent.

## Målet

> **Suksess:** En ferdig prototype på kjøkkenbenken som har laget deigen til sine første surdeigsbrød, stekt i vanlig ovn. Kriteriene er:
> - tre godkjente brød på rad, med ≥ 80 % av referansebrødets poengsum
> - deigen klar for forming til planlagt tid (±30 min)
> - minimalt med manuelt arbeid
> - bestått sikkerhetssjekkliste

| Nivå | Maskinen gjør | Du gjør (i tillegg til å steke) |
|---|---|---|
| N1 | Smart hevekabinett: varme, tidsplan og varsler | Blander, elter, bretter og former |
| **N2 (v0, minimum)** | Blander, elter, bulkhever med bretting og varsler når deigen er klar for forming | Veier og heller i ingrediensene, former og setter kurven i kjøleskapet |
| **N3 (mål for v1)** | Doserer mel, vann og salt, bygger levain og gjør alt det andre | Tilsetter 1 ss surdeig, fyller på beholdere og former |
| N4 (strekkmål) | Steller i tillegg surdeigen («Surhild-modulen») | Fyller på og vasker ukentlig |

**Overlevering:** Maskinen sier fra: *«Deigen er klar for forming.»* Du former den på 2–5 min, legger den i hevekurven og setter den i kjøleskapet til neste dag. Eller du setter hele bollen i kjøleskapet og tipper deigen rett i gryta neste dag («tipp og stek»). Maskinen har ingen kjøling.

Detaljer: [`docs/00-visjon-og-suksesskriterier.md`](docs/00-visjon-og-suksesskriterier.md), [ADR-006](docs/beslutninger/ADR-006-steking-i-vanlig-ovn.md) og [ADR-007](docs/beslutninger/ADR-007-ingen-kjoling.md).

## v0: første maskin

![Surdeigsbaker v0 med åpent lokk](hardware/v0/bilder/v0_aapen_snitt.png)

- **346 × 346 × 541 mm**: ramme av 2020-profil med plater, isolert kammer og elektronikk i sokkelen
- **Avtakbar rustfri bolle** (ca. 3,5 l) på en varmeplate med 50 W silikonelement
- **C-krok av rustfri stang** drevet av en 24 V planetgirmotor i lokket. Lokket vippes opp bakover.
- **Bare 24 V** fra en CE-merket strømforsyning. Lokkbryter og nødstopp bryter motoren i maskinvaren.
- **ESP32-S3 med ESPHome:** PID-styrt temperatur, elte- og bretteprogram, hevemåling med ToF-sensor, nettside, Home Assistant og varsler på mobilen
- **Ca. 9 000 kr** i deler og ca. 1,1 kg PETG

Alt er generert fra én parameterfil med Python-koden i [`hardware/cad/`](hardware/cad/README.md). Endrer du et mål, får du nye filer og en ny [sjekkrapport](hardware/v0/sjekkrapport.md) på under ett minutt. **[Byggeveiledning →](hardware/v0/README.md)**

## Veikart

| Fase | Innhold | Port / milepæl | Status |
|---|---|---|---|
| 0 | Oppstart, forstudie og referansebrød | G0: kravspesifikasjon v1 | 🟡 pågår |
| 1 | Prosesseksperimenter og fermenteringsmodell | G1: maskinvennlig oppskrift | ⚪ |
| 2 | **Bygg v0** ([ADR-008](docs/beslutninger/ADR-008-v0-design.md)) | E17 eltetest · M2: første brød av deig fra v0 | 🟡 design klart |
| 3 | Konseptvalg for v1 og delsystemer (dosering, tidsplanlegger, kretskort) | G3: ADR-001 og delsystemer godkjent | ⚪ |
| 4 | Integrasjon av prototype v1 | **M4: I MÅL 🎉** | ⚪ |
| 5 | Dokumentasjon og DIY-klargjøring | G5: noen andre bygger en | ⚪ |

Detaljer, tidslinje og risikoregister: [`docs/04-veikart.md`](docs/04-veikart.md)

## Dokumentasjon

| Dokument | Innhold |
|---|---|
| [00 – Visjon og suksesskriterier](docs/00-visjon-og-suksesskriterier.md) | Mål, automasjonsnivåer, brødkort, rammer og designprinsipper |
| [01 – Prosessanalyse](docs/01-prosessanalyse.md) | Fra håndgrep til maskinfunksjoner, og den maskinvennlige hypotesen |
| [02 – Forskningsplan](docs/02-forskningsplan.md) | Forskningsspørsmål, forskningsområdene FO1–FO8 og foreløpige funn |
| [03 – Konsepter](docs/03-konsepter.md) | Fire konsepter, en Pugh-matrise og hvorfor v0 ble K2 uten kjøling |
| [04 – Veikart](docs/04-veikart.md) | Faser, porter, risikoer og arbeidsform |
| [05 – Eksperimenter](docs/05-eksperimenter.md) | E01–E17 |
| [06 – Sikkerhet](docs/06-sikkerhet.md) | Elektrisk sikkerhet, brannsikkerhet, matkontakt og regelverk ⚠️ |
| [07 – Arkitektur](docs/07-arkitektur.md) | Moduler, sensorer, effekt, termikk, styring og programvare |
| [08 – Kilder](docs/08-kilder.md) | Leseliste og kjente løsninger |
| [09 – Budsjett og innkjøp](docs/09-budsjett-og-innkjop.md) | Handleliste per fase |
| [10 – Verktøykjede](docs/10-verktoykjede.md) | Åpne CAD-, EDA-, simulerings- og fastvareverktøy for AI-agenter (MCP), med sikkerhetssperrer |
| [11 – Bruksscenarier](docs/11-bruksscenarier.md) | En bakedag med v0 og med v1: hva du gjør, og hva maskinen gjør |
| [Beslutninger (ADR)](docs/beslutninger/) | Viktige valg og begrunnelser |
| [Referanseoppskrift](oppskrifter/referanse-v7.md) | Gullstandarden, oversatt til prosessparametre |
| [**Byggeveiledning v0**](hardware/v0/README.md) | Hva du skal måle, kjøpe, printe, kappe og montere, og hvordan du setter maskinen i drift |
| [Koblingsskjema v0](hardware/v0/koblingsskjema.md) | 24 V-fordeling, sikkerhetskjede og pinnekart |
| [Fastvare v0](firmware/v0/README.md) | ESPHome-programmet: faser, knapper, sikkerhet og første opplasting |

## Struktur

```text
docs/           plan, forskning, beslutninger og maler
oppskrifter/    referanseoppskrift og maskinlesbare oppskrifter (.yaml)
data/           bakelogger og rådata fra eksperimenter
hardware/spec/  parameterfila som alle mål leses fra
hardware/cad/   build123d-kode som lager alt i hardware/v0/
hardware/v0/    STL, STEP, DXF, stykkliste, koblingsskjema, bilder og byggeveiledning
firmware/v0/    ESPHome-fastvare for v0
```

## Bidra

Alle bidrag er velkomne: bakelogger, eksperimenter, kilder, ideer og etter hvert kode og maskinvare. Se [`CONTRIBUTING.md`](CONTRIBUTING.md). Bruk issue-malene for **bakelogg**, **eksperiment** og **idé**.

## ⚠️ Sikkerhet

v0 har bare 24 V inne i maskinen (fra en CE-merket strømforsyning), men den har en sterk motor og et varmeelement, og den skal kunne gå ubemannet i mange timer. Les [`docs/06-sikkerhet.md`](docs/06-sikkerhet.md) før du bygger noe. Du bygger og bruker den på eget ansvar.

## Lisens

Dokumentasjonen er lisensiert under CC BY-SA 4.0, maskinvaren under CERN-OHL-S-2.0 og programvaren under GPL-3.0-or-later. Se [`LICENSE.md`](LICENSE.md). Lisensvalget er foreløpig ([ADR-003](docs/beslutninger/ADR-003-sprak-og-lisens.md)).

---

### English summary

**Surdeigsbaker** ("sourdough baker") is an open-source DIY countertop machine for everything *before* shaping: levain, mixing, kneading and temperature-controlled bulk fermentation with folds and rise measurement. It tells you when the **dough is ready for shaping**. You shape it, cold-retard it in your own fridge and bake it in your regular oven. Documentation is in Norwegian for now.

**v0 is designed and ready to build** ([`hardware/v0/`](hardware/v0/README.md)): a 2020-extrusion frame with a removable stainless bowl on a 50 W heater plate, a stainless C-hook driven from a tilting lid by a 24 V planetary gearmotor, 24 V only (external CE-marked supply) with hardware lid and e-stop interlocks, and an ESP32-S3 running ESPHome. Everything is generated from one parameter file by parametric build123d code: STL, STEP, DXF cutting files, a bending template, renders and automatic design checks. The bill of materials is about NOK 9,000. Nothing has been built yet.

Contributions and bake logs are welcome. Licences: CC BY-SA 4.0 for docs, CERN-OHL-S-2.0 for hardware, GPL-3.0-or-later for software.
