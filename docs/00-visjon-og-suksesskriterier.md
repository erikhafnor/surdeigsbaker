# 00 – Visjon, suksesskriterier og rammer

## Visjon

> En maskin på kjøkkenbenken som tar seg av alt det tidkrevende med et surdeigsbrød: levain, blanding, elting og bulkheving med bretting. Den sier fra når **deigen er klar for forming**, helst til tidspunktet du har bestemt. Den kalde etterhevingen skjer i **ditt eget kjøleskap**, og stekingen i **din vanlige ovn**, med jerngryte, akkurat som i dag. Maskinen er åpen kildekode og godt nok dokumentert til at andre kan bygge sin egen.

Prosjektet starter med én konkret oppskrift som referanse («Det Ultimate Surdeigsbrød v7.0», se [`oppskrifter/referanse-v7.md`](../oppskrifter/referanse-v7.md)). Målet er ikke en maskin som etterligner hendene til en baker, men en maskin som gjør det samme *for deigen*.

### Avgrensning: maskinen slutter ved forming

Maskinen gjør alt fra surdeig til **deig som er klar for forming**. Den har ingen kjøling ([ADR-007](beslutninger/ADR-007-ingen-kjoling.md)), og stekingen skjer i en vanlig ovn ([ADR-006](beslutninger/ADR-006-steking-i-vanlig-ovn.md)).

| Maskinen | Du |
|---|---|
| Bygger levain, blander, autolyserer og elter | (N2: veier og heller i ingrediensene) |
| Styrer bulkhevingen med temperatur og bretting, og måler hevingen | |
| **Varsler: «Deigen er klar for forming»** | Former deigen, legger den i hevekurven og setter den i kjøleskapet (8–24 t) |
| | Forvarmer ovnen med gryta, tipper deigen i, snitter og steker |

Det betyr at maskinen **ikke** trenger ovn, varmeelement på 250 °C, gryte eller kjøling. Den blir mindre, billigere og stillere, kan drives av en ferdig 24 V-strømforsyning, og brannrisikoen blir *mye* lavere. Skorpa blir like god som i dag, fordi stekingen og den kalde etterhevingen er de samme.

## Hva betyr «i mål»?

Suksess er en **ferdig prototype på kjøkkenbenken som har laget deigen til sine første surdeigsbrød**, bakt i vanlig ovn. For å gjøre det målbart deler vi automasjonen inn i nivåer:

| Nivå | Navn | Hva maskinen gjør | Hva mennesket gjør (i tillegg til å steke) |
|---|---|---|---|
| **N0** | Instrumentert manuell baking | Logger temperaturer og heving | Alt |
| **N1** | Smart hevekabinett | Holder temperaturen, planlegger og varsler | Blander, elter, bretter og former |
| **N2** | Deigmaskin | Blander, elter, bulkhever med bretting og varsler når deigen er klar for forming | Veier og heller i ingrediensene, former og setter kurven i kjøleskapet |
| **N3** | Doserer selv | Doserer mel, vann og salt, bygger levain i formen og gjør resten | Tilsetter 1–2 ss surdeig, fyller på beholdere, former og setter kurven i kjøleskapet |
| **N4** | Steller surdeigen | Som N3, og holder i tillegg surdeigskulturen i live | Fyller på og vasker ukentlig |
| **N5** | Former selv | Leverer en ferdig formet deig i hevekurv | Steker |

| Mål | Nivå | Kommentar |
|---|---|---|
| Første nyttige milepæl | N1 | Hevekabinettet fra fase 1 er allerede nyttig i hverdagen |
| v0, første design | N2 | Bygges ikke ([ADR-010](beslutninger/ADR-010-v1-arkitektur.md)). Beholdt i [`hardware/v0/`](../hardware/v0/README.md). |
| Minimum (MVP) | **N2** | Det som absolutt må til for at prosjektet er i mål |
| **Prototype v1 (bygges nå)** | **N3** | Designet ligger i [`hardware/v1/`](../hardware/v1/README.md) ([ADR-010](beslutninger/ADR-010-v1-arkitektur.md)) |
| Strekkmål | N4 | Egen surdeigsmodul («Surhild-modulen») |
| Senere versjoner | N5 | Forming er det vanskeligste å automatisere |

Hvordan en bakedag ser ut for deg på N2 (v0) og N3 (v1), står i [`11-bruksscenarier.md`](11-bruksscenarier.md).

### Overlevering: to varianter

Maskinen gir fra seg deigen når bulkhevingen er ferdig. Eksperiment E06 avgjør hvilken av de to variantene under som blir standard.

