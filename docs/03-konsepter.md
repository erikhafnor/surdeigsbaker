# 03 – Konseptalternativer

Maskinen leverer **stekeklar deig**, og stekingen skjer i vanlig ovn ([ADR-006](beslutninger/ADR-006-steking-i-vanlig-ovn.md)). Da er de viktigste valgene i arkitekturen:

- **Hvordan elter og bearbeider maskinen deigen?** Brødmaskinpadle, krok eller kjøkkenmaskin.
- **Hvordan kjøles og varmes kammeret?** Kompressor eller Peltier.
- **Hvordan får mennesket deigen ut?** Avtakbar bolle eller hevekurv.

Under er fire konsepter. Endelig valg tas ved port G3 med Pugh-matrisen nederst, oppdatert med resultater fra eksperimentene. Valget dokumenteres som ADR-001 i [`beslutninger/`](beslutninger/).

## K1 – Brødmaskin i kjøleskap

Drivverket og formen fra en brukt brødmaskin bygges inn i et **ombygd lite vinkjøleskap eller en kjøleboks med kompressor**. Den får ny styring, et svakt varmeelement og egne sensorer.

```text
┌───────────────────────────────┐
│ isolert kammer (vinkjøleskap) │ ← kompressor 4–6 °C, varmefolie til 24–30 °C
│   ┌──────────────┐            │
│   │ brødform     │  ToF ↓     │ ← avtakbar form med slippbelegg
│   │   padle      │            │
│   └──────┬───────┘            │
│      eltemotor (fra brødmaskin) │
│ ESP32 · SSR/relé · termosikring │
└───────────────────────────────┘
```

- **+**
  - Billig: brødmaskin og vinkjøleskap kan kjøpes brukt på Finn.no.
  - Kort vei til *første maskinlagde surdeigsdeig*.
  - Brødformen er laget for elting og er lett å vaske.
  - Høy DIY-verdi: mange kan bygge den.
- **−**
  - Brødmaskinpadlen behandler deigen grovere enn en krok.
  - Formen er høy og smal, noe som er dårlig for å se og måle bulkhevingen.
  - Motorvarmen havner i kjølekammeret.
  - Lite plass til en hevekurv, og vanskelig å dosere ovenfra (N3).
- **Rolle i planen:** Gangbart skjelett i fase 2. Kan bli en egen, enkel DIY-variant («Surdeigsbaker Mini»).

## K2 – Eltebolle i hevekammer ⭐ foreløpig favoritt

Et isolert kammer med kompressorkjøling og svak varme. I kammeret står en **avtakbar bolle i rustfritt stål** på lastceller, og en **eltekrok som drives ovenfra** av en girmotor i lokket. Lokket har også ToF-sensor og innløp for dosering. Kammeret har plass til en hevekurv ved siden av eller i stedet for bollen.

```text
┌───────────────────────────────────┐
│  Melbeholder      Vann/saltlake   │ ← påfylles ukentlig (N3)
├────────── lokk ───────────────────┤
│  girmotor → krok   ToF   innløp   │
├───────────────────────────────────┤
│   avtakbar bolle (rustfritt)      │ ← 4–30 °C
│   på lastceller   │ plass til     │
│                   │ hevekurv      │
│ kompressor · varme · ESP32/MCU    │
└───────────────────────────────────┘
```

- **+**
  - Kroken gir god deigbehandling og fungerer godt til korte bretterunder (E05).
  - Bulkhevingen er lett å måle ovenfra.
  - Dosering ovenfra gjør N3 mulig.
  - Bollen og kroken tåler oppvaskmaskin.
  - Støtter begge overleveringsvariantene («tipp og stek» og «med forming»).
- **−**
  - Mer mekanisk arbeid: lokk med motor og en kobling som må kunne løftes av.
  - Motorvarme og kondens i kammeret må håndteres.
- **Kritiske eksperimenter:** E05 (bretting med krok), E06 (uten forming), E09 (kald bulkheving), E10 (overlevering) og E13 (kjøling).

## K3 – Kjøkkenmaskin og smart hevekabinett

Den kjøkkenmaskinen du har, brukes til elting. Det som bygges, er bare et **smart hevekabinett** med varme, kjøling, hevemåling, tidsplan og varsling. Mennesket flytter bollen mellom kjøkkenmaskinen og kabinettet og gjør bretting og forming.

- **+**
  - Lavest teknisk risiko.
  - Raskest i bruk: dette er hevekassen fra fase 1.
  - Gir referansekvalitet, fordi mennesket gjør alle håndgrepene.
  - Nyttig i hverdagen allerede på N1.
- **−**
  - Lav automasjon: mennesket må gjøre flere grep og være til stede oftere.
  - To apparater på benken.
- **Rolle i planen:** Første nyttige milepæl (N1), og plattformen for alle eksperimentene i fase 1.

## K4 – Heving i stekegryta (kaldstart)

Den siste hevingen skjer i din egen jerngryte, med bakepapir, inne i maskinens kammer. Ved stekeklar tid setter du hele gryta i en **kald** ovn og steker med kaldstart.

- **+** Ingen tipping av deig. Bakepapiret fungerer som slynge.
- **−**
  - Kaldstart kan gi mindre ovnsspretthet (E08).
  - Kammeret må romme en tung støpejernsgryte, og det er mye masse å kjøle ned.
  - Kald emaljert gryte inn i varm ovn må unngås, fordi emaljen kan sprekke av temperatursjokk.
- **Rolle:** Variant å teste i E08. Ikke prioritert.

## Foreløpig Pugh-matrise

Konsept K2 er referanse (0). De andre konseptene vurderes mot K2 fra −2 (mye dårligere) til +2 (mye bedre). Vektene skal kalibreres i fase 0. Poengene oppdateres etter eksperimentene i fase 1 og 3.

| Kriterium | Vekt | K1 | K2 | K3 | K4 |
|---|---|---|---|---|---|
| Deigkvalitet | 5 | −1 | 0 | +1 | −1 |
| Teknisk risiko (lav er bra) | 4 | +1 | 0 | +2 | 0 |
| Automasjonsnivå mulig i v1 | 4 | −1 | 0 | −2 | 0 |
| Kostnad | 3 | +2 | 0 | +1 | 0 |
| Fotavtrykk på benken | 3 | 0 | 0 | −1 | −1 |
| Rengjøring | 3 | 0 | 0 | 0 | 0 |
| Byggbarhet som DIY | 3 | +1 | 0 | +2 | 0 |
| Tid til første brød | 2 | +2 | 0 | +2 | 0 |
| **Vektet sum** | | **+8** | **0** | **+15** | **−8** |

Matrisen må leses riktig. K3 skårer høyest fordi den er enkel, men den når bare N1. K1 er billig og rask, men egner seg dårlig for dosering (N3). **K2 er den reelle kandidaten for prototype v1 (N3).** K1 og K3 er trinn på veien dit, og de er nyttige ferdige maskiner i seg selv.

## Anbefaling: en trapp der hvert trinn er nyttig

1. **Fase 1, K3 (N1):** Bygg hevekabinettet: et ombygd vinkjøleskap med varme, sensorer og tidsplan. Det er eksperimentkammeret i fase 1, og allerede et nyttig apparat.
2. **Fase 2, K1 (N2):** Sett drivverket og formen fra en brødmaskin inn i kabinettet. Det gir det første maskinlagde surdeigsbrødet.
3. **Fase 3–4, K2 (N3):** Bygg den egentlige eltemodulen med bolle, krok, vekt og dosering i et kammer som er bygd for formålet, og integrer den til prototype v1.
