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
| E06 | Uten forming | 1 | 🔴 | Trenger vi forming i v1? |
| E07 | Sømsiden opp i stedet for snitting | 1 | 🟠 | Trenger vi snitting i v1? |
| E08 | Varm eller kald gryte | 1 | 🔴 | Konsept C eller D? Hvilken gryte? |
| E09 | Kald bulkheving | 1 | 🔴 | Kan kald heving skje i bollen? |
| E10 | Slipp fra bollen | 3 | 🔴 | Kan deigen overføres med tyngdekraften? |
| E11 | Dosering av mel | 3 | 🟠 | Er en snegle nøyaktig nok? |
| E12 | Dosering av vann og saltlake | 3 | 🟠 | Fungerer saltlake? Er nøyaktigheten god nok? |
| E13 | Termikk: oppvarming og kjøling | 3 | 🔴 | Klarer vi effekt og tid innenfor 2000 W? |
| E14 | Måling av heving i bollen | 3 | 🟠 | Kan bulkheving måles automatisk? |
| E15 | Ubemannet drift og feilinjeksjon | 4 | 🔴 | Er maskinen trygg å la stå? |

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
- **Bestått når:** (b) eller (c) ≥ 80 % av (a) på volum og form. Konsekvens: Hvis det ikke er bestått, må forming inn i v1, og det er en stor risiko.

### E07 – Sømsiden opp i stedet for snitting 🟠
- **Hypotese:** Deig som legges med sømsiden eller den ujevne siden opp, sprekker kontrollert og ser akseptabel ut uten snitting.
- **Metode:** Snittet, usnittet med sømsiden ned, og usnittet med sømsiden opp. To brød per variant.

### E08 – Varm eller kald gryte 🔴
- **Hypotese:** Kaldstart (deigen i kald gryte som så varmes opp) gir ≤ 15 % lavere volum enn forvarmet gryte. Lettere gryter reduserer forskjellen.
- **Metode:** Gryter: emaljert jerngryte og en lettere gryte av karbonstål eller tynt stål. Hver gryte bakes med forvarming og med kaldstart. Logg effekt og energi (kWh) med en energimåler i stikkontakten.
- **Konsekvens:** Avgjør mellom konsept C og D, og hvilken gryte vi velger.

### E09 – Kald bulkheving 🔴
- **Hypotese:** Kald heving av hele deigen i bollen (bulk retard ved 4–8 °C) gir like god smak som kald heving i kurven etter forming. Kald deig er dessuten lettere å overføre.
- **Metode:** (a) v7.0 med kald etterheving i kurv, (b) kald bulkheving 12 t etterfulgt av kort varm heving, (c) uten kald heving. Lag også et smakspanel og mål pH.
- **Konsekvens:** Avgjør om kjøling trengs i bollen eller i stekerommet.

### E10 – Slipp fra bollen 🔴
- **Hypotese:** Kald deig (6–10 °C) slipper en vippet bolle (≥ 120°) innen 60 s med ≤ 10 g igjen i bollen, med et egnet belegg.
- **Metode:** Bolle med PTFE-belegg, med silikonbelegg og av rustfritt stål med olje eller mel. Deigen er kald eller romtemperert. Vippevinkel 90–180°. Hjelpemidler: en vibrator, en skrape som beveger seg langs bunnen, eller bakepapir som slynge.
- **Måling:** Tid til deigen slipper, rester i bollen (g) og om deigen er skadet (degassing).

### E11 – Dosering av mel 🟠
- **Mål:** ±1 % på 550 g og ±2 g på små mengder til levain. Mål også tid og hvor ofte melet henger seg opp («bridging»).
- **Metode:** Prototyp på en snegle. Test med siktet mel og sammalt mel ved ulik luftfuktighet. Doseringen stoppes av vekta (lastcelle).

### E12 – Dosering av vann og saltlake 🟠
- **Mål:** Vann ±1 %. Saltlaken skal ha en konsentrasjon som ikke krystalliserer i slangene ved 4–25 °C.
- **Metode:** Peristaltisk pumpe og magnetventil styrt av vekta. Saltlake på 20 % (mettet er ca. 26 %, så vi holder god avstand). Vannmengden i saltlaken trekkes fra i oppskriften.

### E13 – Termikk: oppvarming og kjøling 🔴
- **Mål:** Gryta skal nå 250–260 °C på ≤ 45 min innenfor 2000 W. Bollen skal kjøle 1 kg deig fra 25 °C til ≤ 8 °C på ≤ 3 t.
- **Metode:** Mål oppvarmingskurven til gryta med et termoelement, med ulike typer isolasjon. Sammenlign kjølekurven for et kompressoroppsett (ombygd vinkjøleskap) og et Peltier-oppsett, med en 1 kg vannbalong eller deig. Mål strømforbruk og kondens. Grove beregninger finnes i [arkitekturen](07-arkitektur.md#4-termikk-grove-tall).

### E14 – Måling av heving i bollen 🟠
- **Hypotese:** En ToF-sensor eller et kamera over bollen kan måle bulkheving med ±5 prosentpoeng sammenlignet med måleglasset.
- **Metode:** Kjør målingene parallelt med måleglasset (aliquot jar) under E05 og E09.

### E15 – Ubemannet drift og feilinjeksjon 🔴
- **Metode:** Først 10 tørrkjøringer uten deig, deretter 5 kjøringer med vann og til slutt 3 med deig. Feilinjeksjon: koble fra en temperaturføler, simuler et fastlåst SSR (termosikringen skal løse ut), strømbrudd midt i et program, tapt nettverk og fastkjørt motor.
- **Bestått når:** Alle feil gir en trygg tilstand (varmen av, motoren av, varsel) innenfor definert tid. Se [`06-sikkerhet.md`](06-sikkerhet.md).

## Utstyr til eksperimentene i fase 0–1

Se [`09-budsjett-og-innkjop.md`](09-budsjett-og-innkjop.md). Det meste kan gjøres med en kjøkkenmaskin, en jerngryte, en vanlig ovn, en hevekasse (bygges i fase 1) og et ESP32-basert måleoppsett.
