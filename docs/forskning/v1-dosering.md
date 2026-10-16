# Dosering av mel, salt og vann (v1)

Sist undersøkt: 2026-10-16

*Metode: En research-agent søkte på nettet. Bare GitHub-sider kunne leses i sin helhet. Det som bare er sjekket i søkemotorens sammendrag, er merket **(søk)**. **UVERIFISERT** betyr at det ikke ble funnet noen kilde. Regnestykker er merket **(beregnet)**. Kildelisten står i agentrapporten, og de viktigste lenkene er tatt med her.*

## Sammendrag

- **Ingen åpne prosjekter har vist at de kan dosere mel.** De som finnes, doserer milligram, gram eller granulat. Melskruen er derfor reell utviklingsjobb (E11). Reserveplanen er porsjoner du har veid på forhånd (N2), slik risikoregisteret allerede sier (R5).
- **Mel:** horisontal skrue i et U-trau (25–30 mm). Beholderen har bratte vegger og en lang innløpsåpning, og et langsomt røreverk sitter på samme motor. Vekta styrer: først grovfylling, så små pulser. Klaffen ved utløpet er stengt unntatt under dosering.
- **Salt:** en liten skrue (10 mm) fra en tett boks med fint bordsalt med antiklumpemiddel.
- **Vann:** peristaltisk 24 V-pumpe, styrt av vekta. Fylles per baking.
- **Vekt:** én lastcelle under hele formen med drivverket, lest av NAU7802 (støttet i ESPHome siden 2024.10). Tarer før hver tilsetning, og bare når motor, vifte og varme står stille.

## 1. Mel

### Andre løsninger

- **Rotimatic:** Den største feilkilden er fukt og sammenpresset mel ved utløpet. De anbefaler å rengjøre melkanalen hvert 2.–3. døgn og godkjenner bare noen melmerker (søk).
- **Industrielle skruefyllere:** Tallene er ±1–2 % med deler av rustfritt stål. Et horisontalt røreverk fyller skruen og hindrer brodannelse. Bratt trakt og stort trau. Lang skrue mot drypp. Det finnes egne patenter for mel som danner bro (søk).
- **Fôrautomater for dyr:** Det hjelper å kjøre skruen et halvt omdreining baklengs før dosering (søk). Mel har det motsatte problemet av tørrfôr: Det setter seg ikke fast, men danner bro.

### Hvordan mel oppfører seg

- **Romvekten varierer mye:** fra ca. 530 kg/m³ løst til ca. 880 kg/m³ sammenpresset (søk). Melet setter seg i beholderen mellom bakingene. Dosering etter omdreininger alene kan derfor bomme med flere titalls prosent. **Vekta må styre** (beregnet).
- **Brodannelse avhenger av fukt.** Mel med 14 % fukt trengte en åpning på 122 mm for ikke å danne bro, mot 86 mm ved 8,6 % fukt (søk).
- **Dugg:** Luft fra kammeret (26 °C, ca. 85 % RF) har duggpunkt ca. 23 °C. Den kondenserer på en romtemperert melkanal, og da blir melet til klister. **Utløpet må holdes stengt.**

### Åpne prosjekter verdt å lære av

