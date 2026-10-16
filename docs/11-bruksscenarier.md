# 11 – Bruksscenarier: en bakedag med v0 og med v1

Dette dokumentet viser hvordan en vanlig bakedag ser ut for deg som baker, med maskinen slik den er nå (v0) og slik målet er for prototype v1 (N3). Scenariet i v1 er en **designmålsetting**: Det beskriver hva maskinen skal kunne, og hva som må på plass for å komme dit.

I begge versjonene steker du selv i vanlig ovn ([ADR-006](beslutninger/ADR-006-steking-i-vanlig-ovn.md)), og den kalde etterhevingen skjer i ditt eget kjøleskap ([ADR-007](beslutninger/ADR-007-ingen-kjoling.md)).

**Felles eksempel:** Du står opp kl. 07, er ute hele dagen og vil steke et brød neste morgen.

## Scenario 1: v0 (N2) – slik maskinen er nå

v0 har verken utsatt start, tidsplanlegger eller dosering. Derfor bruker du dagen til levainen og kvelden til deigen:

- **07:00 (5 min):** Du lager en langsom levain (10 g surdeig, 50 g mel og 50 g vann) rett i maskinbollen.
- **17:30 (10 min):** Du heller i resten av melet og vannet og trykker **Start**.
- **ca. 18:15 (2 min):** Du heller i saltlaken.
- **ca. 22:00 (25 min):** Du former deigen og setter den i kjøleskapet.
- **Neste morgen:** Du steker.

