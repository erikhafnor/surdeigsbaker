# 05 – Eksperimentplan

Eksperimentene skal fjerne den største usikkerheten **før** vi bygger mekanikk. Hvert eksperiment har en hypotese, en metode, målinger og et kriterium for når det er bestått. Mal: [`maler/eksperiment.md`](maler/eksperiment.md). Resultatene legges i `data/` og oppsummeres i et GitHub-issue med etiketten `eksperiment`.

**Prioritet:** 🔴 avgjør arkitekturen · 🟠 avgjør en delløsning · 🟢 forbedrer

## Oversikt

| ID | Navn | Fase | Prio | Spørsmål det besvarer |
|---|---|---|---|---|
| E01 | Referansebrød | 0 | 🔴 | Hvordan ser «godt» ut i tall? |
| E02 | Surdeigskinetikk | 1 | 🔴 | Kan vi forutsi når levainen er klar? |
| E03 | Flytetest mot sensorer | 1 | 🟠 | Hva skal maskinen måle i stedet for flytetesten? |
| E04 | Autolyse eller fermentolyse | 1 | 🟢 | Kan levainen bygges i formen fra start? |
| E05 | Bretting med maskin | 1 | 🔴 | Kan strekk og brett erstattes av maskinbearbeiding? |
| E06 | Uten forming | 1 | 🔴 | «Tipp og stek» eller «med forming» som standard? |
| E07 | Sømsiden opp i stedet for snitting | 1 | 🟠 | Trenger vi snitting i v1? |
| E08 | Steking av kald deig i vanlig ovn | 1 | 🟢 | Beste stekeprosedyre for mennesket. Er K4 (kaldstart) aktuell? |
| E09 | Kald bulkheving | 1 | 🟠 | Kan kald heving skje i bollen (i brukerens kjøleskap)? |
| E10 | Overlevering for hånd | 1–3 | 🟠 | Er det lett å få deigen ut av bollen eller kurven og ned i gryta? |
| E11 | Dosering av mel | 3 | 🟠 | Er en snegle nøyaktig nok? |
| E12 | Dosering av vann og salt | 3 | 🟠 | Kan maskinen lage saltlaken selv av tørt salt og vann? Er nøyaktigheten god nok? |
| E13 | Termikk: varme og kammer | 2 | 🔴 | Holder v1 deigen på 24–28 °C ±0,5 °C med 60 W og vifte? |
| E14 | Måling av heving i formen | 2–3 | 🟠 | Kan bulkheving måles automatisk med ToF og kamera? |
| E15 | Ubemannet drift og feilinjeksjon | 4 | 🔴 | Er maskinen trygg å la stå? |
| E16 | Ventevindu etter bulk | 1–2 | 🔴 | Hvor lenge kan deigen vente ved romtemperatur etter bulk før forming, uten kvalitetstap? |
| E17 | Eltetest i brødformen | 2 | 🔴 | Elter eltebladet i Panasonic-formen 77 % deig godt nok, og får det med melet i hjørnene? |
| E18 | Kamera: feil og aktivitet | 2–3 | 🟠 | Kan kameraet og motorstrømmen sammen oppdage feil og vise hvor aktiv deigen er? |

## Detaljer

### E01 – Referansebrød 🔴
- **Hypotese:** v7.0 bakt for hånd gir et stabilt referansebrød. Variasjonen mellom brød er mindre enn forskjellene vi ønsker å måle.
- **Metode:** Bak v7.0 tre ganger med full logging. Vei alt (skjeemål gjøres om til gram). Mål rom-, vann- og deigtemperatur ved hvert trinn. Mål levainens heving (linjal eller ToF) og bulkhevingen i et måleglass med en klump av deigen («aliquot jar»). Mål kjernetemperatur, vekt før og etter steking og volum. Ta snittfoto og fyll ut brødkortet.
- **Leveranse:** Oppskriften i gram, referansekurver for temperatur og heving, og brødkortpoeng med spredning.
- **Bestått når:** Tre brød er logget, og brødkortpoengene varierer med ≤ 15 %.

### E02 – Surdeigskinetikk 🔴
- **Hypotese:** Ved fast temperatur og fast blandingsforhold kan tiden til toppheving forutsies innenfor ±1 t.
- **Metode:** Glass med levain i et temperaturstyrt bad (sous vide-pinne i en kasse med vann) eller i hevekassen fra fase 1. Matrise: 22, 26 og 30 °C × forhold 1:2:2 og 1:5:5. Hevingen logges med en ToF-sensor over hvert glass. pH måles ved topp. Hver kombinasjon gjøres to ganger.
- **Leveranse:** En enkel modell, f.eks. t_topp = f(T, forhold), med usikkerhet. Den brukes i tidsplanleggeren.
- **Bestått når:** Modellen treffer innenfor ±1 t på et nytt kontrollforsøk.

