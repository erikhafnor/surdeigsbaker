# Varme, strømforsyning og elektronikk (v1)

Sist undersøkt: 2026-10-16

*Metode: En research-agent leste kildekoden i ESPHome (utviklingsgrenen 2026-10-16), Klipper og flere kortprodusenters repoer på GitHub, og søkte etter produktdata. Det som bare er sjekket i søkemotorens sammendrag, er merket **(søk)**. **UVERIFISERT** betyr at det ikke kunne bekreftes. Regnestykker er merket **(beregnet)**.*

## Sammendrag

- **Varme:** Silikonmatte på 50–60 W, 24 V, på en aluminiumsplate i bunnen av kammeret, med en liten vifte som sirkulerer lufta. **Viften betyr mer enn flere watt.** En PTC-vifteovn på 100 W for 3D-printerkabinetter frarådes: den er overdimensjonert, har høy startstrøm og er ikke «sikker i seg selv».
- **Strømforsyning:** **Mean Well GST220A24-R7B** (24 V, 9,2 A, 221 W) med 4-pinners DIN-kontakt, og panelkontakten **Kycon KPJX-PM-4S**. Fatkontakten fra v0 klarer ikke strømmen.
- **Styring:** ESP32-S3-DevKitC-1 med ESPHome, på et eget bærekort med moduler i sokler. Klipper er teknisk sterkt, men passer dårlig for et kjøkkenapparat.
- **Motordriver:** **Pololu G2 24v13** i stedet for BTS7960. Den tåler 3,3 V-logikk, har innstillbar strømgrense og gir et brukbart strømsignal.
- **Eltemotor:** 24 V børstet girmotor på 90–120 W med ca. 300–500 o/min og reimutveksling 1,5–2:1 til eltebladet. Brødmaskiner kjører bladet med ca. 230 o/min og ca. 2,9 N·m ([US5364183A](https://patents.google.com/patent/US5364183A/en), søk).

## 1. Varme ved 24–28 °C

- **Varmebehov** (beregnet):
  - Tap gjennom 20 mm XPS: ca. 1–2 W/K, dvs. 12–24 W ved 14 °C på kjøkkenet en vinternatt.
  - Å varme 1,2 kg deig med form 6 K tar ca. 22 kJ. Det som begrenser, er overføringen til deigen.
- **Luft mot formen:**
  - Stillestående luft gir ca. 0,6 W/K, og da tar det timer å endre deigtemperaturen.
  - Med en liten vifte blir det ca. 2–3 W/K.
  - **En matte på 50–60 W er rikelig, men viften er nødvendig.**
- **Hevekasser:** Brød & Taylors sammenleggbare hevekasse varmer lufta med en aluminiumsbunn. Deigen står ikke på varmeren (søk).
- **Formen:** En brødmaskinform har kobling og hevet bunn, så varmen må uansett gå mest gjennom lufta.
- **PTC-varmere** begrenser bare temperaturen i selve elementet (70–200 °C), ikke i kammeret. De trekker høy startstrøm (opptil ca. 250 W for et element på 70 W) og må uansett ha termosikring (søk).
- **Anbefalt:**
  - En matte på 60 W, 24 V, f.eks. Keenovo 100 × 100 mm (ca. 25 €), på en aluminiumsplate med kjøleribber i bunnen av kammeret, og en stillegående vifte.
  - PID-regulering på en DS18B20 som trykkes mot formveggen med fjær.
  - Platen holdes ≤ 38 °C.

### Termisk vern

| Del | Kobling | Hvorfor |
|---|---|---|
| **KSD301**, 50–60 °C, manuell reset | I serie med **spolen** til varmereléet | Merkestrømmen for likestrøm er usikker. Da bryter den bare spolestrøm. |
| **Termosikring**, 72–77 °C | **Direkte i varmekretsen** (ca. 2–2,5 A) | Tar et sveiset relé eller en kortsluttet MOSFET |
| Fastvaren | Over begge | Platen ≤ 38 °C, og varmen av når en føler mangler |

## 2. Strømforsyning 200–240 W

| Modell | Effekt | Kontakt | Pris (søk) |
|---|---|---|---|
| **GST220A24-R7B** | 24 V, 9,2 A, 221 W, med IEC-inntak C14 (ledning kjøpes separat) | 4-pinners strøm-DIN med lås | Ca. 89 € eks. mva. (RS DE), 1 775 kr eks. mva. (RS NO) |
| GSM220A24-R7B | Samme som over, medisinsk versjon | 4-pinners DIN | Ca. 110 € |
| GST160A24-R7B | 24 V, 6,67 A, 160 W | 4-pinners DIN | Ca. 50 $ |
| GST280A24-C6P | 24 V, 11,67 A, 280 W | Molex Mini-Fit Jr. 6-pinners | Ca. 93 € |

- **Overlastvernet:** Det slår inn ved 105–135 % (ca. 126 % målt) og går i «hikke».
- **En motor som står fast, kan derfor slå ut strømforsyningen og starte ESP32 på nytt.** Strømgrensen i motordriveren hindrer det.
- **Panelkontakten** KPJX-PM-4S tåler 7,5 A per pinne og har to pinner per pol. Den koster ca. 6 £. Hullmålet er UVERIFISERT og må måles.
- **Pinnefordelingen** i R7B-pluggen er UVERIFISERT. **Mål før du kobler.**
- **Elfa Distrelec** stengte nettbutikken i mai 2026 etter at RS kjøpte den (søk). Kjøp fra RS Norge, Mouser, DigiKey eller Electrokit.

## 3. Styring

### Støtte i ESPHome

Lest i kildekoden, utviklingsgrenen 2026-10-16:

| Behov | Status |
|---|---|
| TMC2209 over UART | Ny kjernekomponent `tmc2209` lagt til 2026-10-13 (PR #20437). **Ikke i 2026.9.1**, ventet i 2026.11.0. Inntil da: step/dir med `a4988`, eller ekstern komponent. |
| Steppere med step/dir | `a4988` virker med alle step/dir-drivere, men går ett steg per `loop()` og hakker ved høy fart. Greit for doserere. Alternativ: STEP-signal fra LEDC med `output.ledc.set_frequency`, som gir jevn gange. |
| Lastcelle | `nau7802` i kjernen siden 2024.10.0. `hx711` også. |
| Strøm | `ina226`, `ina219`, `ina2xx_i2c` og flere |
| ToF | Bare `vl53l0x` i kjernen. VL53L1X finnes som ekstern komponent ([m5k10/vl53l1x_sensor](https://github.com/m5k10/vl53l1x_sensor)). |
| PID og H-bro | `pid` med autotune. Viftekomponenten `speed` med `direction_output` passer en driver med PWM og retning. |
| Testing | `host`-plattformen (fastvaren kompileres og kjøres på PC) |

### Ferdige 24 V-kort?

| Kort | Vurdering |
|---|---|
| FYSETC E4 (ESP32, 4 × TMC2209) | Få ledige pinner og ingen ferdig ESPHome-konfigurasjon |
| BTT SKR Pico (RP2040, 4 × TMC2209) | Et Klipper-kort uten WiFi |
| Relékort (LilyGO T-Relay, Waveshare, Kincony) | Ingen stepperdrivere |

**Ingen av kortene** har stepperdrivere, H-bro, vektforsterker og WiFi i en form som passer. **ESP32-S3-DevKitC-1 på et bærekort med moduler i sokler** er det mest byggbare.

### Klipper som alternativ

- **For:** sikker varmestyring, jevn stepperstyring og lastceller (HX711, HX717 og ADS1220 siden 2024).
- **Mot:**
  - Den trenger en Linux-maskin.
  - Oppskriftene blir G-kode-makroer, og brukergrensesnittet er laget for 3D-printere.
  - Den støtter ikke ESP32, og DS18B20 virker bare på Linux-maskinen.
  - Den har ingen støtte for INA2xx eller VL53.
- **Konklusjon:** Ikke for v1.

### Oppskriftsmotor som egen ESPHome-komponent

- **Vanlig mønster.** Et eksempel er [TillFleisch/ESPHome-Philips-Smart-Coffee](https://github.com/TillFleisch/ESPHome-Philips-Smart-Coffee), som kompilerer testoppsett i CI.
- **Oppdeling:** ren logikk med enhetstester, en tynn ESPHome-innpakning, og `esphome config` og kompilering på `host` i CI. Det er slik `firmware/v1/components/bakeplan` er bygget.

## 4. Eltemotor og driver

**Motor:**
- 24 V børstet girmotor, 90–120 W.
- Eksempler: 5D90 med snekkegir (90 W, ca. 95 £) eller IG90 (127 o/min, ca. 300 $) (søk).
- Girmotoren på 57 mm fra v0 (60–100 o/min) er for treg, med mindre reima gearer opp.
- En NEMA23-stepper mister for mye moment ved denne farten på 24 V.

| Driver | Ytelse | Logikk | Strømmåling / grense | Pris (søk) | Vurdering |
|---|---|---|---|---|---|
| **Pololu G2 24v13** | 6,5–40 V, 13 A | 1,8–5 V | 40 mV/A, innstillbar grense | ca. 45 $ | **Best** |
| Cytron MD13S | 6–30 V, 13 A | 3,3/5 V | Overstrømsvern | ca. 13 $ | Billigalternativ |
| BTS7960 | 43 A | Usikker ved 3,3 V | Grov | – | Bare som reserve |

Den innstillbare strømgrensen er den viktigste grunnen til å velge G2. Uten den kan en motor som står fast, slå ut strømforsyningen og starte ESP32 på nytt.

## 5. Risiko

1. **Strømforsyningen slår seg av ved motorstart eller -stopp.** Tiltak: strømgrense i G2, myk start, kondensatorer og hold-opp for logikken.
2. **`tmc2209` i ESPHome er ny.** Tiltak: step/dir som reserve.
3. **Steppere som går i `loop()`, er hakkete.** Tiltak: LEDC-puls.
4. **Varmen går sakte inn i 1,2 kg deig.** Tiltak: vifte, og mål tidskonstanten tidlig.
5. **KSD301 og termosikringen har usikre merkeverdier for likestrøm.** Tiltak: koblingen over, der KSD301 bare bryter spolestrøm.
6. **Pinnefordelingen og hullmålet** for strømkontakten er ikke bekreftet. Tiltak: mål selv.
