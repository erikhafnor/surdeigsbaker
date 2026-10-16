# Gjæringsmodell for tidsplanleggeren (v1)

Sist undersøkt: 2026-10-16

*Metode: En research-agent leste åpne kalkulatorer på GitHub og søkte etter forskning og bakerdata. Det som bare er sjekket i søkemotorens sammendrag, er merket **(søk)**. Modellen i avsnitt 4 er tilpasset kildene av oss og er **ikke validert** mot egne bakinger ennå. Koden ligger i [`firmware/v1/components/bakeplan/`](../../firmware/v1/components/bakeplan/).*

## Hovedfunn

1. **Temperaturen virker ikke likt overalt.**
   - Gjæringen går ca. 3–3,5 ganger fortere per 10 °C mellom 18 og 24 °C.
   - Den går ca. 2,4 ganger fortere mellom 22 og 26 °C, og ca. 1,8 ganger mellom 24 og 28 °C.
   - Over ca. 28 °C går den nesten ikke fortere, fordi gjæren i surdeigen har optimum rundt 27 °C (Gänzle mfl. 1998).
   - Mer varme over 28 °C gir altså nesten ingenting.
2. **Halverer du mengden surdeig, legger du til omtrent et fast antall timer.** Tiden øker med logaritmen av fortynningen.
3. **Mengden surdeig du starter med, bestemmer det meste av totaltiden.**
   - 20 g surdeig skal «kolonisere» ca. 1 100 g deig. Det er ca. 55 ganger så mye, uansett hvordan du fordeler matingen.
   - Forholdet i levainen flytter tid mellom levain og bulkheving, men endrer totaltiden lite.
4. **Med 1 ss kald surdeig kl. 07 kan deigen tidligst være klar ca. kl. 17:30–18:00.**
   - For å nå kl. 17 trengs 2 ss (40 g) eller en surdeig som ble matet kvelden før.
   - Maskinen veier surdeigen, så den vet nøyaktig hvor mye du har lagt i. En spiseskje kan variere ±30 %.
5. **Hvor aktiv surdeigen er, er den største usikkerheten** (ca. ±30 %). Den læres fra hevingen og huskes fra baking til baking.

## 1. Forskning

- **Gänzle, Ehmann og Hammes (1998)**, *Appl Environ Microbiol* 64:2616, doi:10.1128/aem.64.7.2616-2623.1998:
  - Vekstmodeller for melkesyrebakterien *L. sanfranciscensis* og gjæren *C. milleri*. Optimum er 32–33 °C for bakteriene og 27 °C for gjæren.
  - 4 % salt stopper bakteriene, mens gjæren tåler 8 % (søk).
  - Temperaturmodellen er μ = a·x^b·e^(−c·x), der x = Tmax − T.
- **Romano mfl. (2007)**, *J Food Eng* 83:142: En modifisert Gompertz-kurve beskriver deigvolumet best: forsinkelse, så lineær fase, så avtagende (søk).
- **Akdogan og Özilgen (1992):** Logistisk vekst, gassproduksjon og volumøkning for surdeig ved 10–30 °C (søk).
- **Det finnes ingen fagfellevurdert modell** som knytter tid til topp for en levain i hjemmeskala til både mengde surdeig og temperatur.

Hastighet relativt til 24 °C (en blanding av gjær- og bakteriemodellen, tilpasset bakerdata):

| °C | 18 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 30 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Hastighet | 0,50 | 0,64 | 0,73 | 0,82 | 0,91 | 1 | 1,08 | 1,16 | 1,22 | 1,26 | 1,30 |

## 2. Bakerdata

- **Levain til topp ved ca. 24 °C** (søk; kildene sprer seg):

  | Forhold | Timer |
  |---|---|
  | 1:1:1 | ca. 4–6 |
  | 1:2:2 | ca. 5,5–8 |
  | 1:5:5 | ca. 8–14 |
  | 1:10:10 | ca. 10–24 |

  Kald surdeig fra kjøleskapet er tregere og mindre forutsigbar, men det ble ikke funnet tall for hvor mye.

- **Bulkheving:**
  - The Sourdough Journey bruker tidtabeller fra over 60 bakinger. Varm deig stoppes ved lavere heving, fordi den fortsetter å gjære etterpå:

    | Deigtemperatur | Heving |
    |---|---|
    | 27 °C | +30 % |
    | 25 °C | +40 % |
    | 24 °C | +50 % |
    | 22 °C | +65 % |
    | 21 °C | +75 % |

  - Andre kilder er raskere, f.eks. Weekend Bakery: 4–5 t ved 24 °C med 20 % surdeig (søk).
