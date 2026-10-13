# Verktøy: kretssimulering, fastvare og lab for agent-arbeidsflyt

Sist verifisert: 2026-10-13

*Metode: GitHub-repo-, release-, commit-, tag- og søkesider (WebFetch), kildekode og README-er (raw.githubusercontent), PyPI/npm-JSON, API-et til det offisielle MCP-registeret, SourceForge-RSS for ngspice og 14 nettsøk. Ingenting er installert eller kjørt. ⭐ er øyeblikksbilder avrundet slik GitHub viser dem. ⚠️ = ikke verifisert direkte. CAD, EDA og mekanisk simulering dekkes i søsterdokumentene.*

## Sammendrag

- **ESPHome har fått en innebygd MCP-server.** ESPHome Device Builder har et `/api/mcp`-endepunkt (lagt inn 20.09.2026, nyeste versjon 1.23.1 fra 10.10.2026) med verktøyene `validate_config`, `compile`, `install` (flashing) og `set_secret`. Verktøyet `install` krever ingen godkjenning fra serveren.
- **Espressif har offisielle MCP-servere.** `idf.py mcp-server` følger med ESP-IDF fra v6.0 (siste er v6.1 fra 27.08.2026) og kan sette mål, bygge, flashe og rydde. Espressif har også en egen MCP-server for dokumentasjonen.
- **Wokwi er det beste verktøyet for å teste fastvare uten maskinvare.** `wokwi-cli mcp` (v0.28.1, 05.10.2026, eksperimentell) har minst 11 verktøy for serieport, pinner, kontroller og VCD-eksport. Wokwi simulerer ESP32-S3, DS18B20, HX711, NTC og relé. Gratisnivået gir 50 CI-minutter per 30 dager.
- **For kretssimulering er ngspice 47 (11.08.2026) gjeldende versjon.** Ingen offisiell MCP-server finnes. Det beste fellesskapsalternativet er [ltspice-mcp](https://github.com/Cognitohazard/ltspice-mcp) (57 ⭐), som også støtter ngspice. For skripting er spicelib 1.6.4 (04.10.2026) best. PySpice har stått stille siden 2021.
- **Data-MCP-er er modne og har lesemodus.** Home Assistant har en offisiell MCP-server i kjernen (HA 2026.10.1). [ha-mcp](https://github.com/homeassistant-ai/ha-mcp) (5,1k ⭐) har read-only-modus, Grafana MCP har `--disable-write`, og InfluxDB 3 MCP har en `readonly`-profil.
- **Laboratorie-MCP-ene er små og ferske (0–100 ⭐).** Dette gjelder seriell, sigrok og SCPI. Det beste sikkerhetsmønsteret har [lab-instrument-mcps](https://github.com/K-Dense-AI/lab-instrument-mcps) med `--simulate`, `--read-only`, `--limit` og revisjonslogg.
- **MCP-spesifikasjonen har versjon 2026-07-28.** Registeret er fortsatt i preview (API v0.1 er frosset). Fellesskapsservere må låses til en versjon og leses før bruk.

## Anbefaling for Surdeigsbaker

1. **Fase 1 (lab).** Agenten skriver ESPHome-YAML i `firmware/lab/` og kjører `esphome config` og `esphome compile` lokalt og i CI. Alle endringer testes først i simulator: logikken på ESPHome-plattformen `host` ⚠️, og maskinvare-I/O i Wokwi med scenarier. **Flashing og alt som kan slå på 230 V gjøres av et menneske.**
2. **Datalogging.** ESPHome sender data via MQTT eller HA-API til CSV eller InfluxDB. Agenten leser bare, gjennom HA-MCP med kun sensorer eksponert, ha-mcp med `/readonly` eller Grafana MCP med `--disable-write`.
3. **Krets.** Bruk ngspice 47 med spicelib, eventuelt ltspice-mcp, til SSR-driver, NTC/PT1000-inngang og RC-snubber. Kjølefelt for SSR dimensjoneres med et lite Python-skript. Grovt regneeksempel ⚠️: 1800 W / 230 V ≈ 7,8 A, og et spenningsfall på 1,2–1,6 V gir 9–13 W tap. Med 40 °C inne i kabinettet og maks 80 °C på bunnplaten blir kravet ≤ ca. 2,9 K/W. **Sjekk alltid deratingkurven i databladet.**
4. **Fase 2–4.** Følg med på Klipper/Moonraker-MCP-er, men ikke ta dem i bruk ennå. Sikkerhetsvaktens fastvare skal aldri ligge i agentens skriveområde.
5. **SwiftIO og Embedded Swift er bare et hobbyspor.** Embedded Swift er fortsatt «experimental» (Swift 6.4.1 kom 12.10.2026), og mm-sdk har versjon 2.2.0-alpha.0.

## Oversikt

| Verktøy | Hva | Lisens | Siste versjon (dato) | Sist aktiv | ⭐ | MCP/agent | Modenhet | Relevans |
|---|---|---|---|---|---|---|---|---|
| ngspice | SPICE-motor | BSD (modifisert) ⚠️ | 47 (11.08.2026) | 29.08.2026 | – (SF) | via MCP-er under | moden | høy |
| Xyce | Parallell SPICE | GPL-3.0 | 7.10 (07.2025) | 07.2025 ⚠️ | 182 | nei | moden | lav |
| Qucs-S | GUI for ngspice/Xyce | GPL-2.0 | 26.1.1 (26.04.2026) | 04.2026 | 1,4k | nei | moden | middels |
| spicelib | Python-automatisering av SPICE | GPL-3.0 | 1.6.4 (04.10.2026) | 10.2026 | 145 | Python-API | moden | høy |
| PySpice / InSpice | Python-binding | GPL-3.0 | 1.5 (2021) / 1.7.0.7 (17.09.2026) | 2024 / 09.2026 | 871 / – | API | stagnert / lovende ⚠️ | lav |
| ltspice-mcp | MCP for LTspice og ngspice | GPL-3.0+ | 0.6.1 (08.09.2026) | 12.10.2026 | 57 | 8 verktøy, `run_code` | lovende | høy |
| spicebridge | MCP for ngspice | GPL-3.0+ | 1.3.0 (13.02.2026) | 06.04.2026 | 38 | 28 verktøy | eksperimentell | middels |
| ESPHome | YAML-fastvare | MIT + GPL-3.0 (C++) | 2026.9.1 (29.09.2026), 2026.10.0b3 | 12.10.2026 | 11,9k | CLI | moden | svært høy |
| ESPHome Device Builder | Dashboard | Apache-2.0 | 1.23.1 (10.10.2026) | 13.10.2026 | 126 | innebygd `/api/mcp` | MCP eksperimentell | svært høy |
| ESP-IDF | Espressif-SDK | Apache-2.0 | v6.1 (27.08.2026) | 15.09.2026 | 19,2k | offisiell `idf.py mcp-server` + dokumentasjons-MCP | moden | middels |
| PlatformIO Core | Byggsystem | Apache-2.0 | 6.2.0 (05.09.2026) | 09.2026 | 9,5k | CLI, ingen offisiell MCP | moden | middels |
| platformio-mcp (jl-codes) | MCP | MIT | 3.1.0 (25.09.2026) | 12.10.2026 | 52 | `flash_requires_approval` | lovende | middels |
| Arduino CLI | CLI | GPL-3.0 ⚠️ | 1.5.1 (05.06.2026) | 07.2026 | – | bare fellesskaps-MCP | moden / eksperimentell | lav |
| Zephyr | RTOS | Apache-2.0 | 4.4.2 (08.2026) | 08.2026 | 16,8k | ingen offisiell MCP | moden | lav |
| Klipper | MCU-fastvare | GPL-3.0 | v0.13.0 (11.04.2025), rullerende master | – ⚠️ | 12,0k | fellesskaps-MCP via Moonraker | moden / MCP eksperimentell | høy i fase 2–4 |
| Embedded Swift | Swift for MCU | Apache-2.0 | Swift 6.4.1 (12.10.2026) | 10.2026 | 1,0k (eksempler) | nei | eksperimentell | hobby |
| MadMachine mm-sdk | SwiftIO-SDK | MIT | 2.2.0-alpha.0 (28.01, trolig 2026 ⚠️) | 01.2026 ⚠️ | 29 | nei | eksperimentell | hobby |
| Wokwi CLI | Klient for skysimulator | MIT (simulatoren er proprietær) | 0.28.1 (05.10.2026) | 10.2026 | 67 | `wokwi-cli mcp` | lovende | svært høy |
| Renode | Emulator | MIT | 1.17.0 (07.09.2026) | 09.2026 | 3,0k | Robot Framework, ingen offisiell MCP | moden | middels ⚠️ |
| QEMU (Espressif) | Emulator for ESP32/S3/C3 | GPL-2.0 | esp-develop-9.2.2-20260417 (19.04.2026) | 04.2026 | 357 | via pytest-embedded | moden | middels |
| pytest-embedded | Testrammeverk | MIT | 2.9.3 (31.08.2026) | 08.2026 | – | tillegg for wokwi, qemu og serial | moden | høy |
| serial-mcp-server (Adancurusul) | Seriell MCP | MIT | mål 0.3.0 ⚠️ | 07.07.2026 | 94 | makroer med tørrkjøring | lovende | høy |
| sigrok + sigrok-mcp-server | Logikkanalysator | GPL-3.0 / MIT | libsigrok 0.5.2 (2019); MCP 0.2.0 (25.02.2026) | 20.11.2025 / 17.08.2026 | – / 12 | 11 verktøy | treg / eksperimentell | middels |
| PyVISA | VISA-instrumenter | MIT | 1.16.2 (27.02.2026) | 02.2026 | 968 | API | moden | middels |
| lab-instrument-mcps (labmcp-scpi) | SCPI, PSU, oscilloskop | Apache-2.0 | 0.1.3 (26.09.2026) | 09.2026 | 19 | `--simulate`, `--read-only`, `--limit` | eksperimentell | middels |
| HA MCP Server (kjerne) | Offisiell | Apache-2.0 | HA 2026.10.1 (10.10.2026) | 10.2026 | 91,5k | OAuth; standard «alle LLM-API-er» gir full kontroll | moden | høy |
| ha-mcp | Fellesskap | MIT | 8.6.0 (30.09.2026) | 13.10.2026 | 5,1k | 87 verktøy, read-only | lovende | høy |
| mcp-grafana | Offisiell | Apache-2.0 | v2.0.2 (10.10.2026) | 10.2026 | 3,6k | `--disable-write` | moden | middels |
| influxdb3_mcp_server | Offisiell | MIT / Apache-2.0 | 1.4.2 (08.10.2026) | 10.2026 | 38 | `readonly`-profil (bare InfluxDB 3) | lovende | middels |
| embeddedskills | Claude Code-ferdigheter | MIT | – | 03.09.2026 | 744 | ferdigheter for J-Link, OpenOCD, probe-rs og seriell | lovende | lav–middels |

## Detaljer per kategori

**Kretssimulering.** Agenten trenger ingen MCP for dette: ngspice i batchmodus og spicelib kan diffes og testes i CI. ltspice-mcp har jobbkø, Monte Carlo og `verify_circuit`, men `run_code` kjører vilkårlig Python og bør slås av (`[tools] run_code = false`). For en SPICE-motor gjelder at riktig modell (SSR-LED, triac, termistor) betyr mer enn verktøyet.

**Fastvare.** Device Builder-MCP-en følger med ESPHome-dashbordet. [ESPHome-MCP](https://github.com/loryanstrant/ESPHome-MCP) (30 ⭐) regner selv med å bli arkivert. Espressifs `idf.py mcp-server` er stdio-basert og lokal. Den er nyttig om vi forlater ESPHome. ESPHome 2026.7 fikk også innebygd ESP-IDF-verktøykjede ⚠️. For Klipper finnes [mcp-3D-printer-server](https://github.com/DMontgomery40/mcp-3D-printer-server) (251 ⭐) og flere små Moonraker-MCP-er. Alle er laget for 3D-skrivere.

**Simulatorer.** Wokwi kjører i skyen og laster opp fastvaren, men sletter den etterpå. Automatiseringsscenarier i YAML (`set-control`, `wait-serial`, `expect-pin`) er i alfa. MAX31865 og MAX31856 finnes ikke som ferdige deler og må lages som egne brikker ⚠️. QEMU og pytest-embedded virker helt uten nett. Renode passer best til ARM-kort (Klipper-MCU-er) ⚠️. ESP32 er ikke dokumentert.

**HIL og lab.** Seriell-MCP-ene gir agenten øyne på loggen. RTS/DTR kan resette ESP32 eller sette den i nedlastingsmodus, så de bør sperres. Rammeverkene [Jumpstarter](https://github.com/jumpstarter-dev/jumpstarter) (225 ⭐, Apache-2.0) og labgrid-mcp er aktuelle for en senere HIL-rigg. For instrumenter bør man velge servere med målrettede verktøy og grenser fremfor rå SCPI.

**Økosystem.** Det offisielle Claude-pluginregisteret har 315 plugins. Et nøkkelordsøk fant bare ett som gjelder maskinvare: `cwc-makers`, som flasher en M5Stack med esptool og ber brukeren trykke på knappen. Det er et nyttig mønster. Lister: [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) (96,3k ⭐, med kategoriene «Embedded System», «Home Automation» og «Industrial & IoT») og [awesome-mcp-hardware](https://github.com/beriberikix/awesome-mcp-hardware) (59 ⭐). Servere distribueres som npm-, PyPI- eller OCI-pakker eller som fjernservere, beskrevet i `server.json`. Registeret lagrer bare metadata under navnerom som `io.github.<bruker>/…`.

## Slik kan en agent jobbe

1. **Utvikle.** Agenten skriver `firmware/lab/hevekasse.yaml`. Den bruker `climate: pid` med varme- og kjøleutgang, maksgrenser og makstid, og hemmeligheter ligger i `!secret` med dummyverdier.
2. **Validere.** `esphome config` og `esphome compile` kjøres i Claude Code og i GitHub Actions. Linjer med grenser i YAML-en eies av en navngitt person gjennom CODEOWNERS.
3. **Simulere.** Logikken testes med `host`-plattformen og maler for sensorer ⚠️. Firmware for ESP32-S3 testes i Wokwi med DS18B20, NTC og relé. Scenariet setter temperaturen til 45 °C og forventer «varme AV» i loggen. Agenten itererer via `wokwi-cli mcp`.
4. **Krets.** spicelib eller ltspice-mcp kjører ngspice 47 på SSR-driveren og NTC-deleren, og et Python-skript sjekker kjølefeltet. Resultatene legges ved PR-en.
5. **Flashe med godkjenning.** Et menneske går gjennom PR-en og kjører `esphome run` eller `install`. Første gang byttes varmeelementet ut med en lampe eller dummylast, og lag 1 og lag 2 skal være på plass.
6. **Logge.** ESPHome sender data til HA eller MQTT, og videre til InfluxDB eller CSV med bake-ID. HA eksponerer bare sensorer til Assist, ikke varmebryteren.
7. **Analysere.** Agenten henter historikk via ha-mcp (`/readonly`) eller Grafana MCP (`--disable-write`). Den beregner oversving og hevekurve, skriver en rapport i `data/` og foreslår nye PID-parametre som en ny PR. Deretter går sløyfen tilbake til trinn 2.

## Holde seg oppdatert

Første mandag i måneden (eventuelt som en planlagt agentjobb som oppretter en issue):

- **GitHub-søk**, både nylig oppdatert (`s=updated`) og flest stjerner (`s=stars`), byttes med `&s=stars&o=desc`:
  - https://github.com/search?q=esphome+mcp&type=repositories&s=updated&o=desc
  - https://github.com/search?q=platformio+mcp&type=repositories&s=updated&o=desc
  - https://github.com/search?q=esp-idf+mcp&type=repositories&s=updated&o=desc
  - https://github.com/search?q=wokwi+mcp&type=repositories&s=updated&o=desc
  - https://github.com/search?q=ngspice+mcp&type=repositories&s=updated&o=desc
  - https://github.com/search?q=scpi+mcp&type=repositories&s=updated&o=desc
  - https://github.com/search?q=sigrok+mcp&type=repositories&s=updated&o=desc
  - https://github.com/search?q=serial+mcp+server&type=repositories&s=updated&o=desc
  - https://github.com/search?q=klipper+mcp&type=repositories&s=updated&o=desc
  - https://github.com/search?q=hardware-in-the-loop+agent+mcp&type=repositories&s=stars&o=desc
  - Bare nye repoer: https://github.com/search?q=esp32+mcp+created%3A%3E2026-09-13&type=repositories&s=stars&o=desc
- **Unngå støy.** Søk som «arduino mcp» gir treff på brikkene MCP23017 og MCP2515. Legg til «server», og unngå `OR` og parenteser, som gir støy i repo-søket.
- **MCP-registeret** (navnesøk): `curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=esphome&version=latest"`. Gjenta med platformio, scpi, sigrok, serial, home-assistant og wokwi.
- **Versjoner:** `https://pypi.org/pypi/<pakke>/json` (esphome, spicelib, ha-mcp, labmcp-scpi), `https://registry.npmjs.org/platformio-mcp` og ngspice-RSS: `https://sourceforge.net/projects/ngspice/rss?path=/ng-spice-rework`.
- **Varsler om nye utgivelser** (GitHub «Watch → Releases»): esphome/esphome, esphome/device-builder, wokwi/wokwi-cli, espressif/esp-idf og Klipper3d/klipper.
- **Lister:** commit-historikken til de to awesome-listene og [awesome-hardware-skills](https://github.com/chopinfeng/awesome-hardware-skills).
- Oppdater tabellen over og datoen for «Sist verifisert».

## Risiko og tillit

- **Forsyningskjede.** De fleste MCP-ene er laget i 2026 av én person og har under 100 ⭐. Les kildekoden, lås versjonen (`uvx pakke==x.y.z`, eksakt npm-versjon) og kjør dem i en devcontainer. Velg førstepartsservere når det er mulig: ESPHome, Espressif, HA, Grafana, InfluxData og Wokwi.
- **Hemmeligheter.** Device Builder-MCP-en har verktøyene `set_secret` og `list_secret_names`. Wokwi laster fastvaren opp til skyen. Bruk derfor dummyverdier for Wi-Fi og API-nøkler i simulering.
- **Promptinjeksjon.** Serielogg, HA-tilstander og datablad er data, ikke instrukser.
- **Fysiske sikringer (må-krav):**
  - Agenten har **ingen vei til 230 V**. Slå av «Expose all LLM APIs» i HA-MCP og eksponer bare sensorer. Varmeelement, kompressor og motor eksponeres aldri, og ha-mcp kjører i read-only-modus.
  - **Flashing** sperres i Claude Code-tillatelsene (`esphome upload/run`, `idf.py flash`, `pio run -t upload`, `esptool write_flash`, MCP-verktøyene `install` og `flash_*`). Den krever menneskelig godkjenning, for eksempel med platformio-mcp `flash_requires_approval`.
  - **Simulator først.** Ingen flashing før validering, kompilering og simulatortest har passert.
  - **Lag 1** (termosikring og termostat med manuell tilbakestilling) og **lag 2** (sikkerhetsvakten) kan aldri konfigureres av programvare. Fastvaren til vakten flashes manuelt og ligger utenfor agentens skriveområde.
  - **Instrumenter** skal ha `--read-only` som standard, `--limit` for spenning og strøm, og menneskelig godkjenning for å slå på utganger. RTS/DTR sperres.
  - Ta i bruk revisjonslogg (`--audit-log`) og tidsbegrensede økter.

## Ikke verifisert

- Hvilken utgivelse av Device Builder som først hadde `/api/mcp`, hvordan endepunktet autentiserer, og om det er tilgjengelig i HA-tillegget.
- At ESPHome-fastvare kjører i Wokwi, og hvilke komponenter `host`-plattformen støtter.
- Om Renode støtter ESP32 og RP2040.
- At Claude Code kan nå HA-MCP direkte på LAN (dokumentasjonen beskriver tilkobling fra skyen).
- Hvem som eier PyPI-pakken `mqtt-mcp`. ngspice-lisensen i detalj.
- Antall servere i registeret (kildene oppgir alt fra 2 000 til 17 000), og at MCP er flyttet til Linux Foundation.
- Termiske tall for SSR, som må sjekkes mot databladet.
- ⭐ og «sist aktiv» for noen repoer er hentet fra feltet «updated» i GitHub-søket. Datoen for Xyce (taggen er fra 07.07.2025, utgivelsen fra 21.07).
