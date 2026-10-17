# 07 – Systemarkitektur (utkast)

> **Oppdatert 2026-10-17:** Maskinen har **ingen kjøling** ([ADR-007](beslutninger/ADR-007-ingen-kjoling.md)), og **prototype v1 er designet** ([ADR-010](beslutninger/ADR-010-v1-arkitektur.md)). Arkitekturen som faktisk bygges, står i:
>
> - [`hardware/v1/README.md`](../hardware/v1/README.md): mekanikken
> - [`hardware/v1/koblingsskjema.md`](../hardware/v1/koblingsskjema.md): 24 V, sikkerhetskjede og pinnekart
> - [`firmware/v1/`](../firmware/v1/README.md): ESPHome med bakeprogrammet i C++
>
> Kort fortalt:
>
> - Bare 24 V fra en CE-merket strømforsyning, og ESP32-S3 med ESPHome.
> - En brødmaskinform med eget drivverk står på én lastcelle.
> - Mel, salt og vann doseres etter vekt.
> - Varmen kommer fra en matte med vifte bak formen.
> - Dørbryter og nødstopp bryter reléer.
>
> Avsnittene under om kjøling, kaldhold, 230 V og to nivåer med vert og mikrokontroller er skrevet før dette og gjelder ikke v1. Tabellene er oppdatert med det v1 bruker.

Maskinen leverer deig som er **klar for forming**, og stekingen skjer i vanlig ovn ([ADR-006](beslutninger/ADR-006-steking-i-vanlig-ovn.md)). Arkitekturen tar utgangspunkt i konsept K2, «eltebolle i hevekammer» ([`03-konsepter.md`](03-konsepter.md)). Delsystemene er definert slik at de også passer trinnene på veien: K3 (hevekabinett) og K1 (brødmaskin i kjøleskap). Alt her er et **utkast** som skal modnes i fase 1–3.

## 1. Moduler

```mermaid
flowchart TB
  subgraph ING["Dosering (N3, over taket og i tårnet)"]
    MEL["Melbeholder<br/>skrue, røreverk og klaff"]
    VANN["Vanntank<br/>peristaltisk pumpe"]
    SALT["Saltboks<br/>skrue og klaff"]
  end
  subgraph KAM["Kammer, romtemperatur til 28 °C"]
    FORM["Brødform i holder<br/>(elteblad)"]
    TAK["Takmodul: ToF, IR,<br/>kamera og utløp"]
    VARME["Varmematte 60 W og vifte<br/>+ KSD301 og termosikring"]
  end
  subgraph VEKT["På lastcella"]
    DRIV["Lagersøyle, reim<br/>og eltemotor 120 W"]
  end
  subgraph CTRL["Styring (i tårnet)"]
    MCU["ESP32-S3 med ESPHome:<br/>tidsplan, dosering, trinn, PID"]
    PI["Pi Zero 2 W<br/>(kamera)"]
    SAFE["Dørbryter, nødstopp<br/>og reléer (maskinvare)"]
  end
  VARSEL["Varsler: «klar for forming»,<br/>«fyll mel», feil"]
  OVN["Din vanlige ovn<br/>(valgfri smartovn-integrasjon)"]
  ING --> FORM
  FORM --- DRIV
  MCU --> KAM
  MCU --> ING
  MCU --> DRIV
  MCU --> VARSEL
  PI -.-> VARSEL
  VARSEL -.-> OVN
  SAFE -. kan bryte .-> DRIV
  SAFE -. kan bryte .-> VARME
```

## 2. Sensorer og aktuatorer (kandidater)

