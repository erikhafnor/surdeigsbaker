# 02 – Forskningsplan

Formålet med researchen er å **ta riktige designvalg tidlig** og unngå å bygge mekanikk for problemer som kan løses enklere i oppskriften. Researchen går i tre spor som går parallelt:

1. **Kunnskap:** litteratur, bøker og fagartikler
2. **Kjente løsninger:** produkter, DIY-prosjekter og patenter
3. **Egne eksperimenter**, se [`05-eksperimenter.md`](05-eksperimenter.md)

Forstudien (oktober 2026) har allerede gitt en del svar. De står under hvert område som *foreløpige funn*. Kildene finnes i [`08-kilder.md`](08-kilder.md).

> **Avgrensning:** Maskinen leverer stekeklar deig, og stekingen skjer i vanlig ovn ([ADR-006](beslutninger/ADR-006-steking-i-vanlig-ovn.md)). Funn om steking er derfor nyttige for brukerveiledningen, men ikke for designet av maskinen.

> **Kildekvalitet:** Forstudien bygger delvis på søkeresultater og forum. Funn merket ⚠️ er ikke bekreftet i primærkilder. De må sjekkes før vi bygger på dem.

## Overordnede forskningsspørsmål

- **HS1:** Kan en maskin på kjøkkenbenken lage en surdeigsdeig som, stekt som referansen i vanlig ovn, får ≥ 80 % av referansebrødets poengsum med høyst to korte manuelle grep (eventuell forming og tipping i gryta)?
- **HS2:** Hvilke trinn i referanseprosessen kan fjernes eller forenkles uten vesentlig kvalitetstap?
- **HS3:** Hva er den enkleste robuste arkitekturen (eltemekanisme, kjøling og overlevering) som oppfyller kravspesifikasjonen?
- **HS5:** Hvor presist kan maskinen treffe «klar for forming kl. X», og hvor lenge kan deigen vente ved romtemperatur uten tap (E16)?
- **HS4:** Hvordan kan maskinen avgjøre *når* et trinn er ferdig, slik at den ikke bare følger klokka?

## Forskningsområder (FO)

### FO1 – Prosess og mikrobiologi

**Spørsmål**
- Hvordan påvirker temperatur, hydrering og andel levain tidene for levain, bulkheving og etterheving?
- Hva gjør autolyse, bretting, forming og kald heving med brødet, og hva skjer når de utelates?
- Hvordan styrer temperatur og hydrering smak og syrlighet (forholdet mellom melkesyre og eddiksyre)?

**Metode:** Litteraturstudie (bøker og oversiktsartikler) og eksperimentene E02 og E04–E09.

**Foreløpige funn**
- Gjæringshastigheten omtrent **dobles for hver ca. 8 °C** økning (tommelfingerregel, Q10 ≈ 2,4). Den gjelder ikke under ca. 10 °C.
- Hevingskurven følger godt en **modifisert Gompertz-kurve** (forsinkelse, akselerasjon, metning). Det gjør den egnet til å forutsi topphevingen fra tidlige målinger.
- Gjæren i surdeig (*Kazachstania humilis*, tidligere *Candida milleri*) har vekstoptimum rundt **27 °C** (Gänzle mfl. 1998). Det støtter et settpunkt på ca. 24–27 °C for surdeigen.
- Et anslag for tiden til topp er t_topp ≈ t_forsinkelse + g(T) · log₂(fortynning). Dette er en egen syntese, ikke en publisert modell, og den må tilpasses vår egen kultur i E02. Én anekdotisk måleserie ved 24 °C (⚠️) ga ca. 5 t ved 1:1:1, 5,5 t ved 1:2:2, 10 t ved 1:5:5 og 17 t ved 1:10:10.
- Ett stort felles forsøk (Global Sourdough Project, 500 surdeiger) fant liten geografisk forskjell mellom surdeiger. Eddiksyrebakterier forklarte mye av variasjonen i hevehastighet og aroma.
- Forholdet mellom melkesyre og eddiksyre kan bare styres i et begrenset område, med temperatur og hydrering. At «kaldere gir mer eddiksyre» er ⚠️ ikke godt dokumentert.

