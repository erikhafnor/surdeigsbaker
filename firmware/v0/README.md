# Fastvare v0 (ESPHome)

Fastvare for maskinen i [`hardware/v0/`](../../hardware/v0/). Den kjører på en ESP32-S3-DevKitC-1 og er skrevet i [ESPHome](https://esphome.io). Koblingene står i [`koblingsskjema.md`](../../hardware/v0/koblingsskjema.md).

> **Status:** utkast. Konfigurasjonen er validert med `esphome config` (ESPHome 2026.9.1), men den er **ikke kompilert eller testet på maskinvare ennå**. Regn med feil i første runde.

## Hva den gjør

| Fase | Hva skjer | Innstillinger (standard) |
|---|---|---|
| 1 Blanding | Kroken blander mel, vann og levain | 3 min, 30 % fart |
| 2 Fermentolyse | Hvile. Varmen holder deigen på bulktemperaturen. | 40 min |
| 3 Tilsett saltlake | Maskinen piper og varsler. Du heller i saltlaken og trykker **Start**. Kan slås av. | venter maks 60 min |
| 4 Elting | 90 s framover og 10 s bakover, om og om igjen | 10 min, 50 % fart |
| 5 Bulkheving | Holder temperaturen, bretter deigen med korte omrøringer og måler hevingen med ToF-sensoren | 26 °C, 4 brettinger hver 30. min, mål +25 % volum, maks 5 t |
| 6 Klar for forming | Varmen slås av. Du får varsel, og LED-en blir gul. Påminnelse etter 1 t. | – |

I tillegg finnes **Levain** (hold **Start** inne i 2 s): Maskinen holder 26 °C og varsler når levainen har hevet seg 100 %. Når du har tilsatt resten og trykker **Start**, starter hovedprogrammet.

Alle tider, farter og temperaturer kan endres på nettsiden eller i Home Assistant. De huskes etter strømbrudd.

### Knapper og lys

| | Kort trykk | Langt trykk |
|---|---|---|
| **Start** (A) | Start deig, fortsett etter pause, eller kvitter for et varsel | 2 s: start levain |
| **Pause** (B) | Pause og parker kroken, slik at du kan åpne lokket | 3 s: avbryt programmet |

| LED | Betyr |
|---|---|
| Grønn | Klar |
| Blå | Arbeider |
| Gul | Venter på deg (saltlake, forming, pause) |
| Rød | Feil, nødstopp eller strømbrudd midt i et program |

### Sikkerhet i fastvaren

Maskinvaren stopper motoren når lokket åpnes eller nødstoppen trykkes, uansett hva fastvaren gjør. Fastvaren legger på:

- **Pause når lokket åpnes:** Motoren starter ikke igjen før du har lukket lokket og trykket **Start**.
- **Varmen** slås av hvis en temperaturføler mangler, hvis platen når **maks platetemperatur** (38 °C), hvis bolleveggen når 32 °C, mens motoren går og når nødstoppen er inne.
- **Fastkjørt motor:** over 4 A i 2 s gir feil, og motoren stopper.
- **Strømbrudd:** Etter omstart midt i et program slås varmen av, og du får et varsel. Programmet fortsetter ikke av seg selv.
- Den fanger ikke opp alt. Termostaten (60 °C) og termosikringen (77 °C) på varmeplaten er de siste vernene.

## Første opplasting

Du trenger ESPHome på PC-en (`pip install esphome`) eller ESPHome Builder i Home Assistant.

1. Kopier `secrets.example.yaml` til `secrets.yaml` og fyll inn WiFi, passord og en ny `api_key`.
2. **Koble fra 24 V.** Koble ESP32-en til PC-en med USB-C (porten merket USB).
3. Kjør `esphome run surdeigsbaker-v0.yaml` og velg USB-porten.
4. Senere oppdateringer går over WiFi: `esphome run surdeigsbaker-v0.yaml --device surdeigsbaker.local`.
5. Nettsiden ligger på `http://surdeigsbaker.local` (brukernavn og passord fra `secrets.yaml`).

## Etter første oppstart

1. **DS18B20-adressene:** Se i loggen (`esphome logs surdeigsbaker-v0.yaml`). Ved oppstart lister `one_wire` adressene den finner. Varm én føler i hånden for å se hvilken som er hvilken. Fyll inn `ds18b20_bowl` og `ds18b20_plate` øverst i YAML-fila og last opp på nytt. **Varmen står av til begge følerne virker.**
2. **Gaffelsensoren:** Snu kroken for hånd (uten strøm) til flagget står i gaffelen. *Kroken er parkert* skal vise PÅ. Hvis den viser motsatt, sett `home_inverted: "true"`.
3. **Motorretning:** Trykk på *Krok (bare for test)* på nettsiden med lav fart. Kroken skal gå slik at C-en skyver deigen ned. Hvis den går feil vei, bytter du M+ og M− på BTS7960.
4. **Kalibrer ToF-sensoren:** Sett i den tomme bollen, parker kroken og trykk *Kalibrer: tom bolle*.
5. **Varmen:** Fyll bollen med 1 l vann på 20 °C, sett mål 26 °C og trykk *Autotune varme*. Det tar ca. 1–2 t. Skriv inn de nye PID-verdiene fra loggen under `control_parameters`.
6. **Varsler:** Installer ntfy-appen, abonner på emnet fra `ntfy_url` og slå på *Varsle på mobil (ntfy)*.

## Kjente begrensninger i v0

- **Ingen tidsplanlegging ennå.** Du starter programmet selv, og bulkhevingen slutter når deigen har hevet seg nok (eller etter maks tid). Planleggeren som regner baklengs fra «klar for forming kl. 20» kommer når fermenteringsmodellen fra E02 finnes.
- **Hevingen måles på ett punkt** (ToF-sensoren ser ca. 70 mm fra senter). Det er et grovt mål, og E14 skal finne ut hvor godt det fungerer.
- **VL53L0X** er valgt fordi ESPHome har den innebygd. VL53L1X er mer nøyaktig, men krever en ekstern komponent.
- Oppskriftsformatet i [`oppskrifter/maskinvennlig-v0.yaml`](../../oppskrifter/maskinvennlig-v0.yaml) leses ikke av fastvaren ennå. Verdiene er lagt inn som innstillinger.

## For AI-agenter

Agenter skal validere med `esphome config` med dummy-hemmeligheter og **aldri** kjøre `esphome run`, `upload` eller flashe. Et menneske laster opp (se [`.claude/settings.json`](../../.claude/settings.json)).