| Funksjon | Kandidat | Merknad |
|---|---|---|
| Kammer- og deigtemperatur | v1: DS18B20 med fjær mot formbunnen (i holderen), MLX90614 mot overflaten, SHT40 i kammerluften. PT1000 + MAX31865 for bedre nøyaktighet. | Føleren i holderen står på vekta, så kabelen går gjennom veiesløyfa |
| Romklima | SHT4x | Romtemperaturen brukes i modellen (som i Panasonic-brødmaskiner). Fukt i kammeret gir varsel om kondens. |
| Heving i surdeigsglass | VL6180X (ToF, kort rekkevidde) | Dekkvindu må kalibreres for krysstale og dugg |
| Heving i formen | v1: VL53L0X i taket, glattet over 3 min. Tillegg: kamera (Pi Zero 2 W + Camera Module 3 Wide). Senere kanskje 8 × 8 ToF. | E14, [ADR-009](beslutninger/ADR-009-kamera.md) |
| Feil og aktivitet | Motorstrøm (strømsignalet fra Pololu G2), vekta og kamera | E18 |
| Vekt (dosering) | v1: én enpunkts lastcelle på 10 kg (C3) + NAU7802 under hele drivverket | Tarer før hver tilsetning. Motor, vifte og varme er av mens maskinen veier. |
| CO₂ (valgfritt, E03) | STC31 (0–100 vol%) eller SprintIR-6S-100 | SCD41 blir mettet |
| ~~Kjøling~~ | Utgår (ADR-007) | – |
| Varme | v1: silikonmatte 60 W på kjøleprofil, med vifte | Relé K2 (spole via KSD301), termosikring i kretsen, MOSFET med langsom PWM |
| Eltemotor | v1: 24 V planetgirmotor 120 W, ca. 300–400 o/min, reim 2:1 til eltebladet | Strømgrense i Pololu G2. Fastvaren stopper ved over 6 A i 2 s. |
| Dør lukket | v1: mikrobryter (KW11) i spolekretsen til motorreléet | Eltebladet stopper når døra åpnes. At formen står der, ser vekta. |
| Melskrue (N3) | v1: NEMA17 med planetgir 5:1, printet skrue på 28 mm på rustfri aksel, røreverk og servoklaff | Grovdosering til 92 %, deretter finpulser styrt av vekta. Reversering ved bro. |
| Vann (N3) | v1: Kamoer KPHM400, 24 V | Doserer etter vekt, ikke volum. Går baklengs etter dosering. |
| Salt (N3) | v1: skrue på 10 mm med NEMA17 pannekake, fra en tett boks over taket | Doseres etter vekt. Vannet doseres rett etter, og saltlaken blir til i formen (E12). |

## 3. Effektbudsjett

Uten ovn blir effekten lav, og maskinen kan stå på en hvilken som helst stikkontakt.

| Fase | Forbruker | Effekt |
|---|---|---|
| Elting og bretting | Eltemotor (v1: 24 V, 120 W) | ≤ 120 W (kort tid) |
| Levain og bulk (24–28 °C) | Varmematte (v1: 60 W) og vifte | ≤ 60 W, vanligvis mye mindre |
| Dosering | Steppere, pumpe og servoer | ca. 30 W, noen minutter |
| ~~Kald heving og kaldhold~~ | Utgår (ADR-007) | – |
| Hele tiden | Elektronikk og Pi Zero 2 W | ca. 9 W |
| **Sperre i fastvaren** | Varmen og doseringen er av mens motoren går. | **v1: ca. 130 W i normal drift, 221 W strømforsyning** |

## 4. Termikk: grove tall

- **Kjøling:** Et kammer på 15–20 L med 40 mm skumisolasjon trenger ca. 15–25 W netto kjøleeffekt for å holde 4 °C og kjøle 1 kg deig.
  - Med **Peltier** (COP ca. 0,3–0,5) gir det **40–80 W** elektrisk. Det går, men er marginalt i et varmt kjøkken. Kondens på kaldsiden må tettes godt (lukket cellegummi og en ekstra fuktsperre).
  - En **kompressor** (f.eks. Secop BD35F, COP ca. 1,9) er omtrent fire ganger mer effektiv. Det enkleste og tryggeste er å **bygge om et lite vinkjøleskap eller en kompressorkjøleboks** og styre den eksternt, slik BrewPi og Fermentrack gjør for ølgjæring. Selve kjølekretsen skal du ikke åpne, siden det krever sertifisering.
  - **Anbefaling:** Bruk kompressor (ombygd vinkjøleskap) i hevekabinettet (K3) og i K1. Peltier passer til surdeigsmodulen (N4), der lasten er liten (jf. Brød & Taylor Sourdough Home, maks ca. 38 W). Kjølingen i K2 avgjøres i fase 3 (E13).