### FO2 – Kjente løsninger og patenter

**Spørsmål:** Hvem har prøvd før, hva fungerte, hva feilet, og hvorfor?

**Metode:** Produktanalyse, DIY-prosjekter, teardown av en brukt brødmaskin (fase 2) og patentsøk (Google Patents, Espacenet). Søkeord: *automatic sourdough*, *bread making apparatus starter culture*, *household dough retarder proofer*, *dough transfer tilting bowl*.

**Foreløpige funn**
- **Ingen hjemmeprodukter automatiserer hele brødet** fra surdeig til ferdig brød. Det er en reell åpning for dette prosjektet.
- **Brødmaskiner** når bare ca. **140–155 °C** i formen, ifølge målinger fra brukere. De gir hull etter padlen, og ingen av dem kan kjøle. For oss er det uviktig, siden vi ikke steker i maskinen. Brødmaskinens drivverk og form er derimot laget for elting og kan brukes i K1.
- **Sourdough Sidekick** (FirstBuild/GE og King Arthur, 2025–26) er en automatisk surdeigsmater med melbeholder, vanntank og omrøring. Den planlegger etter ønsket bakedag og romtemperatur. Den er det nærmeste eksisterende produktet til Surhild-modulen (N4).
- **Brød & Taylor Sourdough Home** holder et glass på opptil 1 L ved 5–50 °C med maks ca. 38 W kjøling. Det viser at et lite Peltier-kammer for surdeigen er realistisk (⚠️ at det er Peltier, er ikke bekreftet av produsenten).
- **Rotimatic** (automatisk flatbrødmaskin) har hatt store problemer med meldosering og deigfeil, og krever godkjente melmerker. Lærdom: **meldosering er den største pålitelighetsrisikoen**, så hold den enkel eller valgfri.
- **Whirlpool Polara** (2002, nedlagt) og **Suvie** viser at «kjøl først, kok etterpå» i samme apparat er gjort før. Lærdom: Feil i kjølingen må oppdages og varsles. De må ikke stille ødelegge tidsplanen.
- **Anova Precision Oven** har et åpent utvikler-API der et program er en liste med trinn, hver med egne inngangs- og utgangsbetingelser. Det er en god modell for oppskriftsformatet vårt.
- **DIY:** Det finnes flere surdeigsmonitorer med ToF-sensor (f.eks. Justin Lams prosjekter, Breadwinner og en e-ink-krukke med SCD30). Brødmaskiner er hacket med Arduino. Gjæringskamre for øl (BrewPi, Fermentrack) har moden styring for varme og kjøling. *The Sourdough Framework* er en åpen bok om surdeig.
- **Industri:** Konisk «rounder» (ett motorisert kjegleelement og en fast spiral) er en mulig enkel formemekanisme for N5. Retarder-proofere varmer langsomt opp fra kald tilstand for å unngå kondens på deigen. Industrielle snitteroboter bruker ultralydkniv eller vannstråle. Snitting er altså vanskelig, og det er greit å la den være valgfri.

### FO3 – Sensorer: hva skal måles og hvordan?

**Spørsmål:** Hvilke størrelser forteller pålitelig at et trinn er ferdig, og hvilke sensorer er praktiske i fuktig og klissent miljø?

**Metode:** Litteratur og eksperimentene E02, E03 og E14.

