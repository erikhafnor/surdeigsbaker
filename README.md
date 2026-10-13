# Surdeigsbaker 🍞

**En åpen DIY-maskin som lager surdeigsbrød på kjøkkenbenken, fra surdeig til ferdig brød.**

> **Status: Fase 0, forstudie (oktober 2026).** Ingenting er bygget ennå. Repoet inneholder planen, forstudien, eksperimentplanen og malene. Følg med, eller bidra!

## Hvorfor?

Et godt surdeigsbrød krever få ingredienser, men mange små håndgrep på riktig tidspunkt over et døgn: mating, autolyse, elting, bretting, forming, heving, kald heving og steking i rykende varm gryte. Tidene endrer seg med årstiden. Brødmaskiner finnes, men de når bare ca. 140–155 °C, gir formbrød med blek skorpe og kan ikke kjøle. **Vi har ikke funnet noe hjemmeapparat som lager hele surdeigsbrødet automatisk.** Det vil vi gjøre noe med, og vi gjør det åpent.

## Målet

> **Suksess:** En ferdig prototype på kjøkkenbenken som har laget sine første surdeigsbrød. Kriteriene er tre godkjente brød på rad, ≥ 70 % av referansebrødets poengsum, kjernetemperatur ≥ 96 °C, minimalt med manuelt arbeid og bestått sikkerhetssjekkliste.

| Nivå | Maskinen gjør | Du gjør |
|---|---|---|
| N2 (minimum) | Elter, hever, kjøler og steker | Veier og heller i ingrediensene |
| **N3 (mål for v1)** | Doserer mel, vann og salt, bygger levain og gjør alt det andre | Tilsetter 1 ss surdeig og fyller på beholdere |
| N4 (strekkmål) | Steller i tillegg surdeigen («Surhild-modulen») | Fyller på og vasker ukentlig |

Detaljer: [`docs/00-visjon-og-suksesskriterier.md`](docs/00-visjon-og-suksesskriterier.md)

## Slik ser vi for oss maskinen (foreløpig favoritt)

```text
┌───────────────────────────────────┐
│  Melbeholder      Vann/saltlake   │  ← påfylles ukentlig
├───────────────────────────────────┤
│   Elte- og hevebolle (vippbar)    │  ← 4–30 °C, på vekt, med hevesensor
├─────── termisk skille / luke ─────┤
│   Gryte med lokk (≤ 260 °C)       │  ← egne varmeelementer og termosikringer
└───────────────────────────────────┘
```

Prinsippet er at **oppskriften tilpasses maskinen**. Hvis eksperimentene viser at brødet blir godt nok uten forming og snitting, blir maskinen *mye* enklere. Se [konseptene](docs/03-konsepter.md).

## Veikart

| Fase | Innhold | Port / milepæl | Status |
|---|---|---|---|
| 0 | Oppstart, forstudie og referansebrød | G0: kravspesifikasjon v1 | 🟡 pågår |
| 1 | Bakelab, prosesseksperimenter og fermenteringsmodell | G1: maskinvennlig oppskrift | ⚪ |
| 2 | Gangbart skjelett: hacket brødmaskin | M2: første maskinbakte surdeigsbrød | ⚪ |
| 3 | Konseptvalg og delsystemer | G3: ADR-001 og delsystemer godkjent | ⚪ |
| 4 | Integrasjon av prototype v1 | **M4: I MÅL 🎉** | ⚪ |
| 5 | Dokumentasjon og DIY-klargjøring | G5: noen andre bygger en | ⚪ |

Detaljer, tidslinje og risikoregister: [`docs/04-veikart.md`](docs/04-veikart.md)

## Dokumentasjon

| Dokument | Innhold |
|---|---|
| [00 – Visjon og suksesskriterier](docs/00-visjon-og-suksesskriterier.md) | Mål, automasjonsnivåer, brødkort, rammer og designprinsipper |
| [01 – Prosessanalyse](docs/01-prosessanalyse.md) | Fra håndgrep til maskinfunksjoner, og den maskinvennlige hypotesen |
| [02 – Forskningsplan](docs/02-forskningsplan.md) | Forskningsspørsmål, forskningsområdene FO1–FO8 og foreløpige funn |
| [03 – Konsepter](docs/03-konsepter.md) | Fem konsepter og en Pugh-matrise |
| [04 – Veikart](docs/04-veikart.md) | Faser, porter, risikoer og arbeidsform |
| [05 – Eksperimenter](docs/05-eksperimenter.md) | E01–E15 |
| [06 – Sikkerhet](docs/06-sikkerhet.md) | Elektrisk sikkerhet, brannsikkerhet, matkontakt og regelverk ⚠️ |
| [07 – Arkitektur](docs/07-arkitektur.md) | Moduler, sensorer, effekt, termikk, styring og programvare |
| [08 – Kilder](docs/08-kilder.md) | Leseliste og kjente løsninger |
| [09 – Budsjett og innkjøp](docs/09-budsjett-og-innkjop.md) | Handleliste per fase |
| [10 – Verktøykjede](docs/10-verktoykjede.md) | Åpne CAD-, EDA-, simulerings- og fastvareverktøy for AI-agenter (MCP), med sikkerhetssperrer |
| [Beslutninger (ADR)](docs/beslutninger/) | Viktige valg og begrunnelser |
| [Referanseoppskrift](oppskrifter/referanse-v7.md) | Gullstandarden, oversatt til prosessparametre |

## Struktur

```text
docs/           plan, forskning, beslutninger og maler
oppskrifter/    referanseoppskrift og maskinlesbare oppskrifter (.yaml)
data/           bakelogger og rådata fra eksperimenter
hardware/       CAD, elektronikk og stykkliste (kommer)
firmware/       kode for måleoppsett og maskin (kommer)
```

## Bidra

Alle bidrag er velkomne: bakelogger, eksperimenter, kilder, ideer og etter hvert kode og maskinvare. Se [`CONTRIBUTING.md`](CONTRIBUTING.md). Bruk issue-malene for **bakelogg**, **eksperiment** og **idé**.

## ⚠️ Sikkerhet

Maskinen bruker 230 V, ca. 2 kW og ca. 250 °C, og skal gå ubemannet. Les [`docs/06-sikkerhet.md`](docs/06-sikkerhet.md) før du bygger noe. Du bygger og bruker den på eget ansvar.

## Lisens

Dokumentasjonen er lisensiert under CC BY-SA 4.0, maskinvaren under CERN-OHL-S-2.0 og programvaren under GPL-3.0-or-later. Se [`LICENSE.md`](LICENSE.md). Lisensvalget er foreløpig ([ADR-003](docs/beslutninger/ADR-003-sprak-og-lisens.md)).

---

### English summary

**Surdeigsbaker** ("sourdough baker") is an open-source DIY countertop machine that makes real sourdough bread – crusty, Dutch-oven style – from starter to finished loaf with minimal human work. The project is in phase 0, research and planning; documentation is in Norwegian for now. The core idea is to *adapt the recipe to the machine*: minimise dough transfers, skip shaping and scoring if experiments show it's acceptable, and use temperature control (including cold retard) to make timing predictable ("ready at 07:00"). The leading concept is a temperature-controlled, tilting kneading and fermentation bowl above an electrically heated lidded pot. Contributions and bake logs are welcome. Licences: CC BY-SA 4.0 for docs, CERN-OHL-S-2.0 for hardware, GPL-3.0-or-later for software.
