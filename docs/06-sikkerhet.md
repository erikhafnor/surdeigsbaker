# 06 – Sikkerhet, matkontakt og regelverk

> ⚠️ **Dette er ikke juridisk eller elfaglig rådgivning.** Maskinen kobles til 230 V, har et varmeelement på ca. 2 kW, kommer opp i ca. 250 °C og skal gå ubemannet. Les dokumentet før du kobler noe til strømnettet, og få en fagperson til å se på løsningen når du er usikker. Punkter merket ⚠️ er ikke bekreftet i primærkilder ennå.

Matlaging på komfyren er den største enkeltårsaken til boligbranner i Norge. Ifølge DSB var 43 % av brannvesenets utrykninger til boligbranner i 2016 komfyrbranner. Maskinen vår er i praksis en liten ovn som står alene om natten. Sikkerheten bygges derfor inn **fra første prototype**, også i den hackede brødmaskinen.

## 1. Sikkerhetsarkitektur: tre uavhengige lag

```text
Lag 3  Programvare i hovedstyringen    grenser per trinn, makstid, sensorsjekk, varsling
Lag 2  Sikkerhetsvakt (egen MCU/krets) watchdog, overtemperatur, frakobling via relé/kontaktor
Lag 1  Ren maskinvare                  termosikring + manuell-reset termostat i serie med element
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
- [ ] **Høytemperaturledning** (silikon, PTFE eller glassfiber) i varme soner. Strekkavlastning på alle ledninger.

### Varme og brann

- [ ] **Termosikring som ikke kan tilbakestilles** og **termostat med manuell tilbakestilling**, begge i serie med *hvert* varmeelement og montert nær elementet. Utløserverdien skal ligge under det laveste materialet tåler.
- [ ] **SSR svikter ofte ved at det står lukket.** Sett derfor et mekanisk relé eller en kontaktor i serie, styrt av sikkerhetsvakten (lag 2). Kontaktoren skal bryte begge poler.
- [ ] **Varmen er av ved enhver omstart, ethvert spenningsfall og enhver programvarefeil.** Standardtilstanden er alltid «av».
- [ ] **Sensorovervåking:** åpen krets, kortslutning og urimelig temperaturstigning (både for raskt og for sakte, slik termisk runaway-beskyttelse virker på 3D-skrivere). Hver fase har en makstid.
- [ ] **Overtemperaturføler i elektronikkrommet.** Den skal også overvåke Peltier-elementet.
- [ ] **Røykvarsler** like ved, helst tilkoblet slik at den kan slå av maskinen og varsle.
- [ ] **Plassering:** på et underlag som ikke brenner og med klaring rundt. Overskap over stekesonen må vurderes særskilt (overflatetemperatur og ventilasjon), og kravet tas med i kravspesifikasjonen.
- [ ] **Ingen ubemannet drift før E15 er bestått** ([eksperimentplanen](05-eksperimenter.md)).

### Mekanisk

- [ ] **Lokk- og dekselbrytere** (interlock) for elte- og vippemekanismene
- [ ] **Overvåking av fastkjørt motor** (overstrøm og blokkering)
- [ ] **Lokal stoppknapp** som bryter motorer og varme, uavhengig av programvaren

### Fjernstyring

Prinsipper hentet fra IEC 60335-1 (avsnitt 22.49–22.51) ⚠️:

- [ ] Fjernstyring må aktiveres **på maskinen** og vises med en indikator. Betjening på maskinen går foran fjernstyring.
- [ ] Driftstid og program låses **før** fjernstart.
- [ ] Fjernstyring kan **aldri** heve temperatur- eller tidsgrenser eller overstyre beskyttelsesfunksjoner.
- [ ] Maskinen skal fungere **helt lokalt**, uten skytjeneste. Nettverk er en tilleggsfunksjon.

## 3. Matkontakt og hygiene

### Materialer

| Materiale | Bruk | Merknad |
|---|---|---|
| Rustfritt stål 304/316 | Bolle, krok, skrue- eller sneglemater, rammedeler med matkontakt | Førstevalget |
| Matgodkjent, ettervulkanisert silikon | Pakninger, slanger og skraper | Krev dokumentasjon. Det finnes ingen harmonisert EU-regel for silikon. |
| Emaljert støpejern, karbonstål | Stekegryte | Klassisk løsning, men tung |
| PTFE-belegg (non-stick) | **Bare** i kalde soner, f.eks. bollen | Brytes ned fra ca. **260 °C**, og ved ca. 350 °C dannes giftig røyk («polymer fume fever»). **Skal ikke brukes i stekesonen.** Merk at referanseoppskriften forvarmer til 260 °C. |
| Ubehandlet aluminium | ❌ | BfR fraråder aluminium sammen med sur og salt mat, og surdeig er sur |
| 3D-print (PLA/PETG) | ❌ ikke i matkontakt eller varme soner | Lagene kan huse bakterier. PLA mykner fra ca. 55–65 °C og PETG fra ca. 80 °C. Messingdyser kan inneholde bly. |
| Smøremidler | Lukkede drev utenfor matsonen, eller NSF H1-godkjent smøremiddel | |

Regelverk: EU-forordning 1935/2004 (rammeforordningen), 2023/2006 (god produksjonspraksis) og 10/2011 (plast). I Norge gjennomføres dette i matkontaktforskriften.

### Prosesshygiene

- **Rått mel er en råvare med smitterisiko** (f.eks. E. coli). Det er stekingen som gjør brødet trygt. Mel- og deigbanen behandles som en «rå sone».
- **Mager deig over natten er normalt.** Gjæringen senker pH og holder sykdomsbakterier tilbake, men dreper dem ikke. Ingredienser som melk, egg eller ost krever kjøling eller sperre mot utsatt start ⚠️.
- **Ingen varm og fuktig oppbevaring etter steking.** Sporer fra *Bacillus* overlever stekingen og kan gi «trådtrekk» (rope) i varm og fuktig krumme. Ventiler og avkjøl brødet.
- **Melbeholderen skal være tett og tørr**, langt fra damp og varme. Mugg vokser over vannaktivitet ca. 0,70–0,75, og mel trekker raskt fukt over ca. 70 % relativ luftfuktighet.
- **Rengjøring:** Alt som er i kontakt med mat skal være avtakbart og glatt, uten sprekker og helst tåle oppvaskmaskin. Rester av surdeig mugner.

## 4. Regelverk: egen bruk, deling og salg

| Situasjon | Hva gjelder (foreløpig vurdering) |
|---|---|
| **Bygget for egen bruk** | Trolig ikke «å gjøre tilgjengelig på markedet». Du er likevel ansvarlig for at utstyret er i forsvarlig stand (FEL). Forsikringen kan avkortes ved feil. **Spør DSB** om tilfellet ditt. |
| **Publisere tegninger og kode åpent** | Trolig ingen produktplikt (analogt med Cyber Resilience Act, der det å legge åpen kildekode på et repo ikke regnes som å gjøre noe tilgjengelig) ⚠️. Ikke påstå CE-samsvar, og ha tydelige advarsler. |
| **Gi bort eller selge ferdige maskiner eller byggesett** | Du blir trolig **produsent**. Det betyr risikovurdering, testing mot EN 60335-1 og 60335-2-9 (som eksplisitt omfatter brødmaskiner) og 60335-2-14 (kjøkkenmaskiner), teknisk dokumentasjon, samsvarserklæring, CE-merking og bruksanvisning. Byggesett omfattes også av EMC-direktivet. Har maskinen Wi-Fi eller Bluetooth, gjelder radioutstyrsdirektivet (RED) og dets cybersikkerhetskrav (EN 18031, gjeldende fra august 2025). Produktansvarsloven gir objektivt ansvar. |

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
- **Testlaboratorium (f.eks. Nemko):** Før byggesett eller ferdige maskiner deles ut. Kjøp IEC 60335-1, 60335-2-9 og 60335-2-14 for å få eksakte grenser for overflatetemperatur, unormal drift og krav til bruksanvisningen.
- **Forsikringsselskapet ditt:** Før maskinen går ubemannet hjemme.
- **Mattilsynet:** Hvis du leverer deler som kommer i kontakt med mat til andre.
