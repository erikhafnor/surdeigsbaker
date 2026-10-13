# ADR-003: Dokumentasjonsspråk og lisenser

- **Status:** foreslått. Bekreftes før det første eksterne bidraget kommer inn.
- **Dato:** 2026-10-13
- **Port:** G0

## Kontekst

Prosjektet skal være åpent og kan bli en DIY-byggeoppskrift for andre. Både språket og lisensen bestemmer hvem som kan bidra, og hva andre kan gjøre med designet.

## Beslutning (forslag)

### Språk

- **Dokumentasjon:** norsk (bokmål) i fase 0–4. Det er raskest for kjerneteamet.
- **README:** har en engelsk oppsummering.
- **Kode, kodekommentarer og filnavn i fastvaren:** engelsk.
- **Fase 5:** Byggeveiledning og README oversettes til engelsk for å nå det internasjonale DIY-miljøet.

### Lisenser (vanlig modell for åpen maskinvare)

| Del | Lisens | SPDX-kode |
|---|---|---|
| Dokumentasjon, oppskrifter og bilder | Creative Commons Attribution-ShareAlike 4.0 | `CC-BY-SA-4.0` |
| Maskinvare (CAD, kretskort, mekaniske tegninger) | CERN Open Hardware Licence v2, Strongly Reciprocal | `CERN-OHL-S-2.0` |
| Programvare og fastvare | GNU General Public License v3.0 or later | `GPL-3.0-or-later` |

Alle tre lisensene er «del-på-samme-vilkår»-lisenser (copyleft). Forbedringer andre gjør og distribuerer, må derfor også være åpne. Lisensene hindrer ikke salg av byggesett, men den som selger, må dele endringene sine.

## Alternativer

1. **Tillatende lisenser** (`MIT`, `CERN-OHL-P-2.0` og `CC-BY-4.0`): gir enklest gjenbruk, også i lukkede kommersielle produkter. Ulempen er at forbedringer ikke nødvendigvis kommer tilbake til prosjektet.
2. **Bare én lisens for alt:** enklere, men programvarelisenser passer dårlig for maskinvare og dokumentasjon.

## Konsekvenser

- Bibliotekene vi velger, må ha kompatible lisenser. GPL-3.0 er kompatibel med f.eks. Klipper (GPL-3.0) og med MIT-bibliotek.
- Lisensen kan endres så lenge det bare er eierens eget arbeid i repoet. Etter at andre har bidratt, krever en endring samtykke fra dem. **Avgjør derfor lisensen før det første eksterne bidraget.**