- [guiguijke/OpenPowder](https://github.com/guiguijke/OpenPowder) har den best dokumenterte styringen: rask fylling til 80–95 %, 300–500 ms pause, og så pulser med 1/3, 1/10 og 1/20 av farten opp til 97 % og 99,5 %. Den doserer krutt, ikke mat.
- [jaapp/smart-grind-by-weight](https://github.com/jaapp/smart-grind-by-weight) er en kaffekvern med ESP32-S3 og HX711. Den lærer hvor fort den doserer og hvor mye som kommer etter at motoren stopper, stopper i tide og pulser deretter. Den gir også gode råd om støy i vekta.
- [vertical-cloud-lab/powder-doser](https://github.com/vertical-cloud-lab/powder-doser) (2026) er en printet skrue i laboratorieskala med problemer med statisk elektrisitet. Erfaringene kan ikke overføres til mel.

### Anbefalt melskrue

| Del | Valg |
|---|---|
| Skrue | 25–30 mm diameter, stigning ≈ diameteren, aksel av rustfritt stål (316, 8 mm), i et U-trau |
| Beholder | Vegger minst 60° fra horisontalen, med innløpsåpning på minst 120 mm langs skruen |
| Røreverk | Tråd av rustfritt stål (3 mm) like over åpningen, ca. 10–20 o/min, drevet av samme motor via tannhjul, så det bare går under dosering. Ikke vibrasjon, for det pakker melet. |
| Motor | NEMA17 med planetgir 5:1 og TMC2209 (stille) |
| Kapasitet | Ca. 2,4–4,3 g per omdreining. 560 g tar 2–4 min. En puls på 1/8 omdreining gir ca. 0,3–0,5 g (beregnet). |
| Utløp | Kort, loddrett fallrør med servoklaff som bare er åpen under dosering |
| Rengjøring | Beholder, skrue og trau tas ut uten verktøy |

**Styringen:**
1. Tarer når vekta er stabil (standardavvik under 0,1 g over 1 s).
2. Grovfyller til ca. 92 %, venter 1 s, og pulser deretter halvparten av det som mangler.
3. Sikter litt under målet, siden mel ikke kan tas ut igjen.
4. **Regner ut vann og salt ut fra den faktiske melmengden.**
5. Øker ikke vekta etter et antall omdreininger, er beholderen tom eller melet har dannet bro. Da reverserer skruen et halvt omdreining, røreverket går, og maskinen prøver igjen. Hjelper ikke det, varsler den.

### Én beholder med melblanding, eller to beholdere?

- **Én beholder:** halvparten så mye maskinvare, én kalibrering og lavere maskin. Ulempen er at kli og hvetemel kan skille seg i beholderen. Bland derfor etter vekt når du fyller. Sammalt mel harskner etter 1–3 måneder i romtemperatur, men det er greit når du fyller hver uke (søk).
- **To beholdere:** fritt forhold mellom melsortene og ingen separasjon, men dobbel pris og plass.
- **Anbefaling:** Én beholder i v1, men konstruert slik at en til kan settes på senere.

## 2. Salt

- **Klumping:** Salt (NaCl) trekker fukt over ca. 75 % relativ luftfuktighet. Når lufta tørker igjen, kristalliserer saltlaken og binder kornene sammen. Fint salt klumper lettere, og havsalt trekker mer fukt (søk).
- **Valg:** fint bordsalt med antiklumpemiddel (f.eks. Jozo ekstra fint med E535, søk). Ikke flaksalt eller havsalt.
- **Beholder:** ca. 250 ml (ca. 20 bakinger), med pakning og silikagel i lokket, og med eget utløp og egen klaff, adskilt fra melet.
- **Doserer:** liten horisontal skrue (10 mm). Ca. 0,34 g per omdreining, så 12 g tar ca. 20 s, og en kvart omdreining gir ca. 0,1 g (beregnet). Salt renner lett og trenger ikke røreverk. Unngå vibrasjonsrenner (de drypper og forstyrrer vekta) og aluminium eller vanlig stål nær saltet.
- **Oppløsning:** 48 g vann løser ca. 17 g salt ved 20 °C. 12 g er ca. 70 % av metning (beregnet). Hvor lang tid det tar, er UVERIFISERT og måles i E12.
- **Er salt og vann rett på deigen det samme som saltlake?** Med maskinelting trengs det ifølge erfarne bakere ikke å løse saltet først, med mindre det er grovt (søk). **For v1:** Etter fermentolysen doseres 12 g salt og deretter 48 g vann rett på deigen, og maskinen elter rolig i 2–4 min. E12 tester om resultatet blir like godt som med ferdig saltlake.

## 3. Vann

- **Pumpe:**
  - Kamoer KPHM400, 24 V, ca. 400 ml/min (søk). 470 g tar ca. 70 s.
  - Slange: matgodkjent platinaherdet silikon er godt nok for ca. 10 timer drift i året. Byttes årlig.
- **Drypp:**
  - En peristaltisk pumpe stenger selv når den står stille, så den trenger ingen tilbakeslagsventil.
  - Kjør pumpen ½–1 omdreining baklengs etter hver dosering.
  - Tanken står lavere enn dysen, og dysen sitter over deigen, unna sprut.
  - Membranpumper med ventiler drypper når det setter seg rester i ventilene og frarådes.
- **Hygiene:**
  - Kaffemaskinprodusenter anbefaler å bytte vannet hver dag (søk), og EPA sier det samme om luftfuktere (søk).
  - I lagret husholdningsvann økte bakterietallet fra ca. 50 til ca. 160 000 per ml på 4 døgn, mest *Pseudomonas* (søk).
  - Ingen råd fra Mattilsynet ble funnet (UVERIFISERT).
  - **Anbefaling:**
    - Fyll vann per baking.
    - Tanken skal stå unna det varme kammeret.
    - Etter siste dosering pumper maskinen slangen tom baklengs.
    - Vask tanken hver uke. Bruk en ugjennomsiktig tank med vid åpning.

## 4. Vekt

- **Vektforsterker:**
  - HX711 og NAU7802 har omtrent samme støy.
  - **NAU7802 velges:** Den bruker I²C og er støttet i ESPHome-kjernen siden 2024.10.
  - ADS1232 har ingen ESPHome-komponent.
- **Lastcelle:**
  - En ekte enpunkts lastcelle i klasse C3 (f.eks. Zemic L6D) kryper ca. 0,03 % per 30 min. En TAL220B kryper ca. 0,1 % på 3 min (søk).
  - **Hvis hele drivverket med formen står på vekta (ca. 3,8 kg + deig), trengs en celle på 10 kg** (beregnet).
- **Støy og drift** (beregnet):
  - Støyen er ca. 0,02–0,08 g, og ±0,5 g er realistisk.
  - De største feilene er nullpunktsdrift (ca. 2,5 g per 10 °C for en 5 kg TAL220B) og kryp (ca. 0,5 g etter 470 g). **Tarer derfor rett før hver tilsetning**, og vei bare når motor, vifte og varme står stille.
- **ESPHome:**
  - Les `nau7802` med 10 målinger i sekundet, og filtrer med median og glidende snitt.
  - Grov- og finstyringen legges i en egen C++-komponent, ikke i YAML-skript.
  - `tmc2209` (UART) finnes bare på utviklingsgrenen i oktober 2026. Inntil den er sluppet, kjøres stepperne med step/dir.
- **Mekanikk:**
  - Bruk overlaststopp på ca. 0,3 mm.
  - Ingenting annet enn vekta får bære formen. Kantpressere eller en krok fra lokket ned i deigen ville gitt feil vekt.

## 5. Printede deler og matkontakt

- EU-kravene gjelder den ferdige delen. Erklæringene for filament gjelder ofte bare den naturfargede råvaren (søk).
- PLA og PETG kan rengjøres med varmt såpevann og et kort klorbad (IEEE 2023, søk). Lagene kan likevel samle bakterier.
- **Anbefaling:**
  - Naturfarget PETG med samsvarserklæring etter EU 10/2011, printet med dyse av rustfritt stål og glatte flater der melet renner.
  - Aksler og røreverk av rustfritt stål (316).
  - Børst og støvsug delene tørt hver uke. Vasker du dem, må de være helt tørre før du fyller på igjen.

## 6. Risiko

1. **Melet danner bro eller kanal** (høy luftfuktighet, sammalt mel). Tiltak: lang åpning, bratte vegger, røreverk, reversering og alarm. Reserveplan: N2.
2. **Fukt i de tørre kanalene.** Tiltak: beholderne utenfor kammeret, stengte klaffer, og dosering bare når kroken står stille.
3. **Feil vekt.** Tiltak: ingenting annet enn vekta bærer formen, tarering før hvert trinn, krav om stabil vekt, og vifte og varme av under veiing.
4. **For mye mel.** Tiltak: grovstopp på 92 %, og vann og salt regnes ut fra faktisk mel.
5. **Saltet klumper.** Tiltak: fint salt med antiklumpemiddel, tett boks og silikagel.
6. **Biofilm i vannet.** Tiltak: fyll per baking, tøm slangen og vask tanken hver uke.
