# 06 – Sikkerhet, matkontakt og regelverk

> ⚠️ **Dette er ikke juridisk eller elfaglig rådgivning.** Maskinen kobles til 230 V. Den har en eltemotor på 100–400 W, kjøling (kompressor eller Peltier) og et svakt varmeelement (≤ 100 W), og den skal gå ubemannet i mange timer. Les dokumentet før du kobler noe til strømnettet, og få en fagperson til å se på løsningen når du er usikker. Punkter merket ⚠️ er ikke bekreftet i primærkilder ennå.

Stekingen gjøres i vanlig ovn ([ADR-006](beslutninger/ADR-006-steking-i-vanlig-ovn.md)), så maskinen har ingen høytemperatursone. Det fjerner den største brannrisikoen. Komfyrbranner er den største enkeltårsaken til boligbranner i Norge (43 % av utrykningene til boligbrann i 2016, ifølge DSB). Restrisikoen er likevel reell:

- Et varmeelement som henger seg på inne i et godt isolert kammer, kan bli svært varmt.
- En motor som blokkeres, kan overopphetes.
- Feil på nettspenningssiden kan gi støt eller brann.
- Kjølingen kan svikte i det stille, slik at deigen blir ødelagt.

Sikkerheten bygges derfor inn **fra første prototype**, også i hevekabinettet og skjelettet.

## 1. Sikkerhetsarkitektur: tre uavhengige lag

```text
Lag 3  Programvare i hovedstyringen    grenser per trinn, makstid, sensorsjekk, varsling
Lag 2  Sikkerhetsvakt (egen MCU/krets) watchdog, overtemperatur, frakobling via relé/kontaktor
Lag 1  Ren maskinvare                  termosikring + manuell-reset termostat i serie med varmeelementet,
                                       motorvern (termisk) på eltemotoren
```

Hvert lag skal alene kunne gjøre maskinen trygg dersom lagene over svikter. **Lag 1 skal virke uten strøm til elektronikken og uten programvare.**

## 2. Sjekkliste: sikkerhetsregler for prototypen (må-krav)

### Elektrisk

- [ ] **Bygg maskinen som et apparat med stikkontakt.** Ingen fast installasjon og ingen ny kurs. En lekmann i Norge kan bytte topolede støpsler (opptil 25 A) og skjøteledninger eller apparatkontakter (opptil 16 A). Fast installasjon krever en registrert elvirksomhet (FEK, DSB).
- [ ] **Behandle begge lederne som spenningsførende.** Store deler av Norge har IT-nett, der det ikke finnes noen nøytralleder. Bruk **topolet** hovedbryter og **topolet** sikring eller frakobling.
- [ ] **Klasse I:** Alt tilgjengelig metall jordes, og jordforbindelsen kontrolleres.
- [ ] **Bruk bare kontakter med jordfeilbryter (30 mA).** Mangler boligen jordfeilbryter (vanlig i eldre boliger), skal maskinen kobles via en bærbar jordfeilbryter.
- [ ] **Godkjente delkomponenter:** varmeelementer, strømforsyning og apparatinntak skal være CE/ENEC-merket. Bruk et apparatinntak for høy temperatur (C15/C16) dersom området rundt inntaket blir varmt ⚠️.
- [ ] **Forsterket isolasjon** mellom 230 V og lavspenningssiden (mikrokontroller, sensorer, Wi-Fi). Hold krypestrøms- og luftavstander, og bruk adskilte kabelføringer.
- [ ] **Ledninger** dimensjonert for strømmen og godkjent for kalde og fuktige miljøer (kondens i kammeret). Strekkavlastning på alle ledninger. Elektronikken plasseres i et eget, tørt rom utenfor kjølekammeret.

### Varme og brann