- **Sammalt mel** går litt fortere, og **salt** bremser lite (ca. 9 % ved 1,5 %), så fermentolysen uten salt er ikke et tidsgrep (søk).
- **Hvor lenge deigen kan vente** etter bulkhevingen: ingen tall funnet. Modellen anslår ca. 1 t ved 21 °C fra +30 til +40 % heving.

## 3. Åpne kalkulatorer

| Repo | Modell | Lisens |
|---|---|---|
| [bannon52/sourdough_bulk_fermenter](https://github.com/bannon52/sourdough_bulk_fermenter) (Home Assistant) | Q10 = 2, √(0,20/s) | Ingen lisensfil |
| [YAMIR-1138/dough_formulator](https://github.com/YAMIR-1138/dough_formulator) | Q10 = 2,5, (20/s)^0,4 | MIT |
| [Alexbl00m/dough-designer-pro](https://github.com/Alexbl00m/dough-designer-pro) | t = k(T)·log₂(S*/s), tabell for 10–29 °C | Ingen lisensfil |
| [christinepamela/sourdough-sensor](https://github.com/christinepamela/sourdough-sensor) | ToF og «trapp»-deteksjon av topp | Ingen lisensfil |

Ingen av dem lærer av målt heving og planlegger baklengs med bare varme. Det gjør v1.

## 4. Modellen i v1

Arbeidet regnes i **referansedoblinger**. Én dobling tar k = 1,57 t ved 24 °C og 1,57 t / hastighet(T) ved temperaturen T.

| Trinn | Antall doblinger |
|---|---|
| Levain til ×2 | N = L + 1,6·log₂(D) |
| Bulkheving fra deigen blandes til hevingen R | N = maks(1,2; 3,3 + 1,6·log₂(20/s) + log₂(R/30)) |

- **D** = levainens masse / surdeigens masse.
- **L** = 1,4 for kald surdeig og 0,4 for surdeig som er matet kvelden før.
- **s** = levain / mel i hoveddeigen, i %.
- **R** hentes fra tabellen over (The Sourdough Journey) og avhenger av temperaturen.
- **Aktiviteten** til surdeigen deler tiden. Den er 1 i modellen og læres fra hevingen.

Planleggeren velger:

- **Levainens forhold** (1:1,25:1,25, 1:2,5:2,5 eller 1:5:5), slik at forgjæret mel holdes rundt 10 % (4–20 %).
- **Én temperatur** midt mellom romtemperaturen og 28 °C, slik at det er spillerom begge veier.
- **Utsatt start** hvis målet er sent.

Planen sikrer også minst 1 t målt bulkheving etter brettingen, slik at regulatoren rekker å rette opp.

**Underveis** følger regulatoren hevingen, lærer aktiviteten og justerer temperaturen mot måltiden:

- **Levainen** er bare et tynt lag i formen og måles ikke. Den styres av modellen og den lærte aktiviteten.
- **Bulkhevingen** måles fra en ny baseline etter siste bretting. Regulatoren regner med hevingen som skjedde før baselinen.

### Simuleringen

[`firmware/v1/test/planner_test.cpp`](../../firmware/v1/test/planner_test.cpp) simulerer:

- en surdeig som er tregere eller raskere enn modellen
- en deigtemperatur som henger etter settpunktet og aldri går under romtemperaturen
- bretting som skjuler hevingen
- målestøy på ±6 %

| Tilfelle | Resultat |
|---|---|
| Deigens heving når den meldes klar, med sensor | 96–104 % av målet i vanlige tilfeller. 132 % med svært rask surdeig og 40 g startmengde. |
| Uten hevesensor (bare modellen) | 47–184 % av målet. **Sensoren er nødvendig.** |
| Tidsfeil ved første baking, typisk surdeig (aktivitet 0,85–1,15) | Innenfor ca. ±40 min |
| Etter én baking med læring | Innenfor ca. 10 min, også med aktivitet 0,7 eller 1,4 |
| Mål nær det tidligst mulige | Maskinen sier fra ved start at planen har liten margin (`late_risk_h`) |

Med 20 g kald surdeig og 21 °C i rommet gir modellen dette tidsvinduet for start kl. 07:00:

| Surdeig | Tidligst klar |
|---|---|
| 20 g kald | 17:30 |
| 40 g kald | 15:57 |
| 20 g matet kvelden før | 16:15 |

Senest klar er ca. kl. 08 neste morgen, med fortynnet levain, romtemperatur og utsatt start.

## 5. Ikke verifisert

- Tallene i modellen (1,6, 3,3, forsinkelsen for kald surdeig og den lærte aktiviteten).
- Tabellen for målhevingen.
- Hvor lenge deigen kan vente.

**Valideres med 5–10 loggførte bakinger** (temperatur og høyde) før standardverdiene låses.
