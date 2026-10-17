# 04 – Veikart: fra idé til første brød

Planen går i seks faser. Hver fase avsluttes med en **port** (G0–G5): et sett med kriterier som må være oppfylt før neste fase starter for fullt. Fasene overlapper med vilje. Eksperimentene i én fase gir data til designet i den neste.

Tidsanslagene forutsetter **hobbytempo, ca. 6–10 timer i uka**, og er grove. De justeres ved hver port.

> **Oppdatert 2026-10-17:** Prosjektet hopper over v0 og går rett på **prototype v1** ([ADR-010](beslutninger/ADR-010-v1-arkitektur.md)). v1 er designet med brødmaskinform, vekt, dosering av mel, salt og vann, og en tidsplanlegger som er testet i simulering. Fase 2 er nå å bygge v1, og fase 3 er å kalibrere og forbedre delsystemene i den. Konseptvalget (ADR-001) er avgjort. Byggeveiledningen ligger i [`hardware/v1/`](../hardware/v1/README.md).

```mermaid
gantt
    title Surdeigsbaker – grovt veikart (hobbytempo)
    dateFormat  YYYY-MM-DD
    axisFormat  %b %y
    section Fase 0
    Oppstart og forstudie               :f0, 2026-10-19, 6w
    E01 Referansebrød ×3                :e01, 2026-10-24, 4w
    section Fase 1
    Prosesseksperimenter E02–E09, E16 (for hånd og i v1) :f1b, 2026-11-09, 10w
    section Fase 2 – bygg v1
    Giver, kjøp og mål delene           :v1a, 2026-10-19, 5w
    Print                               :v1b, 2026-11-09, 4w
    Montering og kabling                :v1c, 2026-12-07, 4w
    E11 melskrue og E17 elting          :milestone, e17, 2027-01-11, 0d
    M2 Første brød fra v1               :milestone, m2, 2027-02-01, 0d
    section Fase 3 – kalibrering
    Dosering, varme, heving og modell (E02, E11–E14) :f3, 2027-02-01, 10w
    section Fase 4
    N3 hele dagen, E15                  :f4, 2027-04-12, 6w
    M4 Tre brød på rad fra v1           :milestone, m4, 2027-05-24, 0d
    section Fase 5
    Dokumentasjon og DIY-klargjøring    :f5, 2027-06-14, 8w
```

## Fase 0 – Oppstart og forstudie (uke 1–6)

**Mål:** Forstå feltet, etablere referansen og fryse kravene.

- [ ] Opprett repoet, GitHub-prosjekttavle og etiketter (`eksperiment`, `bakelogg`, `research`, `hardware`, `firmware`, `sikkerhet`)
- [ ] **E01:** Bak referansebrødet tre ganger med full logg, og gjør skjeemål om til gram
- [ ] Forstudie FO1–FO8 etter [forskningsplanen](02-forskningsplan.md), med et kort kunnskapsnotat (1–3 sider) per område
- [ ] Analyser kjente løsninger og søk i patenter (FO2)
- [ ] Mål kjøkkenbenken (plass under overskap, plassering av stikkontakt og hvilken sikringskurs den har)
- [ ] Velg plattform for måleoppsettet i fase 1 (ADR-002, se [arkitektur](07-arkitektur.md))
- [ ] Sett opp verktøykjeden for agentstyrt design ([`10-verktoykjede.md`](10-verktoykjede.md), ADR-005). Installer de låste versjonene, legg inn CI-sjekker og test sikkerhetssperrene i `.claude/settings.json`.
- [ ] Innfør en månedlig rutine for å skanne nye verktøy og MCP-servere
- [ ] Bestill deler til fase 1 ([handleliste](09-budsjett-og-innkjop.md))

**Port G0:** Kravspesifikasjon v1 er frosset (oppdatert [`00-visjon-og-suksesskriterier.md`](00-visjon-og-suksesskriterier.md)), E01 er fullført og alle kunnskapsnotatene er skrevet.

## Fase 1 – Smart hevekabinett (K3) og maskinvennlig oppskrift (uke 4–12)

**Mål:** Bygge hevekabinettet, som er første nyttige maskin (N1). Finne ut hvilke håndgrep maskinen *ikke* trenger å gjøre, og lage en fermenteringsmodell.

- [ ] Bygg måleoppsettet: ESP32 med temperaturfølere, ToF-sensor, lastcelle og logging til dashboard eller CSV. ESPHome-oppsettet valideres og kompileres i CI og testes i Wokwi før et menneske flasher det.
- [ ] ~~Bygg hevekabinettet (K3)~~ **Valgfritt.** v1 har varme, vekt, hevemåling og logging, og kan brukes som eksperimentkammer når den er bygget.
- [ ] Kjør E02 og E03 (surdeigskinetikk og «klar»-signal)
- [ ] Kjør E04–E09 og E16 (forenklinger av prosessen og ventevinduet etter bulk) med kjøkkenmaskin, kjøleskap og vanlig ovn
- [x] Fermenteringsmodell v1, utkast ([gjæringsmodellen](forskning/v1-gjaeringsmodell.md)). Kalibreres med ekte bakinger (E02).
- [ ] Maskinvennlig oppskrift v1 ([`oppskrifter/maskinvennlig-v0.yaml`](../oppskrifter/maskinvennlig-v0.yaml))

