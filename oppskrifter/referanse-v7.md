# Referanseoppskrift: «Det Ultimate Surdeigsbrød» v7.0, oversatt til prosessparametre

**Kilde:** «Det Ultimate Surdeigsbrød, v7.0» av Sven Ole Aase. Oppskriften bygger på *Tartine Bread* (Chad Robertson) og *Open Crumb Mastery* (Trevor J. Wilson).
Originaldokumentet ligger **ikke** i dette repoet, fordi det tilhører forfatteren. Her er bare prosessparametrene hentet ut og omskrevet slik en maskin trenger dem. Tolkninger og omregninger er våre egne.

Oppskriften er **gullstandarden** i prosjektet. Brødet bakes for hånd og logges i fase 0 (eksperiment E01), og maskinen måles mot det.

## Ingredienser (i bakerprosent)

| Ingrediens | Oppskrift | Gram (anslag) | Bakerprosent | Merknad |
|---|---|---|---|---|
| Siktet hvetemel, gjerne høyt protein (f.eks. vårhvete) | 450 g | 450 | 82 % | |
| Fint sammalt mel (spelt, emmer, rug …) | 100 g | 100 | 18 % | |
| Vann, ca. 26 °C | ca. 4,5 dl (start med 4 dl og juster) | 400–450 | 73–82 % | Hydreringen justeres etter melet. Maskinen må enten ha fast oppskrift per mel eller kunne måle deigkonsistens. |
| Fint havsalt | 2 ts | ca. 10–12 | ca. 2 % | **Veies i E01** |
| Levain (matet surdeig) | Alt unntatt 2–3 ss | ca. 100–150 (?) | ca. 18–27 % (?) | **Veies i E01.** Skjeemål må gjøres om til gram. |

### Levain (mating om morgenen, ca. 8 t før blanding)

| Parameter | Verdi | Merknad |
|---|---|---|
| Startkultur | 1–2 ss (ca. 15–30 g?) | Resten kastes |
| Mel | 4 toppede ss siktet hvetemel + 1 toppet ss fint sammalt | ca. 50–75 g (?) |
| Vann | Lunkent, til «tykk velling» | Hydrering ca. 100–120 % (?) |
| Temperatur | «Lun romtemperatur» | Maskinen bør ha et fast settpunkt, f.eks. 26 °C (fastsettes i E02) |
| Tid | ca. 8 t | Avhenger sterkt av temperatur |
| Klar når | Flytetest: en teskje kultur flyter godt i vann | Maskinen trenger en målbar erstatning (heving, CO₂ eller pH, se E03) |
| Ved pause > 4–5 dager | Mat to ganger: først 2–3 ss mel, etter 8 t kast alt unntatt 1–2 ss og mat på nytt | Viktig for surdeigsmodulen (N4) |

(?) = usikker omregning fra skjeemål. Erstattes med veide tall etter E01.

## Prosesstrinn og parametre

Trinn 1–10 er det maskinen skal overta. **Trinn 11–15 gjøres som i dag, i vanlig ovn** ([ADR-006](../docs/beslutninger/ADR-006-steking-i-vanlig-ovn.md)).

