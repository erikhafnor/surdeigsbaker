# ADR-008: Første maskindesign (v0) – benkemaskin med C-krok, varmeplate og 24 V

- **Status:** erstattet av [ADR-010](ADR-010-v1-arkitektur.md). v0 bygges ikke, men designet beholdes som referanse.
- **Dato:** 2026-10-16
- **Port:** G2 (framskyndet, se under)

## Kontekst

Eieren ba om et første utkast av maskinen som kan printes og kjøpes inn nå: *«Design maskinen og lag klar slik jeg kan 3D-printe delene og kjøpe elektronikk/motorer osv. … bare følg dine egne anbefalinger.»*

Etter ADR-006 (steking i vanlig ovn) og ADR-007 (ingen kjøling) er maskinen mye enklere. Den skal blande, elte, holde 24–27 °C, brette under bulkhevingen, måle hevingen og varsle. Veikartet hadde planlagt hackede brødmaskiner og målinger før et eget design. Vi bygger en egen v0 tidligere, fordi den er enkel nok og gir en plattform for de samme eksperimentene. Fase 1-eksperimentene (E01–E10) kan fortsatt gjøres for hånd parallelt.

Hele designet ligger i [`hardware/v0/`](../../hardware/v0/README.md) og er generert fra [`hardware/spec/v0.yaml`](../../hardware/spec/v0.yaml).

## Beslutninger og alternativer

| # | Vi valgte | Fordi | Forkastet |
|---|---|---|---|
| 1 | **Avtakbar rustfri bolle** (ca. 3,5 l, flat bunn) som står på en varmeplate | Billig standardvare, tåler oppvaskmaskin, deigen berører bare rustfritt stål | Brødmaskinform med padle i bunnen (akseltetning mot deigen, vanskelig å rengjøre). Printet bolle (ikke matsikker). |
| 2 | **C-krok fra lokket** (rustfri stang ⌀ 10, bøyd for hånd), drevet ovenfra | Ingen tetning i bunnen av bollen, og kroken tas ut for vask. Kan lages med skrustikke og rør. | Planetbevegelse som i en kjøkkenmaskin (for komplisert for v0). Padle i bunnen. |
| 3 | **Vippelokk** med hengsel bak. Motoren sitter på lokket. | Bollen blir lett å nå. Én bevegelse åpner alt. | Fast topp med motor på en søyle (høyere, vanskeligere å nå bollen). Skuff (vanskeligere å tette og låse). |
| 4 | **Parkering av kroken** med optisk gaffelsensor før lokket åpnes | Kroken må peke mot hengselen for ikke å treffe bollen når lokket vippes opp (sjekket i CAD: 3,9 mm klaring) | Rett krok (elter dårligere). Løftbar krok (mer mekanikk). |
| 5 | **Varmeplate** (50 W silikonelement på 3 mm aluminium) rett under bollen | Varmer deigen der den er, med lite effekt og ingen vifte. Bollen virker som varmefordeler. | Varme luften i kammeret (tregere, trenger vifte). Peltier (unødvendig uten kjøling). |
| 6 | **Bare 24 V (SELV)** fra en CE-merket bordstrømforsyning på 150 W | Ingen 230 V i maskinen. Mindre risiko og enklere CE-vurdering senere. | 230 V inn med intern strømforsyning (krever jording, avstander og kompetanse). |
| 7 | **Sikkerhet i maskinvaren:** Lokkbryteren forsyner motorreléet, og nødstoppen forsyner begge reléene. KSD301 (60 °C) og termosikring (77 °C) i serie med varmeelementet. | Virker uansett feil i fastvaren | Bare programvarevern |
| 8 | **ESP32-S3 med ESPHome** | Samme plattform som måleoppsettet (ADR-002). PID, H-bro, sensorer, nettside, Home Assistant og OTA er innebygd. | Egen C++-fastvare (mer arbeid nå). Raspberry Pi (unødvendig for v0, se ADR-004). |
| 9 | **Ramme av 2020-profil og plater i ACM 3 mm**, med printede deler i PETG | Lett å få tak i, lett å endre og tilgivende for feil i målene | Helprintet kabinett (for stort for vanlige printere). Platearbeid i stål (krever verksted). |
| 10 | **XPS-isolasjon** i kammeret | Mindre varmetap og jevnere temperatur med bare 50 W | Uisolert (mer effekt, mer avhengig av romtemperaturen) |
| 11 | **Hevingen måles med ToF-sensor** (VL53L0X) fra lokket, regnet om til volum i en kjegle | Billig, innebygd i ESPHome og ingen kontakt med deigen | Kamera (mer arbeid). Lastcelle (måler ikke volum). VL53L1X (krever ekstern komponent i ESPHome, kan komme i v1). |
| 12 | **Manuell påfylling (N2).** Dosering flyttes til en v1-modul. | Tippekoppen for levain fikk ikke plass i hjørnet, og helleretningen kolliderte med kroken. Uten dosering kan v0 bygges og testes nå. | Dosering i v0 |
| 13 | **Parametrisk CAD i build123d** med automatiske kontroller (printvolum, klaringer, lokket som åpnes) | Agenter og mennesker kan endre et mål og bygge alt på nytt (ADR-005) | Manuell CAD i FreeCAD eller Fusion (vanskelig å endre og vurdere i git) |

## Konsekvenser

**Positivt:**
- Alt som trengs for å bygge v0, ligger i repoet: STL, STEP, DXF, bøyemal, stykkliste (ca. 9 000 kr), koblingsskjema og fastvare.
- Endringer i mål (f.eks. en annen bolle) gir nye filer og en ny sjekkrapport på under ett minutt.

**Risiko som må følges opp:**
- **Eltingen (E17):** Det er usikkert om en C-krok i senter av en kjegleformet bolle elter godt nok. **Testes som det første etter montering.** Reserveplan: spiralkrok, krok ut fra senter, høyere fart.
- **Bollen kan vri seg.** Friksjon fra silikonsnor og kantputene holder den nå. Hvis ikke det holder, trengs en medbringer i bunnen.
- **Høyden:** 541 mm lukket og ca. 700 mm med åpent lokk. Maskinen må trekkes fram fra overskapene. En lavere v1 kan ha motoren ved siden av bollen.
- **Mål på kjøpte deler** (bolle, motor, moduler) er typiske verdier og må måles før printing.
- **Fastvaren** er bare validert med `esphome config`, ikke kompilert eller testet på maskinvare.

**Endringer i planen:**
- Veikartet ([`04-veikart.md`](../04-veikart.md)) får en byggefase for v0 nå. Hacket brødmaskin (fase 2) blir valgfri.
- Ny eksperiment: **E17 eltetest** ([`05-eksperimenter.md`](../05-eksperimenter.md)).
- [ADR-001](ADR-001-konseptvalg.md) (konseptvalg) er i praksis avgjort for v0: avtakbar bolle med krok ovenfra, uten kjøling. Det endelige konseptvalget for v1 tas etter at v0 er testet.