- **Motorvarme:** 10 min elting med 100–200 W gir 60–120 kJ, og en del av det havner i deigen og kammeret. Det tas med i reguleringen og i ønsket deigtemperatur (friksjonsfaktoren).
- **Fra kald til varm:** Retarder-proofere i bakerier varmer langsomt opp fra kald tilstand for å unngå kondens på deigen. Det samme gjelder her hvis det kommer en varm etterheving etter kald heving.
- **Kondens og hygiene:** Kammeret er kaldt og fuktig i mange timer. Bruk tett innerkledning som kan rengjøres, drenering eller oppsamling av vann, og tørking eller ventilasjon mellom kjøringene. Elektronikken skal være utenfor kammeret.
- **Isolasjon:** Bruk lukket celleskum (PIR/XPS) eller den eksisterende isolasjonen i vinkjøleskapet.
- **Plast:** Det er ingen høytemperatursoner. PETG/ASA til deler i kammeret som ikke er i kontakt med mat (fukt og kulde). Ingen 3D-print i kontakt med mat.

## 5. Styring: plattformvalg

| Alternativ | Fordeler | Ulemper | Egnet for |
|---|---|---|---|
| **ESP32 + ESPHome** | YAML-oppsett som kan versjoneres. PID-regulering med *både* varme- og kjøleutgang i samme sløyfe, med autotuning. Ferdige komponenter for MAX318xx, HX711 og NAU7802. Wi-Fi og Home Assistant. | Lange oppskrifter med mange tilstander passer dårlig i YAML-skript | **Hevekabinettet (K3) i fase 1**, skjelettet (K1) og surdeigsmodulen |
| **Klipper** (Raspberry Pi + 3D-skriverkort) | Moden varmesikkerhet, steppere (`manual_stepper`), støtte for lastceller (fra v0.13, 2025), makroer og API via Moonraker | Laget for 3D-skrivere. Oppskriftslogikk som går over mange timer, bør ligge i et eget program på verten. | Kandidat for mikrokontrollerlaget i K2 når dosering med steppere kommer inn (N3) |
| **Raspberry Pi + egen fastvare på MCU** | Full kontroll | Mest arbeid. Sikkerheten må bygges selv. | Hvis de andre begrenser for mye |
| **MadMachine SwiftIO Micro** (Swift) | Swift på mikrokontroller, kraftig MCU (Cortex-M7 600 MHz), Feather-format | Ingen Wi-Fi. SDK-et er alfa/beta. Mangler drivere for MAX31855/31865, HX711 og NAU7802. Tilgjengeligheten er usikker. | Hobbyspor eller tilleggsmodul. **Aldri eneste sikkerhetslag.** |

**Forslag:**

1. **Fase 1–2:** ESP32 med ESPHome (se [ADR-002](beslutninger/ADR-002-plattform-maaleoppsett.md)). Med lav effekt og uten ovn kan det godt holde helt til N2.
2. **Fase 3–4 (K2, N3):** to nivåer.
   - En **vert** (Raspberry Pi eller Home Assistant) kjører oppskriftsmotor, tidsplanlegger, brukergrensesnitt, logging og eventuelt kamera.
   - En **mikrokontroller** tar sanntidsoppgavene: PID, motorer og dosering.
   - I tillegg kommer en **separat sikkerhetsvakt** (lag 2 i [`06-sikkerhet.md`](06-sikkerhet.md)).
3. Valget tas i ADR-004 ved port G2.

Utviklingsverktøyene (CAD, KiCad, ESPHome-CI, simulatorer) og sperrene for AI-agenter er beskrevet i [`10-verktoykjede.md`](10-verktoykjede.md).

## 6. Programvarearkitektur