1. **Med forming** (som referansen, standard i v1): Du former deigen på 2–5 min, legger den i en hevekurv og setter kurven i kjøleskapet til neste dag. Det gir best kvalitet.
2. **Uten forming** («tipp og stek»): Du setter plast over hele brødformen og setter den i kjøleskapet. Neste dag tipper du den kalde deigen rett i den varme gryta. Det er raskest, men eltebladet følger ofte med deigen ut, og du trenger en form til hvis du vil bake igjen før den er ledig.

### Akseptansekriterier for «første surdeigsbrød»

Prototypen er i mål når **alle** punktene under er oppfylt:

1. **Ett startpunkt:** Prosessen startes med én kommando, eller planlegges som «klar for forming kl. 20:00». Etter det er det ingen manuelle steg, med unntak av dem som er tillatt på valgt nivå.
2. **Lite manuelt arbeid:** ≤ 20 min aktiv tid per brød på N2 og ≤ 10 min på N3. Stekingen og rengjøringen er ikke medregnet.
3. **Presis tidsplan:** Deigen er klar for forming innen ±30 min av planlagt tid, og den tåler å vente minst 1 t ved romtemperatur uten tydelig kvalitetstap (E16).
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
| Størrelse | B ≤ 45 cm, D ≤ 45 cm, H ≤ 45 cm. **v1: 48 × 31 × 53 cm** (avvik i bredde og høyde, akseptert i ADR-010). | Skal stå på benken under overskapene. Uten ovn er det ingen krav til klaring for varme. v1 har dør foran og går under de fleste overskap, men må trekkes fram når melet fylles. Lavere i v2. **Mål din egen benk.** |
| Strøm | Én 230 V-stikkontakt med en CE-merket 24 V-strømforsyning. **v1: 221 W** (GST220A24). | Eltemotor (120 W), varme (60 W), steppere og pumpe. Fastvaren slår av varmen og doseringen mens motoren går, så toppen er ca. 130 W. Ingen 230 V inne i maskinen. |
| Deigtemperatur | Romtemperatur til 30 °C, ±0,5 °C. Bare varme. | Levain og bulk (24–27 °C). Ingen kjøling (ADR-007). |
| Brødstørrelse | 1 brød, ca. 1 kg deig (550 g mel) | Som referanseoppskriften |
| Overlevering | Avtakbar brødform. Hevekurven står i ditt eget kjøleskap. | De to overleveringsvariantene |
| Støy | Stille om natten (≤ ca. 40 dB under heving) | Kjøkkenet er ofte nær soverom. Uten kompressor er det bare motoren som lager lyd, og den går bare noen minutter. |
| Rengjøring | Alle deler i kontakt med mat er avtakbare, helst tåler de oppvaskmaskin | Hygiene og at maskinen faktisk blir brukt |
| Påfylling | Mel og salt for ≥ 4 brød (N3). **v1: mel for 2 brød** (ca. 1,5 kg), salt for ca. 35. Vannet fylles per baking. | Ukentlig rutine. v1 avviker for melet: en større beholder gjør maskinen høyere (ADR-010). |
| Matkontakt | Bare godkjente materialer mot deigen (rustfritt stål, matgodkjent silikon, PTFE-belegg (non-stick), emalje). Ikke ubehandlet aluminium eller 3D-print mot deigen. I v1 berører bare brødformen og eltebladet deigen. Printede deler som berører tørt mel og salt, er av naturfarget PETG etter EU 10/2011. | Se [`06-sikkerhet.md`](06-sikkerhet.md) |
| Ubemannet drift | Trygg å la stå over natten | To uavhengige sikkerhetslag (maskinvare og programvare) |
| Byggbarhet | Standarddeler, 3D-print ikke mot deigen, ingen spesialverktøy utover vanlig makerspace. v1 trenger en brukt brødmaskin som giver. | Målet er DIY |
| Budsjett | **v1: ca. 17 800 kr i deler** ([stykkliste](../hardware/v1/stykkliste.csv)), pluss frakt, giver og ca. 30 % buffer. | Se [`09-budsjett-og-innkjop.md`](09-budsjett-og-innkjop.md). |

## Utenfor omfang (i v1)

- **Steking.** Det gjøres i vanlig ovn ([ADR-006](beslutninger/ADR-006-steking-i-vanlig-ovn.md)). Maskinen kan senere *varsle* eller *integreres* med en smartovn (se [`07-arkitektur.md`](07-arkitektur.md)), men den varmer aldri opp til steketemperatur selv.
- **Kjøling og kald etterheving.** Det gjøres i ditt eget kjøleskap ([ADR-007](beslutninger/ADR-007-ingen-kjoling.md)).
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
