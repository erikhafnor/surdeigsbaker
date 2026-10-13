# 00 – Visjon, suksesskriterier og rammer

## Visjon

> En maskin på kjøkkenbenken som lager et skikkelig surdeigsbrød – med sprø, mørk skorpe og saftig krumme – med så lite manuelt arbeid som mulig. Maskinen er åpen kildekode og godt nok dokumentert til at andre kan bygge sin egen.

Prosjektet starter med én konkret oppskrift som referanse («Det Ultimate Surdeigsbrød v7.0», se [`oppskrifter/referanse-v7.md`](../oppskrifter/referanse-v7.md)). Målet er ikke en maskin som etterligner hendene til en baker, men en maskin som gjør det samme *for brødet*.

## Hva betyr «i mål»?

Suksess er en **ferdig prototype på kjøkkenbenken som har laget sine første surdeigsbrød**. For å gjøre det målbart deler vi automasjonen inn i nivåer:

| Nivå | Navn | Hva maskinen gjør | Hva mennesket gjør |
|---|---|---|---|
| **N0** | Instrumentert manuell baking | Logger temperaturer og heving | Alt |
| **N1** | Assistert | Holder temperatur (hevekammer), varsler | Blander, former og steker |
| **N2** | Ett trykk, manuelt veid | Elter, hever, (kjøler), overfører og steker | Veier mel, vann, salt og surdeig og heller det i |
| **N3** | Doserer selv | Doserer mel, vann og salt, bygger levain i bollen og gjør resten | Tilsetter 1 ss surdeig og fyller på beholdere |
| **N4** | Steller surdeigen | Som N3, og holder i tillegg surdeigskulturen i live | Fyller på og vasker ukentlig |
| **N5** | Bakeri | Former og snitter også, gir frie former | Spiser |

| Mål | Nivå | Kommentar |
|---|---|---|
| Minimum (MVP) | **N2** | Det som absolutt må til for at prosjektet er i mål |
| **Mål for prototype v1** | **N3** | Anbefalt ambisjonsnivå |
| Strekkmål | N4 | Egen surdeigsmodul («Surhild-modulen») |
| Senere versjoner | N5 | Krever forming, som er det vanskeligste å automatisere |

### Akseptansekriterier for «første surdeigsbrød»

Prototypen er i mål når **alle** punktene under er oppfylt:

1. **Ett startpunkt:** Bakingen startes med én kommando, eller planlegges som «ferdig kl. 07:00». Etter det er det ingen manuelle steg, med unntak av dem som er tillatt på valgt nivå.
2. **Lite manuelt arbeid:** ≤ 15 min aktiv tid per brød på N2 og ≤ 5 min på N3, ikke medregnet rengjøring.
3. **Gjennomstekt:** Kjernetemperatur ≥ 96 °C, målt med stikktermometer.
4. **Kvalitet:** ≥ 70 % av referansebrødets poengsum på brødkortet (se under). Referansebrødet er v7.0 bakt for hånd i fase 0.
5. **Repeterbarhet:** 3 godkjente brød på rad, med full logg for hvert.
6. **Sikkerhet:** Alle punktene i sikkerhetssjekklisten ([`06-sikkerhet.md`](06-sikkerhet.md)) er bestått, inkludert testede termosikringer og minst én natt med ubemannet drift uten avvik.
7. **Dokumentert:** Stykkliste (BOM), koblingsskjema, fastvare og byggenotater ligger i repoet.

### Brødkortet (kvalitetsmåling)

Hvert brød får poeng fra 1 til 5 på hvert kriterium. Der det er mulig, brukes en objektiv måling.

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
| Størrelse | B ≤ 60 cm, D ≤ 50 cm, H ≤ 50 cm | Må få plass på benken. **Mål din egen benk.** Over stekesonen må det være klaring og god ventilasjon. Overskap over maskinen må vurderes særskilt, se [`06-sikkerhet.md`](06-sikkerhet.md). |
| Strøm | Én 230 V-stikkontakt, ≤ 2000 W topp | En vanlig 10 A-kurs tåler maks ca. 2300 W, og noe annet kan være koblet til samme kurs |
| Brødstørrelse | 1 brød, ca. 1 kg deig (550 g mel) | Som referanseoppskriften |
| Støy | Stille om natten (≤ ca. 40 dB under heving) | Kjøkkenet er ofte nær soverom |
| Rengjøring | Alle deler i kontakt med mat er avtakbare, helst tåler de oppvaskmaskin | Hygiene og at maskinen faktisk blir brukt |
| Påfylling | Mel og salt for ≥ 4 brød (N3) | Ukentlig rutine |
| Matkontakt | Bare godkjente materialer (rustfritt stål, matgodkjent silikon, emalje). PTFE bare i kalde soner. Ikke ubehandlet aluminium eller 3D-print. | Se [`06-sikkerhet.md`](06-sikkerhet.md) |
| Ubemannet drift | Trygg å la stå over natten | To uavhengige sikkerhetslag (maskinvare og programvare) |
| Byggbarhet | Standarddeler, 3D-print bare utenfor matkontakt og varmesoner, ingen spesialverktøy utover vanlig makerspace | Målet er DIY |
| Budsjett | Prototype v1: ca. 7 000–19 000 kr i deler. Hele prosjektet, inkludert måleoppsett og skjelett: ca. 13 000–34 000 kr (grovt anslag). | Se [`09-budsjett-og-innkjop.md`](09-budsjett-og-innkjop.md). Fastsettes ved G0. |

## Utenfor omfang (i v1)

- Flere brød samtidig, baguetter eller formbrød med frø og topping
- Kommersiell produksjon, CE-merking og salg (vurderes senere, se [`06-sikkerhet.md`](06-sikkerhet.md))
- Fri forming og snitting med robot (N5)
- Malte korn og egen kvern

## Designprinsipper

1. **Tilpass oppskriften til maskinen, ikke maskinen til oppskriften.** Vi lager en *maskinvennlig oppskrift* som gir like godt brød med færre og enklere håndgrep.
2. **Færrest mulig overføringer av deig.** Hver gang deigen må flyttes, får vi et nytt robotproblem: deig er klissen, myk og lett å ødelegge.
3. **Mål, ikke gjett.** Hver baking logges. Hvert brød er et datapunkt.
4. **Sikkerhet i maskinvare først.** Programvaren er andre forsvarslinje. Varmeelementer skal ha uavhengige termosikringer.
5. **Smalt først, bredt senere.** Én oppskrift, én melsort og ett brød. Variasjoner kommer når grunnmuren står.
6. **Modulært og reparerbart.** Standarddeler, skruer framfor lim og tydelige grensesnitt mellom modulene.
7. **Dokumenter mens du bygger.** Det er mye enklere enn å dokumentere i etterkant, og det er dokumentasjonen som gjør prosjektet til et DIY-prosjekt.