```mermaid
flowchart TB
  UI["Brukergrensesnitt<br/>knapp/display · web · varsel · (Home Assistant)"]
  PLAN["Tidsplanlegger<br/>«klar for forming kl. 20:00» → starttid og temperatur,<br/>tillatte tidsrom for varsler"]
  MOTOR["Oppskriftsmotor<br/>tilstandsmaskin, leser oppskrift.yaml"]
  REG["Prosessregulatorer<br/>PID varme · motorprofiler · dosering"]
  HAL["Maskinvarelag (HAL)<br/>sensorer · aktuatorer"]
  LOG["Logg<br/>alle målinger + bake-ID"]
  SAFE["Sikkerhetsvakt (egen MCU)<br/>watchdog · overtemp · frakobling"]
  UI --> PLAN --> MOTOR --> REG --> HAL
  MOTOR --> LOG
  REG --> LOG
  HAL --> LOG
  SAFE -. overvåker og kan bryte .-> HAL
```

### Tilstandsmaskin (forenklet)

```mermaid
stateDiagram-v2
  [*] --> Klar
  Klar --> Levain: start / planlagt start
  Levain --> Fermentolyse: heving ≥ mål eller modell
  Fermentolyse --> Elting
  Elting --> Bulk
  Bulk --> KlarForForming: heving ≥ mål eller maks tid, varsel «klar for forming»
  KlarForForming --> Klar: kvittert av bruker (deigen er tatt ut)
  Levain --> Feil
  Elting --> Feil
  Bulk --> Feil
  Feil --> Klar: kvittert av bruker
  note right of Feil
    Trygg tilstand: varme av, motor av,
    varsel sendt (ingen kjøling, ADR-007)
  end note
```

Hver baking får en **bake-ID**. Alle målinger logges med bake-ID-en, slik at loggen kan kobles til bakeloggen og brødkortet. Oppskriftsformatet er beskrevet som et utkast i [`oppskrifter/maskinvennlig-v0.yaml`](../oppskrifter/maskinvennlig-v0.yaml).

### Varsler

| Varsel | Når | Kanal |
|---|---|---|
| «Fant X g surdeig …» (N3) | Ved start, hvis vekta ikke finner 5–200 g surdeig i formen | Skjerm og nettside |
| «Melet/saltet/vannet kommer ikke ut» (v1) | Når vekta ikke øker under dosering | Skjerm, summer og mobil |
| «Døra ble åpnet …» (v1) | Når døra åpnes mens motoren går | Skjerm og rød LED |
| «Deigen er klar for forming» | Slutten av bulkhevingen, helst innenfor tillatt tidsrom. Påminnelse etter 1 t. | Display, LED, summer og mobil (ntfy eller Home Assistant) |
| Feil eller avvik | Umiddelbart (motor, temperatur, nødstopp, strømbrudd) | Mobil og lys/lyd på maskinen |

### Valgfritt senere: integrasjon med smartovn

Mange nyere ovner kan fjernstyres (via produsentens app eller Home Assistant). Maskinen kan da *foreslå* forvarming til riktig tid. Regler (se [`06-sikkerhet.md`](06-sikkerhet.md)):

- Maskinen slår **aldri** på ovnen uten at brukeren bekrefter det, og bare via ovnens egen fjernstartfunksjon.
- Ingen fjernstart av ovnen når ingen er hjemme.
- Integrasjonen er en tilleggsfunksjon, utenfor v1.

## 7. Åpne arkitekturspørsmål

- ~~Kjøling i K2~~ Avgjort: ingen kjøling (ADR-007).
- ~~Hvordan kobles kroken og lokket?~~ v1: eltebladet i brødformen drives nedenfra. Taket er fast, og formen tas ut gjennom døra (ADR-010).
- ~~Hevekurv i kammeret?~~ Avgjort: kurven står i brukerens kjøleskap.
- Sikkerhetsvakt: I v1 gjøres lag 2 med dørbryter, nødstopp, KSD301 og reléer, uten egen MCU. Trengs en egen watchdog senere?
- Brukergrensesnitt: v1 har dreieknapp med trykk, OLED, LED, nettside og Home Assistant. Trengs en app?
- Hvordan blir maskinen lavere enn 45 cm (v1 er 53 cm)? Skrå melskrue eller mindre melbeholder i v2?
