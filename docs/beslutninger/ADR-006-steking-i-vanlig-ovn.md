# ADR-006: Maskinen leverer stekeklar deig, og stekingen skjer i vanlig ovn

- **Status:** vedtatt
- **Dato:** 2026-10-13
- **Port:** G0

## Kontekst

Det første utkastet til planen la opp til at maskinen også skulle steke brødet. Det krevde en gryte med lokk ved ca. 250 °C og et varmeelement på ca. 1800 W, og deigen måtte overføres til en varm gryte. Det var den største kilden til teknisk risiko, kostnad og brannfare, og til høye krav i regelverket.

Eieren av prosjektet presiserte at det opprinnelig var tenkt slik: *Stekingen kan gjøres i en vanlig ovn. Surdeigsbakeren er prosessen fram til brødet settes inn i ovnen.*

## Beslutning

Maskinen gjør alt fram til **stekeklar deig** og **varsler** når ovnen skal forvarmes. Mennesket steker i vanlig ovn, med jerngryte etter referanseoppskriften.

Overleveringen skjer på en av to måter. Hvilken som blir standard, avgjøres av E06.

1. **Uten forming:** Kald deig i avtakbar bolle tippes rett i gryta.
2. **Med forming:** Mennesket former deigen etter bulkhevingen og legger den i en hevekurv. Maskinen etterhever og kaldhever den.

## Konsekvenser

**Enklere:**
- Stekemodul, gryte, lokkaktuator og overføring til varm gryte forsvinner.
- Effekten faller fra ca. 2000 W til ca. 600 W.
- Det er ingen høytemperatursoner, så PTFE-belegg kan brukes i bollen, og overskap er ikke et problem.
- Brannrisikoen er mye lavere.
- Relevante standarder blir trolig IEC 60335-2-14 (kjøkkenmaskiner) og -2-24 (kjøling) i stedet for -2-9.
- Budsjettet går ned med flere tusen kroner.

**Viktigere enn før:**
- Kjøling og kaldhold (4–6 °C i mange timer).
- Nøyaktig tidsplan («stekeklar kl. 07:00»), og varsling i god tid før ovnen må forvarmes.
- Avtakbar bolle og hevekurv som er lette å håndtere for mennesket.

**Endret:**
- Konseptene i [`03-konsepter.md`](../03-konsepter.md) er skrevet om.
- E08 handler nå om stekeprosessen for mennesket, ikke om maskindesign. E10 handler om overlevering for hånd. Ny E16 tester kaldhold.

**Senere mulighet:** Maskinen kan integreres med smartovner som kan fjernstyres. Det skal bare skje med ovnens egne sikkerhetsfunksjoner og bekreftelse fra mennesket. Se [`07-arkitektur.md`](../07-arkitektur.md).