**Foreløpige funn**
- **Flytetesten er upålitelig.** King Arthur kaller den en myte: Surdeigen kan flyte timer før den har doblet seg, og våte eller grove surdeiger synker selv om de er aktive. Vi bruker heller **heving** (f.eks. dobling) og temperatur, og validerer mot flytetesten i E03.
- **ToF-sensorer:** VL6180X (kort rekkevidde, opptil ca. 200 mm) passer for surdeigsglass. VL53L0X/L1X passer for større avstander, som over bollen. Et dekkvindu foran sensoren gir krysstale og må kalibreres. Ultralyd (HC-SR04) er for unøyaktig (ca. ±1 cm).
- **CO₂:** SCD41/SCD30 er bare spesifisert opp til 5000 ppm og blir mettet i et lukket glass. Til høye nivåer trengs STC31 (0–25 eller 0–100 vol%) eller SprintIR-6S-100 (0–100 %).
- **pH:** Typiske verdier er 3,9–4,1 i surdeig ved topp, 4,6–4,8 i nyblandet deig, 4,2–4,4 i ferdighevet deig og 4,3–4,5 i krummen (⚠️ fra AIB, via forum). Stikkelektroder fungerer til stikkprøver, men ikke til kontinuerlig måling (de tilsmusses og må kalibreres).
- **Ferdig bulkheving:** Målet for heving avhenger av temperaturen. Ved ca. 27 °C stopper man på ca. 30 %, ved ca. 21 °C på ca. 75 %, når kald heving følger etter (⚠️ én kilde). Referansen vår sier 20–25 %. Det må kalibreres i E01 og E09.
- **Ønsket deigtemperatur (DDT):** Vanntemperatur = 4 × DDT − (mel + rom + levain + friksjon). Dette er en klassisk bakerformel. Maskinen kan bruke den til å varme vannet riktig.
- **Referanseinstrument:** Chopin Rheofermentometer (nå KPM Rheo F4) måler deighøyde og gasstrykk i en lukket, temperaturstyrt beholder. Det er i praksis det maskinen vår skal gjøre i enklere form.
- **Ferdig stekt:** Kjernetemperatur på 96–99 °C, og i tillegg vekttap målt med lastcellen.

### FO4 – Mekanikk og håndtering

**Spørsmål**
- Hvordan doseres mel, vann, salt og surdeig nøyaktig og hygienisk?
- Hvilken eltegeometri passer ca. 1 kg deig?
- Hvordan slipper deigen bollen?
- Hvordan blir rengjøringen enkel?

**Metode:** Teardown av en brødmaskin og en kjøkkenmaskin, enkle prototyper og eksperimentene E10–E12.

**Foreløpige funn**
- Saltlake gjør salt til væskedosering. Maskinen kan lage saltlaken selv av tørt salt og vann, så brukeren bare fyller på mel, salt og vann (E12).
- Ved å bygge levain i bollen slipper vi å dosere klissen surdeig.
- No-knead-metoden og sømsiden opp gjør at vi kanskje slipper forming og snitting.
- Ifølge America's Test Kitchen ble no-knead-brød med 80 % hydrering flatt, mens 68 % hevet godt. **Moderat hydrering er viktig for brød uten forming.**

### FO5 – Termikk

**Spørsmål:** Kjøling (Peltier eller kompressor), svak varme, isolasjon, kondens, støy, motorvarme og energibruk per brød.

**Metode:** Beregninger, datablad og E13. Se [`07-arkitektur.md`](07-arkitektur.md).

**Foreløpige funn**
- Peltier er marginalt for et kammer på 15–20 L med 1 kg deig (40–80 W elektrisk). En kompressor (ombygd vinkjøleskap) er omtrent fire ganger mer effektiv.
- Retarder-proofere varmer langsomt opp fra kald tilstand for å unngå kondens på deigen.
- *For brukerveiledningen (E08):* Kaldstart i gryte har blandede resultater. Noen kilder rapporterer liten forskjell, mens andre fikk sammenfalte brød og brent bunn.

### FO6 – Styring og programvare

**Spørsmål:** Plattform for mikrokontrolleren, sanntid og sikkerhet, oppskriftsformat, brukergrensesnitt, logging og lokal drift uten sky.

