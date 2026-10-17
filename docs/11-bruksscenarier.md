# 11 – Bruksscenarier: en bakedag med v0 og med v1

Dette dokumentet viser hvordan en vanlig bakedag ser ut for deg som baker, med v0 (som ikke bygges) og med prototype v1 (N3), som bygges nå. Scenariet i v1 følger designet i [`hardware/v1/`](../hardware/v1/README.md). Tidene er fra simuleringen av fastvaren ([`firmware/v1/`](../firmware/v1/README.md)), ikke fra ekte bakinger ennå.

I begge versjonene steker du selv i vanlig ovn ([ADR-006](beslutninger/ADR-006-steking-i-vanlig-ovn.md)), og den kalde etterhevingen skjer i ditt eget kjøleskap ([ADR-007](beslutninger/ADR-007-ingen-kjoling.md)).

**Felles eksempel:** Du står opp kl. 07, er ute hele dagen og vil steke et brød neste morgen.

## Scenario 1: v0 (N2) – til sammenligning

v0 bygges ikke ([ADR-010](beslutninger/ADR-010-v1-arkitektur.md)), men scenariet viser hvor mye v1 sparer deg for. v0 har verken utsatt start, tidsplanlegger eller dosering. Derfor bruker du dagen til levainen og kvelden til deigen:

- **07:00 (5 min):** Du lager en langsom levain (10 g surdeig, 50 g mel og 50 g vann) rett i maskinbollen.
- **17:30 (10 min):** Du heller i resten av melet og vannet og trykker **Start**.
- **ca. 18:15 (2 min):** Du heller i saltlaken.
- **ca. 22:00 (25 min):** Du former deigen og setter den i kjøleskapet.
- **Neste morgen:** Du steker.

