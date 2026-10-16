# 05 – Eksperimentplan

Eksperimentene skal fjerne den største usikkerheten **før** vi bygger mekanikk. Hvert eksperiment har en hypotese, en metode, målinger og et kriterium for når det er bestått. Mal: [`maler/eksperiment.md`](maler/eksperiment.md). Resultatene legges i `data/` og oppsummeres i et GitHub-issue med etiketten `eksperiment`.

**Prioritet:** 🔴 avgjør arkitekturen · 🟠 avgjør en delløsning · 🟢 forbedrer

## Oversikt

| ID | Navn | Fase | Prio | Spørsmål det besvarer |
|---|---|---|---|---|
| E01 | Referansebrød | 0 | 🔴 | Hvordan ser «godt» ut i tall? |
| E02 | Surdeigskinetikk | 1 | 🔴 | Kan vi forutsi når levainen er klar? |
| E03 | Flytetest mot sensorer | 1 | 🟠 | Hva skal maskinen måle i stedet for flytetesten? |
| E04 | Autolyse eller fermentolyse | 1 | 🟢 | Kan levainen bygges i bollen fra start? |
| E05 | Bretting med maskin | 1 | 🔴 | Kan strekk og brett erstattes av maskinbearbeiding? |
| E06 | Uten forming | 1 | 🔴 | «Tipp og stek» eller «med forming» som standard? |
| E07 | Sømsiden opp i stedet for snitting | 1 | 🟠 | Trenger vi snitting i v1? |
| E08 | Steking av kald deig i vanlig ovn | 1 | 🟢 | Beste stekeprosedyre for mennesket. Er K4 (kaldstart) aktuell? |
| E09 | Kald bulkheving | 1 | 🟠 | Kan kald heving skje i bollen (i brukerens kjøleskap)? |
| E10 | Overlevering for hånd | 1–3 | 🟠 | Er det lett å få deigen ut av bollen eller kurven og ned i gryta? |
| E11 | Dosering av mel | 3 | 🟠 | Er en snegle nøyaktig nok? |
| E12 | Dosering av vann og salt | 3 | 🟠 | Kan maskinen lage saltlaken selv av tørt salt og vann? Er nøyaktigheten god nok? |
| E13 | Termikk: varmeplate og kammer | 2 | 🔴 | Holder v0 deigen på 24–27 °C ±0,5 °C med 50 W, uten varme flekker i bunnen? |
| E14 | Måling av heving i bollen | 3 | 🟠 | Kan bulkheving måles automatisk? |
| E15 | Ubemannet drift og feilinjeksjon | 4 | 🔴 | Er maskinen trygg å la stå? |
| E16 | Ventevindu etter bulk | 1–2 | 🔴 | Hvor lenge kan deigen vente ved romtemperatur etter bulk før forming, uten kvalitetstap? |
| E17 | Eltetest i v0 | 2 | 🔴 | Elter C-kroken i v0 deigen godt nok, uten at deigen bare går rundt med kroken? |

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
- **Hypotese:** Fermentolyse, der levain bygges i bollen og resten av melet og vannet tilsettes uten egen autolyse, gir ≥ 90 % av referansepoengene.
- **Metode:** A/B-test, to brød per variant, med den samme bulk- og stekeprosessen.

### E05 – Bretting med maskin 🔴
- **Hypotese:** 3–4 korte (10–20 s) og langsomme omrøringer med eltekroken under bulkhevingen gir like god glutenstruktur som strekk og brett for hånd.
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
- **Konsekvens:** Gir bollens form og belegg i K2.

### E11 – Dosering av mel 🟠
- **Mål:** ±1 % på 550 g og ±2 g på små mengder til levain. Mål også tid og hvor ofte melet henger seg opp («bridging»).
- **Metode:** Prototyp på en snegle. Test med siktet mel og sammalt mel ved ulik luftfuktighet. Doseringen stoppes av vekta (lastcelle).