**Metode:** Sammenligne plattformer (ESP32/ESPHome, Klipper, Raspberry Pi, MadMachine SwiftIO). Bygge en liten prototype i fase 1. Se [`07-arkitektur.md`](07-arkitektur.md).

**Foreløpige funn:** Apparater som er avhengige av en skytjeneste fra produsenten, kan bli ubrukelige når firmaet legges ned (som Mellow). Maskinen skal derfor **fungere helt lokalt**.

### FO7 – Sikkerhet og regelverk

**Spørsmål:** Elektrisk sikkerhet, brannsikkerhet ved ubemannet drift, matkontaktmaterialer og hva som gjelder for egenbygd utstyr, DIY-oppskrifter og byggesett.

**Metode:** Lese regelverk (DSB, Mattilsynet, EU-forordninger) og standarder (IEC 60335-serien), og rådføre seg med en fagperson ved behov. Se [`06-sikkerhet.md`](06-sikkerhet.md).

### FO8 – Brukeropplevelse

**Spørsmål:** Hva *vil* du gjøre selv, og hva vil du slippe? Er forming noe du liker å gjøre (variant B), eller noe du vil slippe (variant A)? Når på døgnet er det greit å få varsel om forming og forvarming? Hvor ofte er det greit å fylle på og vaske? Hvor stille må maskinen være? Hvordan vil du planlegge brødet (app eller knapp)?

**Metode:** Egen dagbok i fase 0 over hva som er kjedelig og hva som er gøy med å bake. Kort spørreundersøkelse blant surdeigsbakere (f.eks. Facebook-grupper, r/Sourdough, The Fresh Loaf).

## Metoder

| Metode | Brukes til | Leveranse |
|---|---|---|
| Litteraturstudie | FO1, FO3, FO5 | Kunnskapsnotat per område |
| Produktanalyse og teardown | FO2, FO4 | Tabell over kjente løsninger og teardown-notat med bilder |
| Patentsøk | FO2 | Liste over relevante patenter og ideer (og et første blikk på fri bruksrett, hvis prosjektet kan bli kommersielt) |
| Eksperimenter (E01–E18) | FO1, FO3–FO5 | Eksperimentrapporter og data i `data/` |
| Nettsamfunn og fagfolk | Alle | Innspill. Mulige fagmiljøer: Nofima (korn- og bakeforskning), lokale håndverksbakerier og makerspace eller verksted ved universitetet |
| Prototyping | FO4–FO6 | Fungerende delsystemer |

**Om eksperimentene:**
- Endre én faktor om gangen, med mindre et faktorforsøk er planlagt.
- Ha minst to repetisjoner.
- Smak blindt når smak er utfallet.
- Logg alt med maler, så resultatene kan sammenlignes.

## Leveranser fra forskningen

1. **Kunnskapsnotater FO1–FO8**, 1–3 sider hver, i `docs/forskning/` (fase 0)
2. **Kravspesifikasjon v1**, frosset ved G0
3. **Maskinvennlig oppskrift v1 og fermenteringsmodell v1** ved G1
4. **ADR-001: konseptvalg** ved G3
5. **Eksperimentrapporter** fortløpende

## Kunnskapshull: der prosjektet kan bidra

Dette fant forstudien **ikke** dokumentert. Det betyr at vi må finne svarene selv, og at svarene er verdifulle å dele:

- Et hjemmeapparat som lager hele surdeigsbrødet automatisk
- En dokumentert hjemmebygd hevekasse som både varmer og kjøler med Peltier, med beskrevet regulering
- Kontrollerte sammenligninger av strekk og brett mot maskinbearbeiding
- Gode og repeterbare sammenligninger av kaldstart og varmstart i gryte (for brukerveiledningen)
- Systematiske data på hvor lenge en surdeigsdeig kan kaldholdes etter kald heving
- Målte CO₂-nivåer i toppen av surdeigsglass over tid
- Formemekanismer i bolleformat for hjemmebruk
