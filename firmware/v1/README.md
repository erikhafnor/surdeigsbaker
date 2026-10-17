# Fastvare for Surdeigsbaker v1

ESPHome-fastvaren for maskinen i [`hardware/v1/`](../../hardware/v1/README.md) ([ADR-010](../../docs/beslutninger/ADR-010-v1-arkitektur.md)).

> **Status:**
> - Bakeprogrammet er testet på PC: enhetstester og simulering av hele bakedager.
> - ESP32-oppsettet er validert med `esphome config`.
> - **Ikke testet på maskinvare ennå.**
> - Flashing gjøres alltid av et menneske ([`.claude/settings.json`](../../.claude/settings.json)).

## Hva fastvaren gjør

Du legger 1–2 ss surdeig i formen, setter formen inn, velger når deigen skal være klar for forming og trykker **Start**. Resten gjør maskinen:

1. **Veier surdeigen.** Vekta trekker fra den tomme formen.
2. **Planlegger baklengs** fra tiden du valgte:
   - Den velger levainens forhold og én temperatur.
   - Den utsetter starten hvis det er god tid.
   - Er tiden umulig, sier den fra og forteller hva som er tidligst og senest.
3. **Bygger levainen.** Den doserer vann og mel etter vekt og blander.
4. **Lager deigen** når levainen er klar:
   - doserer vann og mel i tre porsjoner
   - fermentolyse i 40 min
   - doserer salt og vann
   - elter og bretter tre ganger
5. **Måler hevingen** med ToF-sensoren etter siste bretting. Den lærer hvor aktiv surdeigen er, og justerer varmen for å treffe tiden.
6. **Varsler** når deigen er klar for forming. Den husker aktiviteten til neste baking.

Underveis stopper den eltingen hvis døra åpnes, og den venter på **Fortsett**. Kommer det ikke mel, salt eller vann, varsler den også, og fortsetter når du har fylt på.

## Filene

| Fil | Innhold |
|---|---|
| [`surdeigsbaker-v1.yaml`](surdeigsbaker-v1.yaml) | Hovedfila for ESP32-S3 med WiFi, API, nettside og målene du må stille inn (`substitutions`) |
| [`pakker/logikk.yaml`](pakker/logikk.yaml) | Programmet og brukergrensesnittet: tidspunkt, knapper, status og sensorer. Felles for maskinen og simuleringen. |
| [`pakker/maskinvare.yaml`](pakker/maskinvare.yaml) | Pinner, sensorer, motorer, klaffer, varme med PID, sikkerhetslaget og skjermen |
| [`surdeigsbaker-v1-sim.yaml`](surdeigsbaker-v1-sim.yaml) + [`pakker/simulator.yaml`](pakker/simulator.yaml) | Hele fastvaren på PC-en mot en modell av maskinen |
| [`components/bakeplan/`](components/bakeplan/) | Bakeprogrammet i C++ (se under) |
| [`test/`](test/) | Tester på PC-en og [`kjor_tester.sh`](test/kjor_tester.sh) |

### Bakeprogrammet (`components/bakeplan`)

Kjernen er vanlig C++ uten ESPHome, slik at alt kan testes på en PC:

| Del | Ansvar |
|---|---|
| `planner.*` | Gjæringsmodellen, planen og regulatoren som lærer aktiviteten og velger temperatur ([gjæringsmodellen](../../docs/forskning/v1-gjaeringsmodell.md)) |
| `doser.*` | Dosering etter vekt: tarering, grovdosering, finpulser, ny tarering ved bro, varsel når beholderen er tom ([dosering](../../docs/forskning/v1-dosering.md)) |
| `sequence.*` | Arbeidstrinnene: dosering, blanding, fermentolyse, salt, elting og bretting, og pause når døra åpnes |
| `bake.*` | Binder dette sammen. Gjør ToF-avstand om til heving i %, og har meldingene. |
| `sim.*` | Modell av maskinen for tester og simulering |
| `bakeplan_component.*`, `__init__.py` | Den tynne ESPHome-innpakningen: sensorer inn, `on_*`-kall ut, handlinger og lagring av det som er lært |

Programmet styrer ikke pinnene selv. Det kaller skript i YAML (`knead_set`, `dose_set`, `flap_set`, `heat_set`, `quiet_set` og `notify`), så du kan se og endre maskinvaren i `pakker/maskinvare.yaml`.

## Testene

```bash
firmware/v1/test/kjor_tester.sh
```

| Test | Hva den viser (resultat 2026-10-16) |
|---|---|
| `planner_test` | Modellen stemmer med forskningstabellene. Tidsvinduet er riktig. Regulatoren treffer med ukjent surdeig, og læringen virker. |
| `doser_test` | 560 g mel med flyt 1,5–4,5 g/s: feil under 0,4 g. 422 g vann: 0,3 g. 11,2 g salt: 0,2 g. En bro løses med én reversering. Tom beholder og urolig vekt oppdages. |
| `bake_test` | Hele dager fra start til «klar for forming», se tabellen under |