- [ ] **Termosikring som ikke kan tilbakestilles** og **termostat med manuell tilbakestilling**, begge i serie med *hvert* varmeelement og montert nær elementet. Elementet er svakt, men et element som henger seg på i et isolert kammer, er det farligste scenariet. Utløserverdien skal ligge godt under det isolasjon, plast og deig tåler (f.eks. 60–70 °C ⚠️, fastsettes i fase 1).
- [ ] **SSR svikter ofte ved at det står lukket.** Sett derfor et mekanisk relé eller en kontaktor i serie, styrt av sikkerhetsvakten (lag 2). Kontaktoren skal bryte begge poler.
- [ ] **Varmen er av ved enhver omstart, ethvert spenningsfall og enhver programvarefeil.** Standardtilstanden er alltid «av».
- [ ] **Sensorovervåking:** åpen krets, kortslutning og urimelig temperaturstigning (både for raskt og for sakte, slik termisk runaway-beskyttelse virker på 3D-skrivere). Hver fase har en makstid.
- [ ] **Overtemperaturføler i elektronikkrommet**, og på varmsiden av en eventuell Peltier.
- [ ] **Røykvarsler** like ved, helst tilkoblet slik at den kan slå av maskinen og varsle.
- [ ] **Plassering:** Følg kravene til luft rundt kompressoren eller kjøleribben (som for et vinkjøleskap). Hold lufteåpningene frie.
- [ ] **Ingen ubemannet drift før E15 er bestått** ([eksperimentplanen](05-eksperimenter.md)).

### Mekanisk

- [ ] **Lokk- og dekselbrytere** (interlock): Kroken skal stoppe når lokket åpnes eller bollen tas ut
- [ ] **Overvåking av fastkjørt motor** (overstrøm og blokkering) og termisk motorvern
- [ ] **Overvåking av kjølingen:** Avvik i kammertemperaturen gir varsel. Svikter kjølingen mens det står deig i kammeret, varsles brukeren med en gang (lærdom fra Suvie).
- [ ] **Lokal stoppknapp** som bryter motorer og varme, uavhengig av programvaren

### Fjernstyring

Prinsipper hentet fra IEC 60335-1 (avsnitt 22.49–22.51) ⚠️:

- [ ] Fjernstyring må aktiveres **på maskinen** og vises med en indikator. Betjening på maskinen går foran fjernstyring.
- [ ] Driftstid og program låses **før** fjernstart.
- [ ] Fjernstyring kan **aldri** heve temperatur- eller tidsgrenser eller overstyre beskyttelsesfunksjoner.
- [ ] Maskinen skal fungere **helt lokalt**, uten skytjeneste. Nettverk er en tilleggsfunksjon.
- [ ] **Smartovn (eventuell senere integrasjon):** Maskinen kan *foreslå* eller *be om* forvarming, men slår aldri på ovnen uten at brukeren bekrefter det, og bare via ovnens egen fjernstartfunksjon med dens egne sikkerhetssperrer. Ovnen skal være tom bortsett fra gryta. En stekeovn skal ikke fjernstartes når ingen er hjemme.

## 3. Matkontakt og hygiene

### Materialer

| Materiale | Bruk | Merknad |
|---|---|---|
| Rustfritt stål 304/316 | Bolle, krok, skrue- eller sneglemater, rammedeler med matkontakt | Førstevalget |
| Matgodkjent, ettervulkanisert silikon | Pakninger, slanger og skraper | Krev dokumentasjon. Det finnes ingen harmonisert EU-regel for silikon. |
| PTFE-belegg (non-stick) | Bollen, brødformen (K1) | Greit i maskinen, som aldri blir varmere enn ca. 30 °C. PTFE brytes ned fra ca. 260 °C, så PTFE-belagte deler skal **ikke** være med inn i ovnen. |
| Ubehandlet aluminium | ❌ | BfR fraråder aluminium sammen med sur og salt mat, og surdeig er sur |
| 3D-print (PLA/PETG) | ❌ ikke i matkontakt | Lagene kan huse bakterier, og messingdyser kan inneholde bly. Til andre deler: PETG/ASA, som tåler kulde og fukt bedre enn PLA. |
| Smøremidler | Lukkede drev utenfor matsonen, eller NSF H1-godkjent smøremiddel | |

Regelverk: EU-forordning 1935/2004 (rammeforordningen), 2023/2006 (god produksjonspraksis) og 10/2011 (plast). I Norge gjennomføres dette i matkontaktforskriften.

### Prosesshygiene