| # | Trinn | Tid | Temperatur | Mekanisk handling | Ferdig når |
|---|---|---|---|---|---|
| 1 | Mating av surdeig | ca. 8 t | Lunt (ca. 24–28 °C?) | Dosere, røre | Flytetest bestått |
| 2 | Blanding, mel og vann | – | Vann ca. 26 °C | Røre sammen | Deigen er noenlunde fast. Den skal bare svært langsomt slippe eltekroken. |
| 3 | Autolyse | 25–60 min | Lunt | Ingen. Dekkes til. | Tid |
| 4 | Salt og levain tilsettes | – | – | Dosere. Et par dråper vann på saltet. | – |
| 5 | Elting | ca. 10 min | – | Eltekrok på laveste hastighet | Tid og konsistens |
| 6 | Første heving (bulk) | 2–3 t | Lunt | Strekk og brett i bollen hver 30. min | Deigen har «løsnet skikkelig», ca. 20–25 % volumøkning |
| 7 | Forforming og benkhvile | 30 min | Rom | Skrape ut på benken uten mel og forme en stram, høy bolle | Tid |
| 8 | Endelig forming | – | Rom | Mel, snu, strekk og brett. Gi overflatespenning. | – |
| 9 | Etterheving på benk | 2 t | Rom | I hevekurv med klede og mel, i plastpose | Tid |
| 10 | Kald etterheving | Opptil 24 t (valgfritt) | Kjøleskap (ca. 4 °C) | Ingen | Tid. Gir bedre smak og fleksibel tidsplan. |
| 11 | Forvarming | ≥ 10 min etter at ovnen har nådd 260 °C | 260 °C | Jerngryte med lokk på nederste rille | Gryta er gjennomvarm |
| 12 | Innlegging og snitting | – | – | Helkorn i bunnen, tippe deigen fra kurven og snitte 2–3 mm (luftig deig) til 2–3 cm (fast deig) | – |
| 13 | Steking med lokk | 20 min | 250 °C | – | Tid |
| 14 | Steking uten lokk | 25 min | 200 °C | Ta av lokket | Mørk, nesten brent skorpe |
| 15 | Avkjøling | 1–2 t | Rom | Ut på rist | Best etter 1–2 t |

Kjernetemperatur ved ferdig steking: oppskriften sier ca. 100 °C. Vanlig anbefaling for magre surdeigsbrød er ca. 96–99 °C, og vi bruker ≥ 96 °C som krav.

## Tidslinje (typisk)

```text
Dag 1  07:00  Mat surdeigen ──────────────── ca. 8 t ─┐
       15:00  Bland mel og vann, autolyse 30–60 min  ◄┘
       16:00  Salt + levain, elting 10 min
       16:15  Bulkheving 2–3 t (bretting hver 30. min)
       19:00  Forforming, benkhvile 30 min
       19:30  Endelig forming, inn i hevekurv
       21:30  Inn i kjøleskap (etter 2 t på benken)
Dag 2  ca. 08–19  Forvarm gryte (ca. 45 min), stek 45 min, avkjøl 1–2 t
```

> «Merk at disse tidene er veiledende og vil endres med årstiden.» Det er nettopp denne variasjonen maskinen skal fjerne, ved å styre temperaturen i stedet for å bare følge klokken.

## Nøkkelobservasjoner for maskindesign

- **Temperatur er hovedratten.** Oppskriften bruker «lunt» mange steder. Maskinen erstatter dette med faste settpunkter og kan da regne ut tidene.
- **Kald etterheving er en buffer.** Opptil 24 t i kjøleskap gjør tidsplanen fleksibel. Maskinen har ingen kjøling ([ADR-007](../docs/beslutninger/ADR-007-ingen-kjoling.md)), men det trengs heller ikke: Den kalde etterhevingen skjer i ditt eget kjøleskap, og maskinen trenger bare å treffe tidspunktet for forming.
- **De vanskeligste trinnene for en maskin er 7, 8 og 12** (forming, overføring og snitting). Trinn 12 gjør mennesket uansett ved ovnen. Forming kan enten droppes («tipp og stek») eller gjøres av mennesket på 2–5 min når maskinen varsler. Se E05–E07 og E10 i [eksperimentplanen](../docs/05-eksperimenter.md).
- **Oppskriften er bevisst moderat i hydrering** («Her safer vi!»). Det er en fordel for maskinen, fordi fastere deig er lettere å håndtere, og fordi deig som ikke formes, holder formen bedre ved moderat hydrering.
- **Flytetesten** er et ja/nei-kriterium som er vanskelig å måle automatisk, og den regnes som upålitelig: Surdeigen kan flyte lenge før den har doblet seg, og våte eller grove surdeiger kan synke selv om de er aktive (se [forskningsplanen](../docs/02-forskningsplan.md), FO3). Maskinen bruker heller heving og temperatur, og validerer det mot flytetesten (E03).
