# Eltemekanisme for v1

Sist undersøkt: 2026-10-16

*Metode: En research-agent søkte på nettet. Bare GitHub-sider kunne leses i sin helhet. Det som bare er sjekket i søkemotorens sammendrag, er merket **(søk)**. **UVERIFISERT** betyr at det ikke ble funnet noen kilde.*

## Sammendrag

- **En brødmaskinform med elteblad i bunnen er et godt valg for v1.** Det er en velprøvd måte å elte 1–1,3 kg deig på. Formen tas ut, og lokket blir ledig for doseringen og sensorene.
- **Formfamilie: Panasonic XL** (SD-2500, SD-2501 og SD-ZB2502, brød på ca. 1,2 kg).
  - Den er vanlig brukt i Norge og Storbritannia, og akselen, koblingen og eltebladet selges som reservedeler.
  - Fra SD-2511 og SD-ZB2512 kan formen ADA12E1651 brukes.
- **Kjøp en brukt maskin som giver** (180–500 kr på Finn.no). Kjør deigen din i maskinens eget deigprogram og mål alt før du lager CAD. Helst kjøper du to like maskiner: én til referanse og én til å ta fra hverandre.
- **To risikoer:**
  - Oppskriften ligger på Panasonics grense på 600 g mel. v1 bruker derfor 560 g som standard.
  - Ingen kilder viser at et elteblad kan gjøre forsiktig bretting under bulkhevingen. Det må testes (E05, E17).

## Formene som reservedeler

| Modell | Del | Pris (søk) |
|---|---|---|
| Panasonic SD-2500/2501/ZB2502 | Aksel med lager og pakning i formen, ADA29E165 | Ca. 38 £ (YPC, UK) |
| Samme | Koblingen i maskinen («base connector») | Ca. 21 £ (eBay) |
| Samme | Elteblad ADD96E160 | eBay |
| Panasonic SD-2511/ZB2512/ZX2522 | Form med aksel, ADA12E1651 | Ca. 107 £ ny |
| Panasonic SD-R2530/YR2550 (i produksjon) | Form ADA12E226 | Ca. 120 €. Bare ca. 1 kg deig. |
| Kenwood BM350/BM450 | Form KW712245 | Ca. 30 £ |
| Unold Backmeister 68520 | Form 6852070 | Ca. 57 €. Tar 1,0–1,5 kg deig. Reserve hvis Panasonic elter dårlig når formen er full. |

- **Holderen som formen låses fast i, selges ikke separat** (UVERIFISERT for alle merker). Den må tas fra en giver eller lages selv. **v1 lager den selv**: den printes etter mål fra den ekte formen.
- **Panasonic-formen låses** ved å dreie den litt med klokka og løsnes ved å dreie mot klokka og løfte (bruksanvisningen, søk).
- **Typiske feil:**
  - Pakningen rundt akselen lekker.
  - Akselen blir stiv. Hele akselenheten byttes.
  - Fatningen i eltebladet slites.
  - Koblingen ruster fast.
  - Formen tåler ikke oppvaskmaskin (søk).

## Fart og moment

- Brødmaskiner gearer motoren ned til ca. **230 o/min og ca. 2,9 N·m** på eltebladet (patent US 5,364,183, søk). Det er ca. 70 W på akselen.
- Motorene er ofte 50–90 W vekselstrømsmotorer med reim.
- Eltemønstre:
  - Sanyo SBM-20 ([elfnor/arduino-bread](https://github.com/elfnor/arduino-bread)): 6 min pulsblanding (200 ms på, 1 s av), 29 min elting, og senere slag for å slå sammen deigen (5 s på, 10 s av, 5 s på).
  - Ingen vanlige brødmaskiner ble bekreftet å skifte retning.
- **Anbefaling for v1** (anslag): minst 4 N·m kontinuerlig og 10 N·m kortvarig på eltebladet, 0–200 o/min, med strømmåling og omdreiningsteller.

## Våt surdeigsdeig i brødmaskin

- **For:**
  - King Arthur anbefaler brødmaskin til svært klissen deig som ciabatta, fordi den er skånsom, som en spiralelter (2007, søk).
  - Brukere på The Fresh Loaf har fått åpen krumme med «svært våt» deig (søk).
- **Mot:**
  - Tørt mel blir liggende i hjørnene. Bakere skraper ned etter ca. 5 min (søk).
  - Brødmaskiner er laget for tørrere loffdeig (forum, søk).
- **Ingen målinger ved 75–80 % hydrering ble funnet** (UVERIFISERT).
- **Tiltak i v1:**
  - Mel doseres gradvis mens eltebladet går sakte, og vannet går først.
  - Pause med kort retningsskift for å få med melet i hjørnene.
  - Kameraet ser etter tørt mel (E18).

## Alternativer

| Alternativ | Minste deig | Pris (søk) | Vurdering |
|---|---|---|---|
| Spiralelter (Famag IM-5, Ooni Halo Pro) | 0,3–0,9 kg | 680–900 € | Best for våt deig, men 230 V, og hodet sperrer for dosering ovenfra |
| Ankarsrum | Valsen virker under ca. 1,8 kg | Ca. 8 000 kr | Vanskelig å kopiere |
| Planetrører | Små porsjoner fungerer dårlig | – | Komplisert, og sperrer for dosering |

## Åpne prosjekter

| Prosjekt | Hva det gjør |
|---|---|
| [elfnor/arduino-bread](https://github.com/elfnor/arduino-bread) | Arduino styrer en Sanyo-maskin for surdeig med lang og fleksibel tid |
| [stevescot/ESPBreadMaker](https://github.com/stevescot/ESPBreadMaker) (2025) | ESP32 styrer maskinens egen motor og varme. Brettingen gjør brukeren selv. |
| [mirecrane/dough_mixer](https://github.com/mirecrane/dough_mixer) (2026) | Nærmest vår plan: ESP32-S3 doserer mel (ca. 5 g/s) og vann (ca. 10 g/s), og en elektromagnet holder formen |

Ingen prosjekter ble funnet som driver en brødmaskinform med egen likestrøms girmotor.

## Mål på den ekte delen før CAD

1. **Formen:** utvendige mål, låseknastene, låsevinkel og -retning, hvor høyt den sitter, sentrering og vekt.
2. **Koblingen:** medbringeren under formen og koblingen i maskinen, med pinneavstand og -diameter, hvor dypt de griper, aksialt slark, akseldiameter og hvordan den er festet.
3. **Drivverket:** reimskivene, reimas deling og bredde, og utvekslingen.
4. **Moment:** friksjon i tom aksel, moment i deigen ved start og ved slutt, og når motoren stopper.
5. **Retningsskift:** om formen løsner når eltebladet går baklengs.
6. **Åpningen:** innvendige mål på formens åpning, for innløpene og hevesensoren.
7. **Eltebladet:** hvordan det sitter på akselen, og om det følger med deigen ut.
