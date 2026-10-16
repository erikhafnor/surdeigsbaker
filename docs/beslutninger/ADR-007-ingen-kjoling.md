# ADR-007: Ingen kjøling i maskinen – kald etterheving skjer i brukerens kjøleskap

- **Status:** vedtatt
- **Dato:** 2026-10-16
- **Port:** G0
- **Erstatter:** delene av [ADR-006](ADR-006-steking-i-vanlig-ovn.md) og [`03-konsepter.md`](../03-konsepter.md) som handler om kjøling og kaldhold i maskinen

## Kontekst

Etter ADR-006 skulle maskinen også kjøle deigen (kald heving og kaldhold ved 4–6 °C). Det krevde kompressor eller Peltier, et isolert kjølekammer, håndtering av kondens og mer effekt. Det ble også den største kilden til støy og kostnad.

Eieren av prosjektet presiserte: *Vi dropper kjøling. Deigen legges klar, og brukeren setter den selv i kjøleskapet og steker den selv. Produktet skal gjøre stegene fram til kald etterheving.*

## Beslutning

Maskinen gjør alle trinnene fram til **forming og kald etterheving**:

1. Levain (valgfritt i maskinen, se trinn 2 i v0)
2. Blanding, fermentolyse og elting
3. Bulkheving ved styrt temperatur (24–27 °C), med bretting og måling av hevingen
4. **Varsel: «Deigen er klar for forming»** til tidspunktet du har planlagt

Deretter tar mennesket over. Du former deigen eller tipper den i en hevekurv, setter kurven i ditt eget kjøleskap (8–24 t) og steker i vanlig ovn.

Maskinen **varmer bare**. Den har ingen kjøling.

## Konsekvenser

**Enklere:**
- Ingen kompressor, Peltier, kondens eller kjølekammer
- Hele maskinen kan drives av en **ferdig sertifisert 24 V-strømforsyning**, så det er ingen 230 V inne i maskinen (se [ADR-008](ADR-008-v0-design.md))
- Lavere effekt (≤ 150 W), mindre støy og lavere pris

**Viktigere:**
- **Tidsplanen må treffe tidspunktet for forming.** Uten kjøling kan maskinen ikke holde deigen lenge. Den kan bare slå av varmen og la deigen gå langsommere ved romtemperatur. Tidsplanleggeren må derfor legge slutten av bulkhevingen til et tidspunkt brukeren har valgt (f.eks. 19–22).
- **Ventevinduet** etter bulk ved romtemperatur blir en viktig parameter (E16 er endret til dette).

**Fjernet eller endret:**
- Kaldhold (gamle E16) og kjøledelen av E13 er fjernet.
- Konseptene er forenklet (se [`03-konsepter.md`](../03-konsepter.md)).
- Akseptansekriteriet om kaldhold er erstattet med et kriterium om treffsikkerhet for formetidspunktet.