- **Rått mel er en råvare med smitterisiko** (f.eks. E. coli). Det er stekingen som gjør brødet trygt. Mel- og deigbanen behandles som en «rå sone».
- **Mager deig over natten er normalt.** Gjæringen senker pH og holder sykdomsbakterier tilbake, men dreper dem ikke. Ingredienser som melk, egg eller ost krever kjøling eller sperre mot utsatt start ⚠️.
- **Kaldhold:** Deigen holdes ved ≤ 6 °C fram til steking. Ved strømbrudd eller feil på kjølingen varsles brukeren. Mager deig som overgjærer, er et kvalitetsproblem, ikke et helseproblem, men den bør da kastes eller stekes snarest.
- **Etter steking** (utenfor maskinen): La brødet avkjøles på rist. Sporer fra *Bacillus* overlever stekingen og kan gi «trådtrekk» (rope) i varm og fuktig krumme.
- **Kondens** i kjølekammeret tørkes ut og ventileres mellom kjøringene, så det ikke vokser mugg.
- **Melbeholderen skal være tett og tørr**, utenfor det fuktige kjølekammeret. Mugg vokser over vannaktivitet ca. 0,70–0,75, og mel trekker raskt fukt over ca. 70 % relativ luftfuktighet.
- **Rengjøring:** Alt som er i kontakt med mat skal være avtakbart og glatt, uten sprekker og helst tåle oppvaskmaskin. Rester av surdeig mugner.

## 4. Regelverk: egen bruk, deling og salg

| Situasjon | Hva gjelder (foreløpig vurdering) |
|---|---|
| **Bygget for egen bruk** | Trolig ikke «å gjøre tilgjengelig på markedet». Du er likevel ansvarlig for at utstyret er i forsvarlig stand (FEL). Forsikringen kan avkortes ved feil. **Spør DSB** om tilfellet ditt. |
| **Publisere tegninger og kode åpent** | Trolig ingen produktplikt (analogt med Cyber Resilience Act, der det å legge åpen kildekode på et repo ikke regnes som å gjøre noe tilgjengelig) ⚠️. Ikke påstå CE-samsvar, og ha tydelige advarsler. |
| **Gi bort eller selge ferdige maskiner eller byggesett** | Du blir trolig **produsent**. Det betyr risikovurdering, testing mot EN 60335-1 og trolig 60335-2-14 (kjøkkenmaskiner) og 60335-2-24 (kjøleapparater) ⚠️. 60335-2-9, som omfatter brødmaskiner, er mindre relevant når maskinen ikke steker, teknisk dokumentasjon, samsvarserklæring, CE-merking og bruksanvisning. Byggesett omfattes også av EMC-direktivet. Har maskinen Wi-Fi eller Bluetooth, gjelder radioutstyrsdirektivet (RED) og dets cybersikkerhetskrav (EN 18031, gjeldende fra august 2025). Produktansvarsloven gir objektivt ansvar. |

Relevante regler:
- FEU (forskrift om elektrisk utstyr, 2017 nr. 1598)
- EMC-forskriften (2017 nr. 1597)
- FEL (forskrift om elektriske lavspenningsanlegg)
- FEK (forskrift om elektrisk kompetanse)
- Produktforskriften kap. 2a (RoHS)
- Forordningen om alminnelig produktsikkerhet (GPSR, (EU) 2023/988). Om den er innlemmet i EØS ennå, må sjekkes ⚠️.
- Maskinforordningen (EU) 2023/1230, gjeldende fra 20.1.2027. Husholdningsapparater som omfattes av lavspenningsdirektivet eller RED, er unntatt.

## 5. Når du bør spørre en fagperson

- **DSB:** Hvor går grensen mellom egen bruk og det å gi bort eller dele ut maskiner? Gjelder maskinforskriften? Har GPSR status i Norge?
- **Autorisert elektriker:** For alt utover støpsel og apparatkontakt, og for å bekrefte om boligen har IT-, TT- eller TN-nett.
- **Testlaboratorium (f.eks. Nemko):** Før byggesett eller ferdige maskiner deles ut. Kjøp IEC 60335-1, 60335-2-14 og 60335-2-24 og avklar hvilken del 2 som gjelder, for å få eksakte grenser for overflatetemperatur, unormal drift og krav til bruksanvisningen.
- **Forsikringsselskapet ditt:** Før maskinen går ubemannet hjemme.
- **Mattilsynet:** Hvis du leverer deler som kommer i kontakt med mat til andre.
