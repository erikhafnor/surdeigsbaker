# 00 – Visjon, suksesskriterier og rammer

## Visjon

> En maskin på kjøkkenbenken som tar seg av alt det tidkrevende med et surdeigsbrød: levain, elting, heving med bretting og kald heving. Den leverer **stekeklar deig til tidspunktet du har bestemt**. Selve stekingen gjør du i **din vanlige ovn**, med jerngryte, akkurat som i dag. Maskinen er åpen kildekode og godt nok dokumentert til at andre kan bygge sin egen.

Prosjektet starter med én konkret oppskrift som referanse («Det Ultimate Surdeigsbrød v7.0», se [`oppskrifter/referanse-v7.md`](../oppskrifter/referanse-v7.md)). Målet er ikke en maskin som etterligner hendene til en baker, men en maskin som gjør det samme *for deigen*.

### Avgrensning: maskinen slutter ved ovnsdøra

Maskinen gjør alt fra surdeig til **stekeklar deig**. Stekingen skjer i en vanlig ovn ([ADR-006](beslutninger/ADR-006-steking-i-vanlig-ovn.md)).

| Maskinen | Du |
|---|---|
| Bygger levain, blander, autolyserer og elter | (N2: veier og heller i ingrediensene) |
| Styrer bulkhevingen med temperatur og bretting, og måler hevingen | (Valgfritt: former deigen når maskinen sier fra) |
| Kald heving, og holder deigen kald til du er klar | |
| **Varsler: «Forvarm ovnen nå»** og «Deigen er klar» | Forvarmer ovnen med gryta, tipper deigen i, snitter og steker |

Det betyr at maskinen **ikke** trenger ovn, varmeelement på 250 °C eller gryte. Den blir mindre, billigere og stillere, og brannrisikoen blir *mye* lavere. Skorpa blir like god som i dag, fordi stekingen er den samme.

## Hva betyr «i mål»?

Suksess er en **ferdig prototype på kjøkkenbenken som har laget deigen til sine første surdeigsbrød**, bakt i vanlig ovn. For å gjøre det målbart deler vi automasjonen inn i nivåer:

| Nivå | Navn | Hva maskinen gjør | Hva mennesket gjør (i tillegg til å steke) |
|---|---|---|---|
| **N0** | Instrumentert manuell baking | Logger temperaturer og heving | Alt |
| **N1** | Smart hevekabinett | Holder temperaturen (varme **og** kjøling), planlegger og varsler | Blander, elter, bretter og former |
| **N2** | Deigmaskin | Elter, bulkhever med bretting, kjøler og holder deigen kald | Veier og heller i ingrediensene, og former eventuelt |
| **N3** | Doserer selv | Doserer mel, vann og salt, bygger levain i bollen og gjør resten | Tilsetter 1 ss surdeig, fyller på beholdere og former eventuelt |
| **N4** | Steller surdeigen | Som N3, og holder i tillegg surdeigskulturen i live | Fyller på og vasker ukentlig |
| **N5** | Former selv | Leverer en ferdig formet deig i hevekurv | Steker |

| Mål | Nivå | Kommentar |
|---|---|---|
| Første nyttige milepæl | N1 | Hevekabinettet fra fase 1 er allerede nyttig i hverdagen |
| Minimum (MVP) | **N2** | Det som absolutt må til for at prosjektet er i mål |
| **Mål for prototype v1** | **N3** | Anbefalt ambisjonsnivå |
| Strekkmål | N4 | Egen surdeigsmodul («Surhild-modulen») |
| Senere versjoner | N5 | Forming er det vanskeligste å automatisere |

### Overlevering: to varianter

Mennesket er uansett til stede når brødet skal i ovnen. Derfor støtter maskinen to måter å overlevere deigen på. Eksperiment E06 avgjør hvilken som blir standard.

1. **Uten forming** («tipp og stek»): Deigen bulkheves og kaldheves i den avtakbare bollen. Ved stekeklar tid tipper du den kalde deigen rett i den varme gryta. Det er bare ett manuelt grep.
2. **Med forming** (som referansen): Maskinen sier fra når bulkhevingen er ferdig. Du former deigen på 2–5 min og legger den i en hevekurv, som settes tilbake i maskinens kalde kammer. Maskinen etterhever og kaldhever, og varsler når ovnen skal forvarmes. Det gir to korte manuelle grep og best kvalitet.

### Akseptansekriterier for «første surdeigsbrød»

Prototypen er i mål når **alle** punktene under er oppfylt:

1. **Ett startpunkt:** Prosessen startes med én kommando, eller planlegges som «stekeklar kl. 07:00». Etter det er det ingen manuelle steg, med unntak av dem som er tillatt på valgt nivå.
2. **Lite manuelt arbeid:** ≤ 20 min aktiv tid per brød på N2 og ≤ 10 min på N3. Stekingen og rengjøringen er ikke medregnet.
3. **Presis tidsplan:** Deigen er stekeklar innen ±30 min av planlagt tid, og den kan holdes kald i minst 12 t uten tydelig kvalitetstap (E16).
4. **Kvalitet:** ≥ 80 % av referansebrødets poengsum på brødkortet (se under). Referansebrødet er v7.0 laget for hånd i fase 0. Stekingen er den samme, så forskjellen skyldes bare deigen. Derfor er kravet høyere enn om maskinen også stekte.
5. **Repeterbarhet:** 3 godkjente brød på rad, med full logg for hvert.
6. **Sikkerhet:** Alle punktene i sikkerhetssjekklisten ([`06-sikkerhet.md`](06-sikkerhet.md)) er bestått, inkludert testede termosikringer og minst én natt med ubemannet drift uten avvik.
7. **Dokumentert:** Stykkliste (BOM), koblingsskjema, fastvare og byggenotater ligger i repoet.