Hele tidsplanen med mengder og råd står i [byggeveiledningen for v0, § 8](../hardware/v0/README.md#8-en-vanlig-bakedag-med-v0).

## Scenario 2: v1 (N3) – «1–2 ss surdeig, klar for forming kl. 17»

### Det du gjør

| Når | Du gjør | Din tid |
|---|---|---|
| **Før hver eller annenhver baking** | Fyll melbeholderen med **melblanding** (ca. 1,5 kg, nok til to brød). Saltboksen rommer ca. 450 g fint salt (ca. 35 brød) og fylles sjelden. | 3 min |
| **07:00** | Ta surdeigsglasset ut av kjøleskapet og ha **2 ss (ca. 40 g)** i den rene brødformen. Sett formen inn og lukk døra. Fyll **vanntanken** med friskt vann (ca. 0,5 l). Velg **«Klar for forming kl. 17:00»** på knappen eller i appen og trykk **Start**. Maskinen veier surdeigen og viser planen. Mat surdeigen din og sett glasset tilbake. | 3 min |
| 07:05–17:00 | Du er ute. Vil du, kan du følge med på mobilen. | – |
| **ca. 17:00** | Varsel: *«Deigen er klar for forming.»* Form deigen, legg den i hevekurven og sett den i kjøleskapet. Trykk **Deigen er formet**. Skyll formen og eltebladet. | 25 min |
| **Neste morgen** | Forvarm ovnen med gryta og stek, akkurat som i dag. | 10 min |

Med **1 ss (20 g)** kald surdeig er det tidligst ca. **kl. 17:30**. Velger du 17:00, sier maskinen fra med en gang og foreslår mer surdeig eller en senere tid. En surdeig du matet kvelden før, rekker 17:00 også med 1 ss.

Det blir ca. **40 minutter** med aktivt arbeid per brød (ca. 30 uten stekingen). Du fyller bare på mel, salt og vann. Saltlaken lager maskinen selv. Du trenger bare å være hjemme når deigen skal formes, og **du bestemmer selv når det er**.

### Det maskinen gjør

Tidene er fra simuleringen med 40 g kald surdeig og 21 °C i rommet ([`bake_test.cpp`](../firmware/v1/test/bake_test.cpp)). Maskinen regner dem ut selv, baklengs fra 17:00.

| Tid | Maskinen |
|---|---|
| 07:00 | Veier surdeigen: 40 g. Sjekker at 17:00 er mulig. Viser planen: *«Levain 1:1,25:1,25 (50 g mel, 50 g vann), 25,5 °C, levain 6,0 t, deig 3,9 t til +37 %.»* |
| 07:00 | Doserer 50 g vann og 50 g mel etter vekt og blander i 1 min |
| 07:01–13:09 | Holder levainen på ca. 25,5 °C. Laget er for tynt til å måles, så modellen og det maskinen har lært om surdeigen din, styrer. |
| 13:09–13:14 | Levainen er klar. Doserer ca. 316 g vann, rører ut levainen og doserer 490 g mel i tre porsjoner med blanding imellom. |
| 13:18–13:58 | Fermentolyse |
| 13:58 | **Lager saltlaken:** doserer 11 g salt og 45 g vann rett på deigen (se under), blander i 3 min og elter i 8 min |
| 14:20, 14:50, 15:20 | Bretter med eltebladet |
| 15:26 | Tar nullpunkt for hevingen med ToF-sensoren. Følger hevingen, lærer hvor aktiv surdeigen er, og justerer varmen slik at deigen treffer 17:00. |
| ca. 17:00 | Slår av varmen og varsler: *«Deigen er klar for forming.»* Lagrer det den har lært om surdeigen til neste baking. |

### Slik lager maskinen saltlaken

Du fyller bare på tørt salt. Ved salttrinnet doserer maskinen ca. 11 g salt og 45 g vann, som gir saltlake på ca. 20 % (godt under metning, som er ca. 26 %). Mengden følger melet som faktisk kom i. To måter kan prøves i E12:

1. **Saltlake i formen (enklest, valgt i v1):** Maskinen drysser saltet over deigen, heller vannet over og blander rolig før eltingen. Saltlaken blir til oppå deigen, og eltebladet arbeider den inn. Det trengs bare en saltdoserer, og vanntanken og vekta finnes fra før.
2. **Saltkopp (som referansen):** Saltet og vannet doseres i en liten kopp der saltet løses helt opp før koppen tippes i formen. Det gir samme saltlake som når du blander den selv, men krever kopp, omrøring og tippemekanisme.

v1 bruker variant 1. Blir saltet ujevnt fordelt i deigen, går vi over til variant 2.

**Saltdosereren:** En liten skrue (10 mm) fra en tett boks over taket, med egen klaff ned i kammeret og stoppet av vekta under formen. Salt trekker fukt og klumper seg over ca. 75 % relativ luftfuktighet. Derfor er boksen tett, med silikagel i lokket, og fint salt med antiklumpemiddel er tryggest.

### Slik treffer maskinen tidspunktet uten kjøling

Maskinen kan bare varme, ikke kjøle. Den kan derfor gjøre gjæringen raskere ved å øke temperaturen, men aldri saktere enn ved romtemperatur. Tidsplanleggeren ([gjæringsmodellen](forskning/v1-gjaeringsmodell.md)) bruker fire grep:

1. **Velger en plan midt i spillerommet.** Levain og bulk planlegges ved én temperatur midt mellom romtemperaturen og 28 °C. Da kan maskinen både skru opp og ned hvis surdeigen er raskere eller tregere enn forventet.
2. **Tilpasser levainen til tiden som er igjen.** Er det lenge til du kommer hjem, doserer den mer mel og vann til levainen (1:2,5:2,5 eller 1:5:5 i stedet for 1:1,25:1,25), eller utsetter starten. Det er det samme trikset som i v0, bare automatisk.
3. **Måler og lærer.** Etter brettingen måler ToF-sensoren hevingen. Maskinen regner ut hvor aktiv surdeigen er i dag, og justerer varmen. Aktiviteten huskes til neste baking.
4. **Sier fra ved start.** Er planen stram, får du beskjed med en gang: *«Planen har liten margin.»*

Når du velger tidspunkt, sjekker maskinen hva som er mulig. Med start kl. 07 og 21 °C i rommet gir modellen:

| Surdeig | Tidligst klar | Senest klar |
|---|---|---|
| 1 ss (20 g) rett fra kjøleskapet | ca. 17:30 | ca. 08:30 neste morgen |
| 2 ss (40 g) rett fra kjøleskapet | ca. 16:00 | |
| 1 ss matet kvelden før | ca. 16:15 | |

Målet er at deigen er klar innen **±30 min** av valgt tid ([akseptansekriterium 3](00-visjon-og-suksesskriterier.md#akseptansekriterier-for-første-surdeigsbrød)). I simuleringen treffer maskinen innen ca. 5 min når surdeigen er som modellen. Er surdeigen 20 % tregere eller 25 % raskere, bommer den med inntil ca. 1 t første gang, men lærer aktiviteten og treffer bedre neste gang. Modellen må valideres med ekte bakinger (E02).

### Kameraet i v1

Et kamera i taket i kammeret ([ADR-009](beslutninger/ADR-009-kamera.md)) gjør scenariet tryggere:

- **Bilde i varslene:** *«Levainen er i rute»* og *«Deigen er klar for forming»* kommer med et bilde av deigen, så du kan se den selv.
- **Bedre heving:** Kameraet ser hvor høyt deigen står langs formveggen, og ToF-sensoren måler i ett punkt. Sammen gir de en sikrere prognose.
- **Tidlige feilvarsler:** for eksempel *«Det ligger tørt mel i hjørnene»*, *«Deigen er nær kanten»* eller *«Formen står ikke riktig»*. (At formen er tom, ser vekta allerede.)

Bildene analyseres i Home Assistant, på en PC eller i skyen, ikke i selve maskinen. Maskinen virker også uten kamera, og styringen bruker ikke bildene ennå.

### Sammenligning

| | v0 (N2) | v1 (N3) |
|---|---|---|
| Om morgenen | Vei og bland en levain (5 min) | 1–2 ss surdeig og velg tid (3 min) |
| Må være hjemme | Hele kvelden: start, saltlake etter 45 min og forming ca. 4 timer senere | Bare ved forming |
| Tidspunkt for forming | Blir når det blir, ca. 4–5 timer etter start | Du velger selv, innenfor et vindu |
| Veiing | Du veier alt | Maskinen veier alt |
| Salt | Du blander saltlaken og heller den i når maskinen piper | Maskinen veier saltet og lager saltlaken selv |
| Aktiv tid per brød (uten steking) | 45–60 min | ca. 30 min |
| Ellers | – | Fyll mel før annenhver baking, salt sjelden |

## Hva som må til for scenario 2

| Funksjon | Hva den må klare | Slik er det løst i v1 | Avgjøres av |
|---|---|---|---|
| **Dosering av mel** | ±1 % på 490 g og ±2 g på levainen. Melet må ikke henge seg opp. | Én beholder med melblanding, vannrett skrue med røreverk og klaff, stoppet av vekta. Simulert: ±0,4 g. | E11 |
| **Dosering av vann** | ±1 % | Peristaltisk pumpe styrt av vekta. Vannet tempereres ikke: maskinen varmer deigen i stedet. | E12 |
| **Salt og saltlake** | ±0,5 g av 11 g, løses i ca. 45 g vann | Saltskrue fra en tett boks. Saltet og vannet doseres rett på deigen. | E12 |
| **Levain i formen fra 1–2 ss** | Fermentolyse med levain i formen gir like godt brød | Levainen bygges i brødformen og blandes med eltebladet | E04 |
| **«Levainen er klar»-signal** | Vite når levainen er klar, uten flytetest | Modellen og læringen. Laget er for tynt til å måles. | E02, E03 |
| **Fermenteringsmodell** | Forutsier levain og bulk innenfor ±1 t ut fra temperatur og blandingsforhold | [Gjæringsmodellen](forskning/v1-gjaeringsmodell.md), testet i simulering | E02 |
| **Hevemåling** | Bulkhevingen innenfor ±5 prosentpoeng | ToF i taket, glattet over 3 min, nullpunkt etter siste bretting. Kameraet kommer i tillegg. | E14 |
| **Feilvarsling** | Grove feil oppdages | Vekta (tomt for mel, salt eller vann), motorstrømmen, døra og nødstoppen. Senere kameraet. | E15, E18 |
| **Ventevindu** | Hvor lenge deigen tåler å vente ved romtemperatur | Ikke løst ennå | E16 |
| **Tidsplanlegger og prognose** | Planlegger baklengs, justerer temperaturen og sier fra om tiden ikke går | [`firmware/v1`](../firmware/v1/README.md), testet med hele simulerte bakedager | Første bakinger |
| **Brukergrensesnitt** | Velge tidspunkt og se planen og prognosen | Dreieknapp og skjerm på maskinen, nettside, Home Assistant og varsler på mobilen | Fastvare v1 |
| **Plass til beholderne** | Mel, salt og vann uten å komme i veien for formen | Vann i tårnet, mel og salt over taket, utløp med klaffer i taket ([`hardware/v1`](../hardware/v1/README.md)) | Bygget |
| **Hygiene** | Tette og tørre beholdere for mel og salt, utenfor det fuktige kammeret. Vanntank som fylles hver bakedag. | Klaffer holder fuktig luft ute av melet. Pumpa tømmer slangen baklengs. | [`06-sikkerhet.md`](06-sikkerhet.md) |

Når dette er bekreftet med ekte bakinger, er maskinen på nivå N3 ([`00-visjon-og-suksesskriterier.md`](00-visjon-og-suksesskriterier.md)), som er målet for prototype v1 i [veikartet](04-veikart.md).
