# Surdeigsbaker 🍞

**En åpen DIY-maskin på kjøkkenbenken som lager surdeigsdeigen for deg, fra surdeig til stekeklar deig, til det tidspunktet du ønsker. Du steker i din vanlige ovn.**

> **Status: Fase 0, forstudie (oktober 2026).** Ingenting er bygget ennå. Repoet inneholder planen, forstudien, eksperimentplanen og malene. Følg med, eller bidra!

## Hvorfor?

Et godt surdeigsbrød krever få ingredienser, men mange små håndgrep på riktig tidspunkt over et døgn: mating, autolyse, elting, bretting, forming, heving og kald heving. Tidene endrer seg med årstiden. *Selve stekingen* tar under en time og fungerer utmerket i en vanlig ovn med jerngryte. Det tidkrevende er alt som skjer før. Brødmaskiner kan elte, men de kan ikke kjøle, ikke bretting og ikke planlegge kald heving. **Det nærmeste vi har funnet, er produkter som bare steller surdeigen.** Vi vil lage maskinen for resten, og vi gjør det åpent.

## Målet

> **Suksess:** En ferdig prototype på kjøkkenbenken som har laget deigen til sine første surdeigsbrød, stekt i vanlig ovn. Kriteriene er:
> - tre godkjente brød på rad, med ≥ 80 % av referansebrødets poengsum
> - deigen stekeklar til planlagt tid (±30 min)
> - minimalt med manuelt arbeid
> - bestått sikkerhetssjekkliste

| Nivå | Maskinen gjør | Du gjør (i tillegg til å steke) |
|---|---|---|
| N1 (første milepæl) | Smart hevekabinett: varme, kjøling, tidsplan og varsler | Blander, elter, bretter og former |
| N2 (minimum) | Elter, bulkhever med bretting, kaldhever og holder deigen kald | Veier og heller i ingrediensene |
| **N3 (mål for v1)** | Doserer mel, vann og salt, bygger levain og gjør alt det andre | Tilsetter 1 ss surdeig og fyller på beholdere |
| N4 (strekkmål) | Steller i tillegg surdeigen («Surhild-modulen») | Fyller på og vasker ukentlig |

**Overlevering:** Enten tipper du den kalde deigen rett fra bollen i den varme gryta («tipp og stek»), eller så former du den på 2–5 min når maskinen sier fra («med forming»). Maskinen varsler i god tid: *«Forvarm ovnen nå.»*

Detaljer: [`docs/00-visjon-og-suksesskriterier.md`](docs/00-visjon-og-suksesskriterier.md) og [ADR-006](docs/beslutninger/ADR-006-steking-i-vanlig-ovn.md).

## Slik ser vi for oss maskinen (foreløpig favoritt, K2)

```text
┌───────────────────────────────────┐
│  Melbeholder      Vann/saltlake   │  ← påfylles ukentlig (N3)
├────────── lokk ───────────────────┤
│  girmotor → krok   ToF   innløp   │
├───────────────────────────────────┤
│   avtakbar bolle    │ plass til   │  ← 4–30 °C, på vekt
│   (rustfritt)       │ hevekurv    │
│ kompressor · svak varme · styring │
└───────────────────────────────────┘
        ↓ stekeklar kl. 07:00
   din vanlige ovn + jerngryte
```

Veien dit går i trinn, og hvert trinn er nyttig i seg selv: **smart hevekabinett** (et ombygd vinkjøleskap) → **brødmaskindrev i kabinettet** → **egen eltebolle med dosering**. Se [konseptene](docs/03-konsepter.md).

## Veikart

| Fase | Innhold | Port / milepæl | Status |
|---|---|---|---|
| 0 | Oppstart, forstudie og referansebrød | G0: kravspesifikasjon v1 | 🟡 pågår |
| 1 | Smart hevekabinett (K3), prosesseksperimenter og fermenteringsmodell | M1: hevekabinett i bruk · G1: maskinvennlig oppskrift | ⚪ |
| 2 | Gangbart skjelett: brødmaskindrev i kabinettet (K1) | M2: første brød av maskinlaget deig | ⚪ |
| 3 | Konseptvalg og delsystemer (K2) | G3: ADR-001 og delsystemer godkjent | ⚪ |
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

Maskinen bruker 230 V, motor, kjøling og et svakt varmeelement, og skal gå ubemannet i mange timer. Les [`docs/06-sikkerhet.md`](docs/06-sikkerhet.md) før du bygger noe. Du bygger og bruker den på eget ansvar.

## Lisens

Dokumentasjonen er lisensiert under CC BY-SA 4.0, maskinvaren under CERN-OHL-S-2.0 og programvaren under GPL-3.0-or-later. Se [`LICENSE.md`](LICENSE.md). Lisensvalget er foreløpig ([ADR-003](docs/beslutninger/ADR-003-sprak-og-lisens.md)).

---

### English summary

**Surdeigsbaker** ("sourdough baker") is an open-source DIY countertop machine that does everything *before* the oven: levain, mixing, kneading, temperature-controlled bulk fermentation with folds, and cold retard. It delivers **cold, ready-to-bake dough at the time you choose**, and notifies you when to preheat your regular oven. You bake as usual in a Dutch oven. The project is in phase 0, research and planning; documentation is in Norwegian for now.

The plan is a staircase where every step is useful on its own:
1. A smart proofing/retarding cabinet (a converted compressor wine cooler).
2. A bread-machine drive inside it.
3. A purpose-built stainless kneading bowl with automatic dosing.

Contributions and bake logs are welcome. Licences: CC BY-SA 4.0 for docs, CERN-OHL-S-2.0 for hardware, GPL-3.0-or-later for software.