**Port G1:** H0 er bekreftet eller avkreftet. Det betyr at vi vet om overleveringen skal være «tipp og stek» eller «med forming». Modellen treffer innenfor ±1 t, og vi vet hvor lenge deigen kan vente ved romtemperatur etter bulk (E16).

## Fase 2 – Bygg v1 (uke 1–15)

**Mål:** Prototype v1 på benken, slik at den kan blande, elte, bulkheve med bretting og varsle når deigen er klar for forming, med deler av doseringen i drift. Hele kjeden fra fastvare til sikkerhet skal fungere på ekte maskinvare.

Alt som trengs, ligger i [`hardware/v1/`](../hardware/v1/README.md): STL, STEP, DXF, stykkliste, koblingsskjema og byggeveiledning. Fastvaren ligger i [`firmware/v1/`](../firmware/v1/README.md).

- [ ] Kjøp en brukt Panasonic SD-2500/2501/ZB2502 (giver). Bak et brød med maskinens deigprogram, og **mål formen og koblingen**.
- [ ] Kjøp girmotor, lastcelle, pumpe og moduler, og **mål dem**. Oppdater [`hardware/spec/v1.yaml`](../hardware/spec/v1.yaml) og bygg CAD på nytt.
- [ ] Bestill profiler (kappet) og plater (kappet etter DXF)
- [ ] Print delene ([`printliste.md`](../hardware/v1/printliste.md)). Formholderen først, som passformtest mot formen.
- [ ] Monter ramme, lastcelle og plattform, drivverk, kammer, tårn, tak, beholdere og dør
- [ ] Idriftsetting trinn for trinn ([§ 8](../hardware/v1/README.md#8-idriftsetting)): uten strøm, uten last, fastvare, vekta og veiespalten, ToF, klaffer
- [ ] **E11 og E12:** Dosering av mel, salt og vann. Melskruen er den største tekniske risikoen.
- [ ] **E17: Eltetest** med 77 % deig i formen
- [ ] Test sikkerhetskjeden: dørbryter, nødstopp, KSD301, termosikring og føler som mangler
- [ ] Bak etter den maskinvennlige oppskriften og stek i vanlig ovn

**Port G2 / milepæl M2:** 🍞 *Første brød av deig laget i v1.* Dørbryteren, nødstoppen og varmevernet er testet og virker.

## Fase 3 – Kalibrering og forbedring av delsystemene (uke 15–25)

**Mål:** Hvert delsystem i v1 oppfyller spesifikasjonen sin.

- [x] ~~ADR-001: Konseptvalg for v1~~ Avgjort i [ADR-010](beslutninger/ADR-010-v1-arkitektur.md)
- [ ] Gjæringsmodellen kalibreres med 5–10 loggførte bakinger (E02). Standardverdiene i fastvaren oppdateres.
- [ ] Dosering innenfor ±1 % for mel og vann og ±0,5 g for salt (E11, E12). Reserveplan for melet: forhåndsveide porsjoner (N2).
- [ ] Varmen holder deigen innenfor ±0,5 °C (E13), og hevingen måles innenfor ±5 prosentpoeng (E14)
- [ ] Bretting med eltebladet (E05) og uttak av deigen fra formen (E10)
- [ ] Kretskort i KiCad 10 i stedet for hullkortet. Fortsatt bare 24 V (SELV). Se [verktøykjeden](10-verktoykjede.md).

**Port G3:** Alle delsystemene har bestått testene sine.

## Fase 4 – Prototype v1 på N3 (uke 25–31)

**Mål:** Én maskin på benken som leverer deig klar for forming til planlagt tid, og som doserer selv (N3).

- [ ] Hele dager på N3: 1–2 ss surdeig om morgenen, deig klar for forming til valgt tid
- [ ] **E15:** Ubemannet drift og feilinjeksjon (krav før første kjøring over natten)
- [ ] Første integrerte bakinger (stekt i vanlig ovn), og deretter iterasjon til akseptansekriteriene er nådd

**Port G4 / milepæl M4:** 🎉 **I MÅL.** Alle akseptansekriteriene i [`00-visjon-og-suksesskriterier.md`](00-visjon-og-suksesskriterier.md) er oppfylt, inkludert tre godkjente brød på rad.

## Fase 5 – Dokumentasjon og DIY-klargjøring (etter M4)

- [ ] Oppdater stykklisten, byggeveiledningen (med bilder fra byggingen), koblingsskjemaet og kalibreringsprosedyren etter erfaringene
- [ ] Fastvare v1.0 og oppskriftsbibliotek
- [ ] Prosjektside med byggelogg (f.eks. Hackaday.io eller blogg) og invitasjon til andre som vil bygge
- [ ] Skisse til v2: Surhild-modulen (N4), forming (N5) og eventuell integrasjon med smartovn
- [ ] Vurder en enkel DIY-variant basert på K1 («Surdeigsbaker Mini»)

**Port G5:** Én annen person har fulgt dokumentasjonen og kommet i gang. Dette er strekkmålet.

## Risikoregister

S = sannsynlighet, K = konsekvens (L = lav, M = middels, H = høy).

| ID | Risiko | S | K | Tiltak | Følges opp i |
|---|---|---|---|---|---|
| R1 | Deigen er vanskelig å få ut av bollen eller kurven, eller mister luft | M | M | E10, slippbelegg (PTFE er greit, siden det ikke er varme), kald deig, mel og hevekurv med klede | Fase 1, 3 |
| R2 | Uformet brød («tipp og stek») blir for dårlig | M | M | E06. Varianten «med forming» er en sikker reserveplan (to korte grep). | Fase 1 |
| R3 | Overoppheting, motorbrann eller elektrisk feil ved ubemannet drift | L | H | Termosikring på varmen, overvåking av motorblokkering, sikkerhetsvakt, jordfeilbryter. Ingen kjøring over natten før E15 er bestått. | Alle |
| R4 | ~~Kjølingen er for svak, gir kondens eller bråker~~ | – | – | Utgår: ingen kjøling ([ADR-007](beslutninger/ADR-007-ingen-kjoling.md)) | – |
| R5 | Meldoseringen er upålitelig (jf. Rotimatic) | H | M | Vannrett skrue med røreverk, klaff og vekt. Reversering ved bro. N2 (forhåndsveide porsjoner) som reserveplan. E11. | Fase 2, 3 |
| R6 | Rengjøringen er så tungvint at maskinen ikke blir brukt | M | H | Avtakbare deler som tåler oppvaskmaskin, designet inn fra start | Fase 3 |
| R7 | Variasjon i surdeigen gjør tidsplanen upresis | **H** | M | Uten kald buffer før forming må temperaturen under bulk justere tiden. Sensorbasert «klar»-signal (E02, E03, E14). Kjøleskapet er bufferen etter forming. | Fase 1, 3 |
| R8 | Prosjektet vokser ut av kontroll, eller motivasjonen forsvinner | H | H | Trapp med nyttige delmål (M1 hevekabinett, M2 deigmaskin), streng avgrensning av v1 og offentlig byggelogg | Alle |
| R9 | Varselet om forming kommer på et upraktisk tidspunkt (f.eks. kl. 02) | M | M | Tidsplanlegger med tillatte tidsrom. Start levain og deig til riktig tid. | Fase 3 |
| R10 | Motorvarme eller fukt skader elektronikken | L | M | Elektronikken og eltemotoren i tårnet, utenfor det fuktige kammeret | Fase 2 |
| R11 | Materialer som ikke er godkjent for matkontakt (3D-print, smøremidler) | M | M | Materialregler i [`06-sikkerhet.md`](06-sikkerhet.md). I v1 berører bare brødformen og eltebladet deigen. Printede deler som berører mel og salt, er av naturfarget PETG etter EU 10/2011. Tettede lager med matgodkjent fett. | Fase 2 |
| R12 | Eltebladet i brødformen klarer ikke 77 % deig, eller melet blir liggende i hjørnene | M | H | **E17** med giveren før bygging. Mel i porsjoner med blanding imellom, retningsskift. Reserve: Unold-form med større volum, lavere hydrering. | Fase 2 |
| R13 | v1 er for høy for plassen under overskapene (526 mm) | M | L | Melet fylles ovenfra: trekk maskinen fram. Døra åpnes forover, så resten går under skapet. Lavere design i v2. | Fase 3 |
| R14 | Noe bærer litt av vekta (kabler, smuler i spalten), og doseringen blir feil | M | M | Spalter ≥ 4 mm, krage med overlapp, myk kabelsløyfe, test med lodd på 100 g ved idriftsetting | Fase 2 |
| R15 | Formen og koblingen fra giveren passer ikke med CAD-målene | M | M | Mål giveren før printing. Holderen og akselen er parametriske. | Fase 2 |

## Arbeidsform

- **Ukerytme:** én baking i uka med bakelogg, og én eller to byggeøkter.
- **Issues:** ett issue per eksperiment og per baking, fra malene i `.github/ISSUE_TEMPLATE`.
- **Beslutninger:** viktige valg skrives som korte ADR-er i [`docs/beslutninger/`](beslutninger/).
- **Portgjennomgang:** ved hver port oppdateres veikartet, risikoregisteret og budsjettet.
- **Åpenhet:** bilder og data fra mislykkede brød legges også ut. Det er gjerne der lærdommen er.