### E03 – Flytetest mot sensorer 🟠
- **Bakgrunn:** Flytetesten regnes som upålitelig (se FO3 i [forskningsplanen](02-forskningsplan.md)). Målet er derfor å finne et bedre «klar»-signal, ikke å etterligne flytetesten.
- **Hypotese:** Relativ heving (f.eks. dobling eller et punkt like før toppen på Gompertz-kurven) forutsier bakeresultatet bedre enn flytetesten.
- **Metode:** Under E02 tas en flytetest hver 30. min. Resultatet sammenlignes med samtidige målinger av heving (ToF), CO₂ (høyområdesensor som STC31, siden SCD41 blir mettet) og pH (stikkprøver). Til slutt bakes et kontrollbrød på levain tatt ut på ulike tidspunkter.
- **Bestått når:** Vi har valgt den målingen som best forutsier en bestått flytetest. Den brukes som «klar»-signal.

### E04 – Autolyse eller fermentolyse 🟢
- **Hypotese:** Fermentolyse, der levain bygges i bollen (i v1: brødformen) og resten av melet og vannet tilsettes uten egen autolyse, gir ≥ 90 % av referansepoengene.
- **Metode:** A/B-test, to brød per variant, med den samme bulk- og stekeprosessen.

### E05 – Bretting med maskin 🔴
- **Hypotese:** 3–4 korte (10–20 s) og langsomme omrøringer med eltebladet (v1) under bulkhevingen gir like god glutenstruktur som strekk og brett for hånd.
- **Metode:** Fire varianter, to brød hver: (a) for hånd (referanse), (b) korte krokomrøringer hver 30. min, (c) bare lengre elting i starten, (d) ingen bearbeiding. Bruk en kjøkkenmaskin med eltekrok.
- **Måling:** Vindustest (windowpane), deighøyde etter forming, volum og krumme.

### E06 – Uten forming 🔴
- **Hypotese:** Deig som tippes rett fra bollen og ned i gryta, uten forming, gir ≥ 80 % av volumet og formen til et formet brød, fordi gryta holder på formen.
- **Metode:** Varianter: (a) formet etter v7.0, (b) uten forming, tippet fra bollen, (c) «tippeforming», der deigen glir over en melet rampe/skrå flate. Bak i samme gryte.
- **Bestått når:** (b) eller (c) ≥ 80 % av (a) på volum og form. Da blir «tipp og stek» standard. Hvis ikke, blir varianten «med forming» standard: mennesket former når maskinen varsler. Det er en akseptabel løsning, ikke en stor risiko.

### E07 – Sømsiden opp i stedet for snitting 🟠
- **Hypotese:** Deig som legges med sømsiden eller den ujevne siden opp, sprekker kontrollert og ser akseptabel ut uten snitting.
- **Metode:** Snittet, usnittet med sømsiden ned, og usnittet med sømsiden opp. To brød per variant.

### E08 – Steking av kald deig i vanlig ovn 🟢
- **Bakgrunn:** Stekingen skjer i vanlig ovn ([ADR-006](beslutninger/ADR-006-steking-i-vanlig-ovn.md)). Eksperimentet optimaliserer det mennesket gjør etter overleveringen. Det er ikke et designvalg for maskinen.
- **Spørsmål:** Trengs det tid på benken etter kjøleskapet før steking? Gir kaldstart i kald gryte (K4) akseptabelt resultat?
- **Metode:** Kald deig rett i forvarmet gryte (referansen), etter 30 min på benken, og med kaldstart i kald ovn. To brød per variant.
- **Konsekvens:** Gir standard stekeprosedyre for brukerveiledningen og varselteksten («forvarm ovnen nå»). Avgjør om K4 skal vurderes videre.

### E09 – Kald bulkheving 🔴
- **Hypotese:** Kald heving av hele deigen i bollen (bulk retard ved 4–8 °C) gir like god smak som kald heving i kurven etter forming. Kald deig er dessuten lettere å tippe i gryta og snitte.
- **Metode:** (a) v7.0 med kald etterheving i kurv, (b) kald bulkheving 12 t etterfulgt av kort varm heving, (c) uten kald heving. Lag også et smakspanel og mål pH.
- **Konsekvens:** Avgjør hvordan kald heving skal skje: i bulk i bollen (variant A, «tipp og stek») eller etter forming i kurv (variant B). Begge skjer i brukerens kjøleskap ([ADR-007](beslutninger/ADR-007-ingen-kjoling.md)).

