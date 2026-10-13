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
| E09 | Kald bulkheving | 1 | 🔴 | Kan kald heving skje i bollen? |
| E10 | Overlevering for hånd | 1–3 | 🟠 | Er det lett å få deigen ut av bollen eller kurven og ned i gryta? |
| E11 | Dosering av mel | 3 | 🟠 | Er en snegle nøyaktig nok? |
| E12 | Dosering av vann og saltlake | 3 | 🟠 | Fungerer saltlake? Er nøyaktigheten god nok? |
| E13 | Termikk: kjøling og svak varme | 1–3 | 🔴 | Klarer kammeret 1 kg deig til ≤ 6 °C, stille og uten kondensproblemer? |
| E14 | Måling av heving i bollen | 3 | 🟠 | Kan bulkheving måles automatisk? |
| E15 | Ubemannet drift og feilinjeksjon | 4 | 🔴 | Er maskinen trygg å la stå? |
| E16 | Kaldhold | 1 | 🔴 | Hvor lenge kan deigen vente kald etter kald heving uten kvalitetstap? |

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
- **Spørsmål:** Trengs det tid på benken etter kaldholdet før steking? Gir kaldstart i kald gryte (K4) akseptabelt resultat?
- **Metode:** Kald deig rett i forvarmet gryte (referansen), etter 30 min på benken, og med kaldstart i kald ovn. To brød per variant.
- **Konsekvens:** Gir standard stekeprosedyre for brukerveiledningen og varselteksten («forvarm ovnen nå»). Avgjør om K4 skal vurderes videre.

### E09 – Kald bulkheving 🔴
- **Hypotese:** Kald heving av hele deigen i bollen (bulk retard ved 4–8 °C) gir like god smak som kald heving i kurven etter forming. Kald deig er dessuten lettere å tippe i gryta og snitte.
- **Metode:** (a) v7.0 med kald etterheving i kurv, (b) kald bulkheving 12 t etterfulgt av kort varm heving, (c) uten kald heving. Lag også et smakspanel og mål pH.
- **Konsekvens:** Avgjør hvordan kald heving skal skje: i bulk i bollen (variant A, «tipp og stek») eller etter forming i kurv (variant B).

### E10 – Overlevering for hånd 🟠
- **Hypotese:** Kald deig (4–8 °C) kan tippes fra en avtakbar bolle eller kurv og ned i en varm gryte på ≤ 30 s, med ≤ 10 g igjen og uten at deigen mister mye luft.
- **Metode:** Bolle med PTFE-belegg (greit, siden det ikke er varme), bolle av rustfritt stål med olje eller mel, og hevekurv med klede og rismel. Hjelpemidler: myk skrape og bakepapir som slynge. Prøv også bollens form: lav og vid, eller dyp.
- **Måling:** Tid, rester (g), om deigen er skadet, og hvor enkelt testpersonene synes det er (1–5).
- **Konsekvens:** Gir bollens form og belegg i K2.

### E11 – Dosering av mel 🟠
- **Mål:** ±1 % på 550 g og ±2 g på små mengder til levain. Mål også tid og hvor ofte melet henger seg opp («bridging»).
- **Metode:** Prototyp på en snegle. Test med siktet mel og sammalt mel ved ulik luftfuktighet. Doseringen stoppes av vekta (lastcelle).

### E12 – Dosering av vann og saltlake 🟠
- **Mål:** Vann ±1 %. Saltlaken skal ha en konsentrasjon som ikke krystalliserer i slangene ved 4–25 °C.
- **Metode:** Peristaltisk pumpe og magnetventil styrt av vekta. Saltlake på 20 % (mettet er ca. 26 %, så vi holder god avstand). Vannmengden i saltlaken trekkes fra i oppskriften.

### E13 – Termikk: oppvarming og kjøling 🔴
- **Mål:**
  - Kammeret skal kjøle 1 kg deig fra 25 °C til ≤ 6 °C på ≤ 3 t, og holde 4–6 °C ±0,5 °C i ≥ 24 t.
  - Det skal varme fra 6 til 24 °C på ≤ 1 t uten kondens på deigen.
  - Det skal være stille om natten (≤ ca. 40 dB).
- **Metode:**
  - Sammenlign kjølekurvene for et kompressoroppsett (ombygd vinkjøleskap) og et Peltier-oppsett, med en 1 kg vannbalong eller deig.
  - Mål strømforbruk, støy og kondens.
  - Mål hvor mye eltemotoren varmer kammeret.
  - Grove beregninger finnes i [arkitekturen](07-arkitektur.md#4-termikk-grove-tall).

### E14 – Måling av heving i bollen 🟠
- **Hypotese:** En ToF-sensor eller et kamera over bollen kan måle bulkheving med ±5 prosentpoeng sammenlignet med måleglasset.
- **Metode:** Kjør målingene parallelt med måleglasset (aliquot jar) under E05 og E09.

### E15 – Ubemannet drift og feilinjeksjon 🔴
- **Metode:** Først 10 tørrkjøringer uten deig, deretter 5 kjøringer med vann og til slutt 3 med deig. Feilinjeksjon: koble fra en temperaturføler, simuler et fastlåst SSR (termosikringen skal løse ut), strømbrudd midt i et program, tapt nettverk og fastkjørt motor.
- **Bestått når:** Alle feil gir en trygg tilstand innenfor definert tid: varmen av, motoren av, varsel, og **kjølingen på hvis det finnes deig** i kammeret, slik at deigen ikke overgjærer. Se [`06-sikkerhet.md`](06-sikkerhet.md).

### E16 – Kaldhold 🔴
- **Hypotese:** Deig som har hatt kald heving, kan holdes ved 4–6 °C i minst 12 t ekstra med ≤ 10 % tap på brødkortet.
- **Metode:** Lag én deig (variant A eller B), del den i tre og stek etter 0, 12 og 24 t ekstra kaldhold. Gjenta med en ny deig. Mål pH og smak (blindtest).
- **Konsekvens:** Bestemmer hvor stort «stekevindu» maskinen kan love. Akseptansekriterium 3 bygger på resultatet.

## Utstyr til eksperimentene i fase 0–1

Se [`09-budsjett-og-innkjop.md`](09-budsjett-og-innkjop.md). Det meste kan gjøres med en kjøkkenmaskin, en jerngryte, en vanlig ovn, en hevekasse (bygges i fase 1) og et ESP32-basert måleoppsett.