Hele tidsplanen med mengder og råd står i [byggeveiledningen, § 8](../hardware/v0/README.md#8-en-vanlig-bakedag-med-v0).

## Scenario 2: v1 (N3) – «1 ss surdeig, klar for forming kl. 17»

### Det du gjør

| Når | Du gjør | Din tid |
|---|---|---|
| **En gang i uka** | Fyll beholderne med **mel** (siktet og sammalt, nok til ca. 4 brød) og **salt** (nok til ca. 20 brød). | 5 min |
| **07:00** | Ta surdeigsglasset ut av kjøleskapet og ha **1 ss (ca. 20 g)** i den rene bollen. Sett bollen i maskinen og lukk lokket. Fyll **vanntanken** med friskt vann (ca. 0,5 l). Velg **«Klar for forming kl. 17:00»** på displayet eller i appen. Maskinen viser planen. Trykk **Start**. Mat surdeigen din og sett glasset tilbake i kjøleskapet. | 3 min |
| 07:05–17:00 | Du er ute. Vil du, kan du følge med på mobilen. | – |
| 16:30 | Varsel: *«Deigen er klar for forming ca. kl. 17:00.»* | – |
| **17:00** | Varsel: *«Deigen er klar for forming.»* Form deigen, legg den i hevekurven og sett den i kjøleskapet. Trykk **OK**. Skyll bollen og kroken. | 25 min |
| **Neste morgen** | Forvarm ovnen med gryta og stek, akkurat som i dag. | 10 min |

Det blir ca. **40 minutter** med aktivt arbeid per brød (ca. 30 uten stekingen), pluss 5 minutter i uka. Du fyller bare på mel, salt og vann. Saltlaken lager maskinen selv. Du trenger bare å være hjemme når deigen skal formes, og **du bestemmer selv når det er**.

### Det maskinen gjør

Tidene er et eksempel. Maskinen regner dem ut selv, baklengs fra 17:00.

| Tid | Maskinen |
|---|---|
| 07:00 | Sjekker at det er nok mel, salt og vann, og at 17:00 er mulig i dag. Viser planen: *«Levain 07:05–12:15 · deig 12:15 · bulk 13:10–17:00 · klar 17:00 ±30 min.»* |
| 07:05 | Veier opp og doserer 40 g siktet mel, 10 g sammalt mel og 50 g vann på 26 °C til levainen. Blander i 1 min. |
| 07:05–12:15 | Holder levainen på ca. 25 °C og måler hevingen. Er den raskere eller tregere enn planlagt, justeres temperaturen. |
| ca. 10:00 | Melding: *«Levainen er i rute. Prognose: klar for forming 17:05.»* |
| ca. 12:15 | Levainen er klar. Doserer resten av melet (460 g siktet og 100 g sammalt) og vannet (372 g, temperert slik at deigen blir ca. 26 °C). Blander i 3 min. Fermentolyse i 40 min. |
| ca. 13:00 | **Lager saltlaken:** veier opp 12 g salt og 48 g vann (se under). Elter i 10 min. |
| 13:10–17:00 | Bulkheving ved 24–27 °C, med 4 brettinger. Måler hevingen og justerer temperaturen underveis slik at deigen treffer 17:00. |
| 16:30 | Varsler at deigen snart er klar. |
| 17:00 | Slår av varmen og varsler: *«Deigen er klar for forming.»* Påminnelse hvis du ikke har kvittert etter 30–60 min. |

### Slik lager maskinen saltlaken

Du fyller bare på tørt salt. Ved salttrinnet veier maskinen opp 12 g salt og 48 g vann, som gir 60 g saltlake på 20 % (godt under metning, som er ca. 26 %). To måter skal prøves i E12:

1. **Saltlake i bollen (enklest):** Maskinen drysser saltet over deigen, heller vannet over og venter ca. 1 min før eltingen. Saltlaken blir til oppå deigen, og kroken arbeider den inn. Det trengs bare en saltdoserer, og vanntanken og vekta finnes fra før.
2. **Saltkopp (som referansen):** Saltet og vannet doseres i en liten kopp der saltet løses helt opp før koppen tippes i bollen. Det gir samme saltlake som når du blander den selv, men krever kopp, omrøring og tippemekanisme.

Vi starter med variant 1. Blir saltet ujevnt fordelt i deigen, går vi over til variant 2.

**Saltdosereren:** Salt renner mye lettere enn mel og kan doseres med en liten snegle eller en cellehjulsdoserer (som i en såmaskin), stoppet av vekta under bollen. Salt trekker fukt og klumper seg over ca. 75 % relativ luftfuktighet. Derfor må beholderen være tett og stå utenfor det fuktige kammeret, og fint salt med antiklumpemiddel er tryggest.

### Slik treffer maskinen tidspunktet uten kjøling

Maskinen kan bare varme, ikke kjøle. Den kan derfor gjøre gjæringen raskere ved å øke temperaturen, men aldri saktere enn ved romtemperatur. Tidsplanleggeren bruker tre grep:

1. **Velger en plan midt i spillerommet.** Levain og bulk planlegges ved 24–25 °C, ikke ved maks temperatur. Da kan maskinen både skru opp (til 27–28 °C) og ned (mot romtemperatur) hvis surdeigen er raskere eller tregere enn forventet.
2. **Tilpasser levainen til tiden som er igjen.** Er det lenge til du kommer hjem, doserer den mer mel og vann til levainen (f.eks. 1:5:5 i stedet for 1:2,5:2,5), så den bruker lengre tid. Det er det samme trikset som i v0, bare automatisk.
3. **Sier fra tidlig.** Viser målingene ved 10-tiden at deigen blir klar for tidlig eller for sent, får du beskjed med en gang, ikke kl. 17. Da har du tid til å legge om dagen.

Når du velger tidspunkt, viser maskinen hva som er mulig. Med start kl. 07 kan det for eksempel være **tidligst ca. 15:00 og senest ca. 22:00** (anslag, avhenger av E02 og romtemperaturen). Målet er at deigen er klar innen **±30 min** av valgt tid ([akseptansekriterium 3](00-visjon-og-suksesskriterier.md#akseptansekriterier-for-første-surdeigsbrød)).

### Sammenligning

| | v0 (N2, nå) | v1 (N3, mål) |
|---|---|---|
| Om morgenen | Vei og bland en levain (5 min) | 1 ss surdeig og velg tid (3 min) |
| Må være hjemme | Hele kvelden: start, saltlake etter 45 min og forming ca. 4 timer senere | Bare ved forming |
| Tidspunkt for forming | Blir når det blir, ca. 4–5 timer etter start | Du velger selv, innenfor et vindu |
| Veiing | Du veier alt | Maskinen veier alt |
| Salt | Du blander saltlaken og heller den i når maskinen piper | Maskinen veier saltet og lager saltlaken selv |
| Aktiv tid per brød (uten steking) | 45–60 min | ca. 30 min |
| Ukentlig | – | Fyll på mel og salt (5 min) |

## Hva som må til for scenario 2

| Funksjon | Hva den må klare | Avgjøres av |
|---|---|---|
| **Dosering av mel** | Snegle fra to melbeholdere, stoppet av en vekt under bollen. ±1 % på 560 g og ±2 g på levainen. Melet må ikke henge seg opp. | E11 |
| **Dosering av vann** | Pumpe styrt av vekta. Vannet tempereres. | E12 |
| **Salt og saltlake** | Tørt salt fra en tett beholder doseres etter vekt (±0,5 g av 12 g) og løses i 48 g vann til saltlake | E12 |
| **Levain i bollen fra 1 ss** | Fermentolyse med levain i bollen gir like godt brød | E04 |
| **«Levainen er klar»-signal** | Måling som forteller når levainen er klar, uten flytetest | E02, E03 |
| **Fermenteringsmodell** | Forutsier levain og bulk innenfor ±1 t ut fra temperatur og blandingsforhold | E02 |
| **Hevemåling** | Bulkhevingen måles innenfor ±5 prosentpoeng | E14 |
| **Ventevindu** | Hvor lenge deigen tåler å vente ved romtemperatur. Det avgjør hvor presis planen må være. | E16 |
| **Tidsplanlegger og prognose** | Planlegger baklengs, justerer temperaturen og varsler tidlig om avvik | Fastvare v1 |
| **Brukergrensesnitt** | Velge tidspunkt på displayet eller i appen, og se planen og prognosen | Fastvare v1 |
| **Plass til beholderne** | Mel, salt og vann må få plass uten å kollidere med kroken eller lokket. Det fikk ikke plass i v0. | Design v1 |
| **Hygiene** | Tette og tørre beholdere for mel og salt, utenfor det fuktige kammeret. Vanntank som tømmes og fylles hver bakedag. | [`06-sikkerhet.md`](06-sikkerhet.md) |

Når disse er på plass, er maskinen på nivå N3 ([`00-visjon-og-suksesskriterier.md`](00-visjon-og-suksesskriterier.md)), som er målet for prototype v1 i [veikartet](04-veikart.md).
