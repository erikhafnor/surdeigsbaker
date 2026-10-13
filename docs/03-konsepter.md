# 03 – Konseptalternativer

Det viktigste valget i arkitekturen er **hvor mange ganger deigen må flyttes**, og **hvor kjøling og steking skjer**. Under er fem konsepter. Endelig valg tas ved port G3 med Pugh-matrisen nederst, oppdatert med resultater fra eksperimentene. Valget dokumenteres som ADR-001 i [`beslutninger/`](beslutninger/).

## A – Hacket brødmaskin (ett kar, formbrød)

En brukt brødmaskin får ny styring: egen mikrokontroller, egne sensorer og egne program. Alt skjer i brødformen med padle.

```text
┌──────────────────────┐
│  lokk (vindu)        │
│ ┌──────────────────┐ │
│ │  brødform (PTFE) │ │  ← elting, heving og steking i samme form
│ │      padle       │ │
│ └──────────────────┘ │
│ varmeelement  motor  │  ← ny styring: ESP32, SSR og egne sensorer
└──────────────────────┘
```

- **+** Ingen overføringer. Billig (brukt fra Finn.no). Rask vei til *første maskinbakte surdeigsbrød*. Gir læring i styring, sikkerhet og fastvare.
- **−** Formbrød med hull etter padlen. Lav ovnstemperatur gir blek skorpe. Ingen kjøling. Ikke den skorpa vi vil ha.
- **Rolle i planen:** «Gangbart skjelett» i fase 2. Valgfritt, men anbefalt.

## B – Modulære stasjoner

Separate moduler: surdeigsmodul, blander, hevekammer og ovn. Deigen flyttes mellom dem av et menneske, eller etter hvert av en mekanisme.

- **+** Hver modul kan utvikles og testes for seg. Fleksibelt, og alle trinn er mulige.
- **−** Mange overføringer. Stort fotavtrykk. Overføringene må automatiseres for å nå N3.

## C – Bolle over gryte (to kar og tyngdekraft) ⭐ foreløpig favoritt

En temperaturstyrt elte- og hevebolle står **over** en elektrisk oppvarmet gryte med lokk. Etter bulkheving og eventuell kald heving i bollen åpnes lokket på den varme gryta. Bollen vippes, og deigen glir ned. Lokket lukkes, og brødet stekes.

```text
┌───────────────────────────────────┐
│  Melbeholder      Vann/saltlake   │  ← påfylles ukentlig (N3)
│   (snegle)          (pumpe)       │
├───────────────────────────────────┤
│   Elte- og hevebolle (vippbar)    │  ← 4–30 °C (varme og kjøling)
│   på lastceller, ToF-sensor       │     krok med egen motor
├─────── termisk skille / luke ─────┤
│   Gryte med lokk (≤ 260 °C)       │  ← egne varmeelementer
│   motorisert lokk                 │     uavhengig termosikring
└───────────────────────────────────┘
```

- **+** Bare **én** overføring, og den gjøres av tyngdekraften. Kald heving skjer i bollen, der det ikke er ovnsvarme, så kjøleenheten (kompressor eller Peltier) er beskyttet. Kald deig er stivere og lettere å overføre. Jerngryteskorpe som i referansen. Kompakt.
- **−** Overføringen fra bollen er den største risikoen (deigen kan sette seg fast eller rives, E10). Lokket må åpnes og lukkes mot en varm gryte. Bollen må skjermes mot varme fra gryta.
- **Kritiske eksperimenter:** E06 (uten forming), E07 (sømsiden opp), E09 (kald bulkheving) og E10 (slipp fra bollen).

## D – Heving i stekebeholderen (kaldstart)

Som C, men deigen overføres til en **kald** gryte med bakepapir rett etter bulkhevingen. Den etterheves i gryta, og så varmes gryta opp med deigen i (kaldstart).

- **+** Ingen overføring til varm gryte, og lokket trenger ikke åpnes mot varme. Bakepapiret kan fungere som slynge.
- **−** Kaldstart kan gi mindre ovnsspretthet og svakere skorpe (testes i E08). Kald *etter*heving må skje i ovnsrommet, og der er Peltier vanskelig. Lettere gryter (mindre termisk masse) kan være nødvendig.
- **Rolle:** Reserveplan hvis E10 viser at overføring til varm gryte er for vanskelig, eller hvis E08 viser at kaldstart er godt nok.

## E – Kombidampovn og robotarm

Kjøpt kombidampovn med heve- og dampfunksjon (f.eks. Anova Precision Oven), kjøkkenmaskin og en robotarm som flytter deigen.

- **+** Gjenbruker ferdige og sertifiserte apparater. Ovnen har allerede damp og hevemodus. Robotarmen åpner for forming senere (N5).
- **−** Dyrt og stort. Programmering av robotarmen er et eget prosjekt. Dårlig egnet som DIY-oppskrift.

## Foreløpig Pugh-matrise

Konsept C er referanse (0). De andre konseptene vurderes mot C fra −2 (mye dårligere) til +2 (mye bedre). Vektene skal kalibreres i fase 0. Poengene oppdateres etter eksperimentene i fase 1 og 3.

| Kriterium | Vekt | A | B | C | D | E |
|---|---|---|---|---|---|---|
| Brødkvalitet (skorpe og volum) | 5 | −2 | 0 | 0 | −1 | +1 |
| Teknisk risiko (lav er bra) | 4 | +2 | −1 | 0 | +1 | −2 |
| Automasjonsnivå mulig i v1 | 4 | −1 | −1 | 0 | 0 | 0 |
| Kostnad | 3 | +2 | −1 | 0 | 0 | −2 |
| Fotavtrykk på benken | 3 | +1 | −2 | 0 | 0 | −2 |
| Rengjøring | 3 | +1 | −1 | 0 | 0 | −1 |
| Byggbarhet som DIY | 3 | +2 | 0 | 0 | 0 | −2 |
| Tid til første brød | 2 | +2 | −1 | 0 | 0 | −1 |
| **Vektet sum** | | **+16** | **−22** | **0** | **−1** | **−26** |

Matrisen må leses riktig. A skårer høyt fordi den er enkel og billig, men den oppfyller ikke det viktigste kravet om skorpe og volum. Den egner seg derfor som skjelett, ikke som mål. **C og D er de reelle kandidatene for prototype v1**, og eksperimentene E08 og E10 avgjør mellom dem.

## Anbefaling

1. **Fase 2:** Bygg konsept A som gangbart skjelett. Da får du styring, sikkerhetslag, oppskriftsmotor og logging på plass, og du får det første maskinbakte surdeigsbrødet tidlig.
2. **Fase 3:** Bygg delsystemene til C, og hold D åpen som reserveplan til E08 og E10 er gjennomført.
3. **Fase 4:** Integrer det valgte konseptet til prototype v1.