### E10 – Overlevering for hånd 🟠
- **Hypotese:** Kald deig (4–8 °C) kan tippes fra en avtakbar bolle eller kurv og ned i en varm gryte på ≤ 30 s, med ≤ 10 g igjen og uten at deigen mister mye luft.
- **Metode:** Bolle med PTFE-belegg (greit, siden det ikke er varme), bolle av rustfritt stål med olje eller mel, og hevekurv med klede og rismel. Hjelpemidler: myk skrape og bakepapir som slynge. Prøv også bollens form: lav og vid, eller dyp.
- **Måling:** Tid, rester (g), om deigen er skadet, og hvor enkelt testpersonene synes det er (1–5).
- **Konsekvens:** Viser om deigen slipper brødformen i v1 lett nok, eller om den trenger belegg, olje eller en annen form.

### E11 – Dosering av mel 🟠
- **Mål:** ±1 % på 550 g og ±2 g på små mengder til levain. Mål også tid og hvor ofte melet henger seg opp («bridging»).
- **Metode:** Melskruen i v1 ([`hardware/v1/`](../hardware/v1/README.md#86-dosering-e11-og-e12)): vannrett skrue på 28 mm med røreverk og klaff, stoppet av vekta. Test melblandingen (siktet og sammalt) ved 40, 60 og 75 % relativ luftfuktighet, med full og nesten tom beholder, og etter at melet har stått en uke. Logg flyt, tid, finpulser og reverseringer fra fastvaren.
- **Konsekvens:** Klarer ikke skruen det, er reserveplanen forhåndsveid mel i beholderen, dosert på én gang (N2).

### E12 – Dosering av vann og salt 🟠
- **Bakgrunn:** Brukeren skal bare fylle på mel, salt og vann. Maskinen lager saltlaken selv ([`11-bruksscenarier.md`](11-bruksscenarier.md#slik-lager-maskinen-saltlaken)).
- **Mål:** Vann ±1 %. Salt ±0,5 g av 12 g. Saltet skal være jevnt fordelt i deigen. Saltet i beholderen skal ikke klumpe seg på en uke i et vanlig kjøkken.
- **Metode:**
  - Vann: peristaltisk pumpe styrt av vekta.
  - Salt: skrue på 10 mm fra en tett boks, stoppet av vekta (v1). Test fint bordsalt og fint havsalt ved 40, 60 og 75 % relativ luftfuktighet.
  - Saltlake: (a) ferdig 20 % saltlake (referanse), (b) tørt salt og vann dosert rett i formen (v1), (c) saltlake laget i en saltkopp i maskinen. To brød per variant. Smak salt på tre steder i krummen og mål ledningsevne eller saltinnhold hvis mulig.
- **Konsekvens:** Avgjør om v1 trenger saltkopp (c), eller om saltlake i formen (b) holder.

### E13 – Termikk: varme og kammer 🔴
- **Bakgrunn:** Maskinen har bare varme ([ADR-007](beslutninger/ADR-007-ingen-kjoling.md)). I v1 sitter en silikonmatte på 60 W bak en kjøleprofil på bakveggen, og en vifte sirkulerer lufta rundt formen ([ADR-010](beslutninger/ADR-010-v1-arkitektur.md)).
- **Mål:**
  - 1 kg deig (eller vann) varmes fra 20 til 26 °C på ≤ 1 t ved 20 °C i rommet.
  - Temperaturen holdes ±0,5 °C i ≥ 5 t.
  - Bunnen av deigen blir aldri over 32 °C (kjøleprofilen er begrenset til 38 °C).
- **Metode:** Formen med 1 l vann og senere med deig. Logg formbunnen, kjøleprofilen, deigoverflaten (IR), kammerlufta og en kjernetemperatur med et ekstra stikktermometer. Kjør PID-autotune. Prøv romtemperatur 18 og 22 °C, med og uten vifta.
- **Konsekvens:** Gir PID-verdier og tidskonstanten for fastvaren og simuleringen (`tau_h` i `sim.h`), og viser om 60 W er nok.

### E14 – Måling av heving i formen 🟠
- **Hypotese:** ToF-sensoren (høyden i ett punkt) og kameraet (linjen der deigen møter formveggen) gir sammen bulkhevingen med ±5 prosentpoeng sammenlignet med måleglasset. Hver for seg gir de trolig ±5–10 (se [`forskning/kamera-og-ai.md`](forskning/kamera-og-ai.md)).
- **Metode:**
  1. Kalibrer først med vann: 250 ml av gangen fra 0,5 til 3 l, med en dråpe melk for kontrast og en hvit flottør for ToF-sensoren.
  2. Kjør deretter målingene parallelt med et måleglass (aliquot jar) i kammeret under vanlige bakinger.
  3. Prøv også en 8 × 8 ToF med flere soner (VL53L8CX) hvis ToF-sensoren og kameraet ikke holder.
- **Konsekvens:** Avgjør om v1 skal ha kamera, 8 × 8 ToF eller begge ([ADR-009](beslutninger/ADR-009-kamera.md)).

### E15 – Ubemannet drift og feilinjeksjon 🔴
- **Metode:** Først 10 tørrkjøringer uten deig, deretter 5 kjøringer med vann og til slutt 3 med deig. Feilinjeksjon: koble fra en temperaturføler, simuler en fastlåst MOSFET (KSD301 og termosikringen skal løse ut), strømbrudd midt i et program, tapt nettverk, fastkjørt motor, døra åpnet mens eltebladet går, tom melbeholder og tom vanntank.
- **Bestått når:** Alle feil gir en trygg tilstand innenfor definert tid: varmen av, motoren av og varsel. Se [`06-sikkerhet.md`](06-sikkerhet.md).

### E16 – Ventevindu etter bulk 🔴
- **Bakgrunn:** Uten kjøling i maskinen ([ADR-007](beslutninger/ADR-007-ingen-kjoling.md)) venter deigen ved romtemperatur fra «klar for forming» til du former den. Det gamle E16 (kaldhold i maskinen) er fjernet.
- **Hypotese:** Deigen kan vente minst 60 min ved 20–22 °C etter at bulkhevingen er ferdig, med ≤ 10 % tap på brødkortet.
- **Metode:** Lag én deig, del den i tre etter bulk og form etter 0, 60 og 120 min. Kald etterheving og steking som referansen. Gjenta med en ny deig.
- **Konsekvens:** Bestemmer hvor presis tidsplanleggeren må være, og når maskinen skal sende en påminnelse. Akseptansekriterium 3 bygger på resultatet.

### E17 – Eltetest i brødformen 🔴
- **Bakgrunn:** v1 elter i en brødmaskinform fra Panasonic XL med elteblad i bunnen, drevet av egen girmotor ([ADR-010](beslutninger/ADR-010-v1-arkitektur.md), [elting](forskning/v1-elting.md)). Ingen kilder viser 75–80 % deig i slike former. (E17 gjaldt C-kroken i v0 før ADR-010.)
- **Hypotese:** Eltebladet gir en glatt og elastisk deig (bestått vindusprøve) på ≤ 12 min med 560 g mel og 77 % vann, uten tørt mel i hjørnene.
- **Metode:**
  1. **Før bygging,** med giveren: kjør deigen i brødmaskinens eget deigprogram.
  2. **I v1:** dosér vann og mel i tre porsjoner med blanding imellom, som i fastvaren. Elt med 50, 75 og 100 % fart. Film ovenfra, logg motorstrømmen og ta vindusprøve hvert 3. minutt.
  3. Test også brettingen med eltebladet (E05).
  4. Se [`hardware/v1/README.md`](../hardware/v1/README.md#88-elting-e17).
- **Bestått når:** Vindusprøven er bestått på ≤ 12 min, motorstrømmen er under ca. 6 A, det ligger ikke tørt mel i hjørnene, og formen sitter fast i holderen.
- **Hvis ikke:** Prøv i rekkefølge:
  - flere korte retningsskift
  - mer vann først
  - lavere hydrering
  - Unold-formen (større)

### E18 – Kamera: feil og aktivitet 🟠
- **Bakgrunn:** Ferdige bildemodeller er usikre på fine vurderinger. Motorstrømmen er det beste signalet for feil under eltingen ([`forskning/kamera-og-ai.md`](forskning/kamera-og-ai.md)).
- **Hypotese:** En ferdig bildemodell (lokalt eller i skyen) oppdager grove feil uten trening: deig over kanten, mel som ikke er blandet inn og formen som ikke står riktig. (Tom form og glemt surdeig ser vekta.) Finere feil (deigen danner ikke ball, klistrer seg fast) oppdages med motorstrøm og en liten modell trent på egne bilder.
- **Metode:**
  1. Ta bilder hvert 5.–10. sekund under eltingen, og hvert 2. minutt under bulken.
  2. Merk feil med en knapp i Home Assistant mens det skjer.
  3. Sammenlign bildemodellen og motorstrømmen med merkingen.
  4. Logg også teksturen og forskjellen mellom bilder som mål på aktivitet (bobler).
- **Bestått når:** Grove feil oppdages i ≥ 90 % av tilfellene med ≤ 1 falsk alarm per baking.
- **Konsekvens:** Avgjør om v1 trenger en trent modell, og om den kan kjøre utenfor maskinen ([ADR-009](beslutninger/ADR-009-kamera.md)).

## Utstyr til eksperimentene i fase 0–1

Se [`09-budsjett-og-innkjop.md`](09-budsjett-og-innkjop.md). Det meste kan gjøres med en kjøkkenmaskin, en jerngryte, en vanlig ovn, kjøleskapet og et ESP32-basert måleoppsett. Når v1 er bygget, kan den brukes til E02–E06, E11–E14, E16 og E17.