### E12 – Dosering av vann og salt 🟠
- **Bakgrunn:** Brukeren skal bare fylle på mel, salt og vann. Maskinen lager saltlaken selv ([`11-bruksscenarier.md`](11-bruksscenarier.md#slik-lager-maskinen-saltlaken)).
- **Mål:** Vann ±1 %. Salt ±0,5 g av 12 g. Saltet skal være jevnt fordelt i deigen. Saltet i beholderen skal ikke klumpe seg på en uke i et vanlig kjøkken.
- **Metode:**
  - Vann: peristaltisk pumpe styrt av vekta.
  - Salt: liten snegle eller cellehjulsdoserer, stoppet av vekta. Test fint bordsalt og fint havsalt ved 40, 60 og 75 % relativ luftfuktighet.
  - Saltlake: (a) ferdig 20 % saltlake (referanse), (b) tørt salt og vann dosert rett i bollen, (c) saltlake laget i en saltkopp i maskinen. To brød per variant. Smak salt på tre steder i krummen og mål ledningsevne eller saltinnhold hvis mulig.
- **Konsekvens:** Avgjør om v1 trenger saltkopp (c), eller om saltlake i bollen (b) holder.

### E13 – Termikk: varmeplate og kammer 🔴
- **Bakgrunn:** Maskinen har bare varme ([ADR-007](beslutninger/ADR-007-ingen-kjoling.md)). I v0 står bollen på en aluminiumsplate med et silikonelement på 50 W ([ADR-008](beslutninger/ADR-008-v0-design.md)).
- **Mål:**
  - 1 kg deig (eller vann) varmes fra 20 til 26 °C på ≤ 1 t ved 20 °C i rommet.
  - Temperaturen holdes ±0,5 °C i ≥ 5 t.
  - Bunnen av deigen blir aldri over 32 °C (platen er begrenset til 38 °C).
- **Metode:** Bollen med 1 l vann og senere med deig. Logg bolleveggen, platen, deigoverflaten (IR) og en kjernetemperatur med et ekstra stikktermometer. Kjør PID-autotune. Prøv romtemperatur 18 og 22 °C, med og uten XPS i kammeret.
- **Konsekvens:** Gir PID-verdier og maks platetemperatur for fastvaren, og viser om 50 W er nok.

### E14 – Måling av heving i bollen 🟠
- **Hypotese:** En ToF-sensor eller et kamera over bollen kan måle bulkheving med ±5 prosentpoeng sammenlignet med måleglasset.
- **Metode:** Kjør målingene parallelt med måleglasset (aliquot jar) under E05 og E09.

### E15 – Ubemannet drift og feilinjeksjon 🔴
- **Metode:** Først 10 tørrkjøringer uten deig, deretter 5 kjøringer med vann og til slutt 3 med deig. Feilinjeksjon: koble fra en temperaturføler, simuler en fastlåst MOSFET (KSD301 og termosikringen skal løse ut), strømbrudd midt i et program, tapt nettverk, fastkjørt motor og lokket åpnet mens kroken går.
- **Bestått når:** Alle feil gir en trygg tilstand innenfor definert tid: varmen av, motoren av og varsel. Se [`06-sikkerhet.md`](06-sikkerhet.md).

### E16 – Ventevindu etter bulk 🔴
- **Bakgrunn:** Uten kjøling i maskinen ([ADR-007](beslutninger/ADR-007-ingen-kjoling.md)) venter deigen ved romtemperatur fra «klar for forming» til du former den. Det gamle E16 (kaldhold i maskinen) er fjernet.
- **Hypotese:** Deigen kan vente minst 60 min ved 20–22 °C etter at bulkhevingen er ferdig, med ≤ 10 % tap på brødkortet.
- **Metode:** Lag én deig, del den i tre etter bulk og form etter 0, 60 og 120 min. Kald etterheving og steking som referansen. Gjenta med en ny deig.
- **Konsekvens:** Bestemmer hvor presis tidsplanleggeren må være, og når maskinen skal sende en påminnelse. Akseptansekriterium 3 bygger på resultatet.

### E17 – Eltetest i v0 🔴
- **Bakgrunn:** v0 elter med en C-krok i senter av en kjegleformet bolle ([ADR-008](beslutninger/ADR-008-v0-design.md)). Det er den største tekniske usikkerheten i designet.
- **Hypotese:** Kroken gir en glatt og elastisk deig (bestått vindusprøve) på ≤ 12 min, uten at deigen bare går rundt med kroken, og uten at bollen vrir seg.
- **Metode:** Testdeig uten surdeig: 500 g hvetemel, 380 g vann og 10 g salt. Elt med 30, 50 og 70 % fart. Film ovenfra, logg motorstrømmen og ta vindusprøve hvert 3. minutt. Gjenta med 77 % hydrering som i den maskinvennlige oppskriften. Se [`hardware/v0/README.md`](../hardware/v0/README.md#76-e17-eltetest-gjør-dette-tidlig).
- **Bestått når:** Vindusprøven er bestått på ≤ 12 min, motorstrømmen er under 3 A, og bollen står stille.
- **Hvis ikke:** Prøv i rekkefølge: høyere fart, kortere intervall mellom retningsskift, spiralkrok, krok ut fra senter. Det siste krever ny CAD.

## Utstyr til eksperimentene i fase 0–1

Se [`09-budsjett-og-innkjop.md`](09-budsjett-og-innkjop.md). Det meste kan gjøres med en kjøkkenmaskin, en jerngryte, en vanlig ovn, kjøleskapet og et ESP32-basert måleoppsett. Når v0 er bygget, kan den brukes til E02–E06, E13, E14, E16 og E17.