| Bakedag (simulert) | Resultat |
|---|---|
| 20 g kald surdeig, klar om 11 t | Klar etter 10,95 t, 96 % av målhevingen, mel/vann/salt innen 1,5 g |
| 20 g kald surdeig, klar om 10 t (kl. 17 hvis du starter kl. 07) | Ikke mulig. Melding: tidligst om 10,5 t. |
| 40 g surdeig, klar om 10 t | Klar i tide |
| Surdeigen 20 % tregere eller 25 % raskere enn modellen | 0,9 t sen og 0,7 t tidlig ved første baking. Riktig aktivitet læres (0,80 og 1,21). |
| Døra åpnes i 60 s under eltingen | Motoren stopper og fortsetter etter **Fortsett**. Eltetiden blir den samme. |
| Melet går tomt under deigen | Varsel, påfylling, **Fortsett**. Riktig mengde til slutt. |

### Simulering av hele fastvaren

`surdeigsbaker-v1-sim.yaml` kompilerer hele ESPHome-fastvaren for PC-en (plattformen `host`). Programmet kjøres da mot `sim.*` omtrent 2000 ganger fortere enn virkeligheten. Én bakedag tar ca. 25 sekunder:

```bash
cd firmware/v1
esphome run surdeigsbaker-v1-sim.yaml
```

Loggen viser hvert trinn med simulert tid, meldingene og hva som er lært:

```text
[bakeplan] Levain 1:2,5:2,5 (50 g mel, 50 g vann), 26,7 °C, levain 7,1 t, deig 3,8 t til +32 %
[bakeplan] [ 0.56 h] Levainen hever
[bakeplan] [ 7.83 h] Doserer mel
[bakeplan] [ 7.96 h] Fermentolyse
[bakeplan] [ 8.70 h] Elter
[bakeplan] [10.06 h] Deigen hever
[bakeplan] [11.33 h] Deigen er klar for forming
```

## Før første opplasting

1. Kopier [`../v0/secrets.example.yaml`](../v0/secrets.example.yaml) til `firmware/v1/secrets.yaml` og fyll inn. Fila er i `.gitignore`.
2. Kjør `esphome config firmware/v1/surdeigsbaker-v1.yaml`.
3. Flash første gang over USB med 24 V frakoblet. Deretter kan du oppdatere over WiFi.

## Innstillinger i `substitutions`

Disse måles på din maskin. Rekkefølgen står i [byggeveiledningen](../../hardware/v1/README.md#8-idriftsetting).

| Navn | Slik finner du verdien |
|---|---|
| `ds18b20_*` | Adressene står i loggen ved første oppstart. Varm én føler i hånda for å se hvilken som er hvilken. |
| `scale_raw_zero`, `scale_raw_ref`, `scale_ref_g` | Les rådata fra NAU7802 i loggen: én gang uten noe på plattformen og én gang med et kjent lodd, f.eks. 1 000 g. Skriv inn begge tallene. |
| `tof_to_bottom` | Avstanden ToF-sensoren viser med tom form i holderen |
| `flap_open`, `flap_closed` | Juster til klaffene ligger tett under fallrørene og svinger helt fri |
| `flour_step_hz`, `salt_step_hz` | Farten på skruene. Gir melet bro ofte, prøv lavere fart. |
| `motor_cs_v_per_a`, `motor_max_a` | Fra databladet til G2-kortet ditt. Stopp ved ca. 6 A. |
| `blade_rpm_per_pulse_per_min` | Fra Hall-pulser per motoromdreining, girutvekslingen og reimutvekslingen (2:1) |

Deretter, med maskinen ferdig montert:

1. Trykk **Lagre tom form** med tom form i holderen.
2. Kjør PID-autotune for **Varme** med ca. 1 kg vann i formen (`climate.pid.autotune`). Skriv verdiene inn i `pakker/maskinvare.yaml`.

## Sikkerhetslag i fastvaren

Dette kommer i tillegg til vernet i maskinvaren ([koblingsskjemaet](../../hardware/v1/koblingsskjema.md#sikkerhetsprinsipp)):

- **Varmen** slås av mens maskinen veier og hvis en temperaturføler mangler. Over 38 °C på kjøleribba stopper PWM. Over 45 °C slipper K2, og du får et varsel.
- **Motoren** står når døra er åpen, mens maskinen veier, og i 10 s etter at strømmen har vært over 6 A i 2 s.
- **Nødstoppen** avbryter programmet.
- **Stepperne** slås av 2 s etter siste bevegelse.

## Kjente begrensninger

- Modellen og standardverdiene er ikke validert mot ekte bakinger. Det trengs 5–10 loggførte bakinger (E02 i [eksperimentene](../../docs/05-eksperimenter.md)).
- Levainen måles ikke, fordi laget er for tynt for ToF-sensoren. Den følger modellen, og læringen skjer i bulkhevingen.
- Kameraet ([ADR-009](../../docs/beslutninger/ADR-009-kamera.md)) er ikke en del av styringen ennå. Pi-en sender bilder for analyse utenfor maskinen.
- `tmc2209` over UART kommer i ESPHome 2026.11. Til da kjøres stepperne med STEP-pulser fra LEDC.