### Brødkortet (kvalitetsmåling)

Hvert brød får poeng fra 1 til 5 på hvert kriterium. Der det er mulig, brukes en objektiv måling. Stekingen gjøres alltid likt (samme ovn, gryte og profil), slik at brødkortet måler deigen.

| Kriterium | Objektiv måling | Vekt |
|---|---|---|
| Volum | Spesifikt volum (ml/g), målt med frøfortrengning eller foto | 25 % |
| Ovnsspretthet og form | Forhold høyde/bredde, målt på foto | 15 % |
| Krumme | Snittfoto og poreandel (ImageJ/Python) | 20 % |
| Skorpe | Farge mot fargekort og sprøhet | 15 % |
| Smak og syrlighet | Smakspanel med familien, pH i krummen | 20 % |
| Gjennomstekt | Kjernetemperatur og at det ikke finnes rå partier | 5 % |

Mal: [`maler/bakelogg.md`](maler/bakelogg.md).

## Rammer (foreløpig kravspesifikasjon)

Rammene skal gjennomgås og fryses som *kravspesifikasjon v1* ved port G0 (se [veikartet](04-veikart.md)).

| Krav | Verdi (utkast) | Begrunnelse |
|---|---|---|
| Størrelse | B ≤ 45 cm, D ≤ 45 cm, H ≤ 45 cm | Skal stå på benken under overskapene. Uten ovn er det ingen krav til klaring for varme. **Mål din egen benk.** |
| Strøm | Én 230 V-stikkontakt, ≤ 600 W topp | Eltemotor (100–400 W), kjøling (ca. 50–80 W) og svak varme (≤ 100 W). Fastvaren sørger for at de ikke går på full effekt samtidig. |
| Kammertemperatur | 4–30 °C, ±0,5 °C | Kald heving og -hold (4–6 °C), levain og bulk (24–27 °C) |
| Brødstørrelse | 1 brød, ca. 1 kg deig (550 g mel) | Som referanseoppskriften |
| Overlevering | Avtakbar bolle, og plass til en standard hevekurv (ca. 22–25 cm rund) i kammeret | De to overleveringsvariantene |
| Støy | Stille om natten (≤ ca. 40 dB under heving og kjøling) | Kjøkkenet er ofte nær soverom. Kompressoren er den største kilden. |
| Rengjøring | Alle deler i kontakt med mat er avtakbare, helst tåler de oppvaskmaskin | Hygiene og at maskinen faktisk blir brukt |
| Påfylling | Mel og salt for ≥ 4 brød (N3) | Ukentlig rutine |
| Matkontakt | Bare godkjente materialer (rustfritt stål, matgodkjent silikon, PTFE-belegg (non-stick), emalje). Ikke ubehandlet aluminium eller 3D-print. | Se [`06-sikkerhet.md`](06-sikkerhet.md) |
| Ubemannet drift | Trygg å la stå over natten | To uavhengige sikkerhetslag (maskinvare og programvare) |
| Byggbarhet | Standarddeler, 3D-print bare utenfor matkontakt, ingen spesialverktøy utover vanlig makerspace | Målet er DIY |
| Budsjett | Prototype v1: ca. 5 600–14 000 kr i deler. Hele prosjektet, inkludert hevekabinett og skjelett: ca. 12 000–29 000 kr (grovt anslag). | Se [`09-budsjett-og-innkjop.md`](09-budsjett-og-innkjop.md). Fastsettes ved G0. |

## Utenfor omfang (i v1)

- **Steking.** Det gjøres i vanlig ovn ([ADR-006](beslutninger/ADR-006-steking-i-vanlig-ovn.md)). Maskinen kan senere *varsle* eller *integreres* med en smartovn (se [`07-arkitektur.md`](07-arkitektur.md)), men den varmer aldri opp til steketemperatur selv.
- Flere brød samtidig, baguetter eller formbrød med frø og topping
- Kommersiell produksjon, CE-merking og salg (vurderes senere, se [`06-sikkerhet.md`](06-sikkerhet.md))
- Forming og snitting med robot (N5)
- Malte korn og egen kvern

## Designprinsipper

1. **Tilpass oppskriften til maskinen, ikke maskinen til oppskriften.** Vi lager en *maskinvennlig oppskrift* som gir like godt brød med færre og enklere håndgrep.
2. **Færrest mulig overføringer av deig.** Hver gang deigen må flyttes, får vi et nytt robotproblem: deig er klissen, myk og lett å ødelegge. Den beste overføringen er den mennesket gjør på vei til ovnen.
3. **Mennesket er til stede ved ovnen, så bruk det.** Det maskinen sparer mest tid på, er ventingen og passingen. De korte grepene (forming og snitting) kan mennesket gjøre når det likevel er der.
4. **Mål, ikke gjett.** Hver baking logges. Hvert brød er et datapunkt.
5. **Sikkerhet i maskinvare først.** Programvaren er andre forsvarslinje. Også små varmeelementer skal ha uavhengige termosikringer.
6. **Smalt først, bredt senere.** Én oppskrift, én melsort og ett brød. Variasjoner kommer når grunnmuren står.
7. **Modulært og reparerbart.** Standarddeler, skruer framfor lim og tydelige grensesnitt mellom modulene.
8. **Dokumenter mens du bygger.** Det er mye enklere enn å dokumentere i etterkant, og det er dokumentasjonen som gjør prosjektet til et DIY-prosjekt.
