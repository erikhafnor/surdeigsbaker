# Kamera og AI i maskinen

Sist undersøkt: 2026-10-16

*Metode: To research-agenter søkte på nettet og leste kildene. Bare GitHub-sider (repoer, kildekode, utgivelser) kunne leses i sin helhet. For andre sider (produktsider, artikler, esphome.io, home-assistant.io) er det søkemotorens sammendrag som er sjekket. Det er merket **(søk)**. **UVERIFISERT** betyr at påstanden ikke kunne bekreftes. Tall merket **(beregnet)** er egne regnestykker. Priser er omtrentlige og omregnet til NOK.*

## Sammendrag

- **Ja, det går, og det trengs ikke AI i selve maskinen.** Maskinen trenger bare ett bilde hvert 1.–10. minutt. Det kan analyseres i Home Assistant, på en PC eller i skyen. Et eget AI-kort (Raspberry Pi 5 med AI HAT+ 2, MaixCAM2 eller Jetson) kan kjøre små bildemodeller lokalt, men koster 1 100–4 300 kr ekstra og gir lite så lenge bildetakten er så lav.
- **Anbefalt kamera nå: Raspberry Pi Zero 2 W med Camera Module 3 Wide** (ca. 700–800 kr). Begge agentene kom til det samme. Det er det eneste alternativet som ble funnet med både bred nok vinkel (120° diagonalt), autofokus ned til 5 cm og HDR. Det billigere alternativet er et ESP32-S3-kamerakort med vidvinkellinse i ESPHome (ca. 300–450 kr), men med svakere bilder og eksponeringskontroll.
- **Kameraet gjør hevemålingen bedre, men erstatter ikke ToF-sensoren.** Bollen er en kjegle, så linjen der deigen møter bolleveggen sier direkte hvor høyt deigen står. Kameraet måler høyden ved kanten, og ToF-sensoren måler den i midten. Sammen kan de trolig treffe ±5 prosentpoeng (beregnet, ikke publisert).
- **Ingen andre ser ut til å ha gjort dette ovenfra i en kjegleformet bolle.** Alle kameraprosjektene for surdeig som ble funnet, ser på et glass fra siden.
- **Feil under eltingen oppdages best med motorstrømmen**, som INA226 allerede måler. Kameraet er et supplement. Ferdige bildemodeller som ikke er trent på deig, er dårlige til å vurdere tilstander som «deigen klatrer på kroken». Til det trengs egne, merkede bilder.
- **De praktiske problemene er dugg, mel og lys:**
  - **Dugg:** Kammerluften har duggpunkt 22–25 °C. Et vindu i et romtempert lokk dugger derfor, og vinduet må varmes opp med 0,5–1 W.
  - **Mel og deigsprut:** Vinduet må sitte i en kort hette og kunne tas av og vaskes.
  - **Lys:** Hvitt, diffust LED-lys med låst eksponering og hvitbalanse.

## 1. Maskinvare

### Hvor bred må linsen være?

Kameraet sitter under lokket, ca. 190 mm over bollebunnen og ca. 40–70 mm fra senter, fordi akselen til kroken står i midten. Bollekanten (⌀ 240) er bare 55–75 mm fra linsen.

- Ved vanlig deighøyde trengs det ca. 60–75° synsfelt for å se hele kanten av deigen, og opptil ca. 120° når deigen står høyt (beregnet).
- Det er nok å se en del av ringen. Bollens senter er kjent, så en sirkel kan tilpasses en bue.
- Linsen må kunne fokusere på 6–20 cm.

### Alternativer

| Alternativ | Pris (ca.) | Effekt | Linse og bilde | Programvare | Vurdering |
|---|---|---|---|---|---|
| **Pi Zero 2 W + Camera Module 3 Wide** | 700–800 kr | 1–2 W | IMX708, 12 MP, 120° diagonalt (102° × 67°), autofokus fra 5 cm, HDR (søk: [SparkFun](https://www.sparkfun.com/raspberry-pi-camera-module-3-wide-angle.html)) | `rpicam-still` eller Picamera2. Ikke ESPHome. | **Anbefalt for forsøkene i v0** |
| ESP32-S3-kamerakort (N16R8) + OV5640 med 120–160° linse | 300–450 kr | ca. 1 W | OV5640 5 MP. Vidvinkelmoduler finnes (søk). Fast fokus må stilles inn. | ESPHome `esp32_camera` | Billigst og passer med resten av maskinen. Fiskeøyelinsen må kalibreres. |
| Seeed XIAO ESP32S3 Sense | 180–215 kr | 0,7–1,1 W | OV3660. Standardlinsen er trolig ca. 66°, som er for smalt (UVERIFISERT). | ESPHome | Bare med bytte til vidvinkelmodul |
| ESP32-P4 (f.eks. Waveshare) + OV5647 160° | ca. 500 kr | UVERIFISERT | MIPI-CSI, maskinvare-H.264 for video av eltingen, ca. 4 × raskere AI enn S3 | ESPHome-støtte ennå ikke sluppet. PR [#19480](https://github.com/esphome/esphome/pull/19480) er åpen. | Aktuell for v1 når støtten er sluppet |
| Raspberry Pi AI Camera (IMX500) | ca. 900 kr | – | 78° diagonalt, fokus fra 20 cm (søk) | Modeller på brikken | For smal og fokuserer for langt unna |
| Sipeed MaixCAM2 (4 GB) | 1 100–1 300 kr | ca. 2,5 W | 8 MP. Kjører Qwen3-VL-2B lokalt ([GitHub](https://github.com/sipeed/sipeed_wiki/blob/main/docs/hardware/en/maixcam/maixcam2.md)) | Eget økosystem | Hvis AI absolutt skal kjøre i maskinen |
| Pi 5 + AI HAT+ 2 (Hailo-10H) + Camera Module 3 Wide | ca. 3 800 kr | 5–12 W | Som over | Qwen2-VL-2B og Qwen3-VL-2B lokalt på 1–2 s per bilde ([Hailo model zoo](https://github.com/hailo-ai/hailo_model_zoo_genai/blob/main/docs/MODELS.rst)) | Mest kapasitet, men dyrt. Prisen har økt fra 130 til 200 USD i 2026 (søk). |
| Jetson Orin Nano Super | ca. 4 300 kr + kamera | 7–25 W | – | Raskest | Overkill. Prisen økte til 399 USD i juli 2026 (søk). |

Raspberry Pi-prisene har økt flere ganger i 2025–2026 på grunn av minneprisene (søk).

### ESPHome og Home Assistant (versjonene ble lest på GitHub)

- **ESPHome 2026.9.1:**
  - `esp32_camera` støtter OV2640, OV3660, OV5640 med flere på ESP32-S3, i opptil 2560 × 1920.
  - Komponenten `camera_encoder` (JPEG i programvare) kom i 2025.9 (søk).
  - Det finnes ennå ingen kamerastøtte for ESP32-P4 i ESPHome.
- **Home Assistant 2026.10:**
  - **AI Task** (`ai_task.generate_data`) kan få et kamerabilde som vedlegg og returnere strukturerte felt, for eksempel `heving_prosent` eller `feil`. Både Ollama (lokalt) og Anthropic støtter vedlegg ([kildekode](https://github.com/home-assistant/core/blob/dev/homeassistant/components/ollama/ai_task.py)).
  - **LLM Vision** v1.7.2 ([GitHub](https://github.com/valentinfrlch/ha-llmvision)) analyserer bilder og video, kan returnere strukturerte svar og har tidslinje og varsler. Det fungerer med skytjenester (Anthropic, OpenAI, Gemini og flere) og lokalt (Ollama, LocalAI).

### Lokale bildemodeller (lav bildetakt er nok)

Alle tidene under er per bilde.

| Modell | Raspberry Pi 5 (CPU) | Pi 5 + Hailo-10H | Merknad |
|---|---|---|---|
| Moondream2 | 8–25 s (søk) | – | Moondream 3.1 (juli 2026) er for stor for en Pi. |
| Florence-2-base | 16–41 s ([GitHub](https://github.com/harvard-edge/cs249r_book/blob/dev/kits/contents/raspi/vlm/vlm.qmd)) | – | |
| Qwen3-VL-2B, Gemma 4 E2B | flere titalls sekunder (UVERIFISERT) | Qwen3-VL-2B: 1–2 s til første ord | Finnes i Ollama og llama.cpp |
| YOLO26n / YOLO11n segmentering | under 1 s | under 10 ms | Må trenes på egne bilder |

Alt dette holder med god margin når det kommer et bilde hvert 1.–10. minutt.

### Små modeller på ESP32 (ESP-DL v3.3)

Tallene er fra [ESP-DL](https://github.com/espressif/esp-dl) og [esp-detection](https://github.com/espressif/esp-detection):

| Modell | ESP32-S3 | ESP32-P4 |
|---|---|---|
| Liten klassifikator (MobileNetV2 224) | ca. 0,4 s | ca. 0,15 s |
| ESPDet-Pico (detektor, 224) | 126 ms | 51 ms |
| YOLO11n-seg ved 640 | 7 s | 1,9 s |

Det holder til enkle ting som «deigen er formet / ikke formet» eller «bollen er tom». ESP-DL krever imidlertid egen ESP-IDF-kode og er ikke en del av ESPHome.

## 2. Hva andre har gjort

### Hobbyprosjekter

- **Kamera mot et glass fra siden** er det vanlige. Ett bilde hvert 5. min, terskling og øverste kant av deigen:
  - [justinmklam/sourdough-starter-monitor](https://github.com/justinmklam/sourdough-starter-monitor) (2018). Han gikk senere over til en ToF-sensor i lokket fordi kameraet var tungvint ([iot-sourdough-starter-monitor](https://github.com/justinmklam/iot-sourdough-starter-monitor)).
  - [jwiemann/doughmonitor](https://github.com/jwiemann/doughmonitor) er det mest avanserte (aktivt i 2026, GPL-3.0). Det er et tillegg til Home Assistant som henter bilder fra Frigate. En bildemodell i skyen (OpenRouter) eller OpenCV finner overflaten, og tillegget regner ut heving og når toppen kommer. Problemene som oppgis, er mørke bilder, gjenskinn og lys deig. Skytjenesten koster ca. 1–5 USD per døgn.
- **Avstandssensor i lokket** er hovedsporet i de fleste prosjektene:
  - [christinepamela/sourdough-sensor](https://github.com/christinepamela/sourdough-sensor) bruker VL53L0X. Den peker på støy på kort hold som største risiko, og har sluttet å finne toppen ut fra stigningen.
  - [stocyr/SourdoughMonitor](https://github.com/stocyr/SourdoughMonitor) bruker TMF8821 med flere soner og må kalibreres for krysstale.
- **Ingen prosjekter ble funnet som måler hevingen ovenfra ut fra diameteren i en kjegleformet bolle.**

### Produkter

- Lokk for surdeigsglass (Breadwinner, Crustello, Doubot) bruker avstandssensor, ikke kamera (søk).
- Ovner med kamera (LG Signature, KitchenAid) vurderer om maten er ferdigstekt, ikke hevingen (søk).
- **June Oven mistet appen og skytjenesten 22.09.2026** (søk, [Wikipedia](https://en.wikipedia.org/wiki/June_(company))). Det viser at funksjoner som avhenger av en produsents skytjeneste, kan forsvinne.
- Industri: BIBA Bremen har en hevekasse med LiDAR eller kamera og Raspberry Pi, med styring i lukket sløyfe (søk).

### Forskning (sjekket via sammendrag)

| Arbeid | Metode | Resultat |
|---|---|---|
| Romano mfl. 2007, J Food Eng | Bildeanalyse av deigvolum over tid | Modifisert Gompertz-kurve passer best |
| Ivorra mfl. 2014, J Food Eng, doi:10.1016/j.jfoodeng.2013.12.031 | Laserlinje og kamera i hevekammeret | Høyde og tverrsnitt under hevingen |
| Pérez Alvarado mfl. 2015, J Food Process Eng, doi:10.1111/jfpe.12209 | Overflatetekstur (GLCM) | Forutsier riktig eltetid (nøyaktighet UVERIFISERT) |
| Giefer mfl. 2019, Appl Sci, doi:10.3390/app9204266 | LiDAR og dyp læring | Volumavvik ca. 10 % |
| Lee mfl. 2023, Foods, doi:10.3390/foods12224160 | Kamera i en brødmaskin, OpenCV | Tilpasser steketiden |
| Murengami mfl. 2024, J Food Eng | YOLOv8 og teksturtrekk | 83 % riktig for under-, riktig- og overgjæret |

### Kan en bildemodell oppdage feil uten trening?

- Forsøk med ferdige modeller på industrielle feil (MMAD, ICLR 2025, [arXiv](https://arxiv.org/abs/2410.09453)) og på tilstanden til gjenstander (STATUS Bench 2025) viser at de er usikre på fine vurderinger. Det hjelper å trene dem videre på egne eksempler.
- **Vurdering:** Grove ting som tom bolle, deig over kanten og tørt mel som ikke er blandet inn, går trolig fint uten trening. Om deigen klatrer på kroken, ikke danner en ball eller klistrer seg fast, krever merkede bilder eller en liten trent modell, sammen med motorstrømmen. Patenter på kjøkkenmaskiner og brødmaskiner bruker nettopp strøm og turtall til dette.

## 3. Metoder som passer maskinen

- **Høyde fra kontaktlinjen** (beregnet):
  - Kjeglen har halv åpningsvinkel 19,8°, og deigdiameteren er D = 150 + 0,72 · h mm.
  - Med 1 kg deig er D ≈ 179 mm ved start og ≈ 201 mm ved +100 %.
  - **1 mm feil i høyde gir ca. 3 prosentpoeng feil i heving.**
  - Med et kalibrert kamera gir linjen der deigen møter veggen h direkte.
- **ToF i midten og kamera ved kanten** gir sammen formen på kuppelen.
- **8 × 8 ToF med flere soner** (VL53L5CX, VL53L7CX eller VL53L8CX, ca. 300 kr) er et billigere «dybdebilde»:
  - ESPHome har ikke støtte for den i kjernen, men det finnes en eksperimentell ekstern komponent: [SG-O/VL53L_MZ_esphome](https://github.com/SG-O/VL53L_MZ_esphome).
  - Nøyaktigheten er ca. ±2 cm absolutt, men det meste er en fast forskyvning som forsvinner når man måler mot startverdien.
  - Aktuell for v1.
- **Aktivitet og bobler:** Ingen fagfellevurderte metoder ble funnet for levain sett ovenfra. Logg tekstur og forskjell mellom bilder, men regn det som eksperimentelt.

## 4. Praktiske problemer

| Problem | Hvorfor | Løsning |
|---|---|---|
| **Dugg på vinduet** | Kammerluft på 26 °C har duggpunkt 22,3 °C ved 80 % RF og 24,2 °C ved 90 % RF (beregnet). Lokket holder romtemperatur. | Hold vinduet ca. 2 K over kammertemperaturen med en varmemotstand på 0,5–1 W og termostat (beregnet). Antidugg-belegg (hydrofilt) med samsvarserklæring for matkontakt. Ikke blås luft over deigen, for da tørker den. |
| **Mel og deigsprut** | Under blandingen | Vinduet sitter i en kort hette nær kanten, unna kroken. Ta ikke bilder de første minuttene av blandingen. Avtakbart glass med silikonpakning. Varsle når bildet blir uskarpt (målt med Laplace-varians). |
| **Lys** | Kammeret er mørkt. Rustfritt stål og våt deig gir gjenskinn. | Diffust, hvitt LED-lys (4000–5000 K, høy CRI) fra siden, bare på når bildet tas. Lås eksponering og hvitbalanse. Krysspolarisering fjerner gjenskinn, men koster mye lys. |
| **Matsikkerhet** | Vinduet sitter over maten | Glass (herdet eller borosilikat) er enklest. PMMA er greit med samsvarserklæring (EU 10/2011). **Unngå polykarbonat:** EU har forbudt BPA i matkontaktmaterialer (forordning 2024/3190). Elektronikk og LED skal sitte bak vinduet. Vinduet monteres i plan, så kondens ikke drypper på deigen. |
| **Personvern og sky** | Bilder kan sendes ut av huset | Ta bare bilder når lokket er lukket (signalet finnes i fastvaren). Analyser lokalt (Home Assistant med Ollama) der det går. Send bare nedskalerte utsnitt hvis skyen brukes. |

## 5. Forslag til første kameraforsøk (E14 og E18)

1. **Kalibrer med vann:** Hell kjente mengder vann (250 ml av gangen, 0,5–3 l) i bollen, med en dråpe melk for kontrast og en hvit flottør for ToF-sensoren. Kalibrer kameraet og sammenhengen mellom kontaktlinje og volum, og sjekk samtidig kjeglemodellen og ToF-sensoren.
2. **Ta bilder:**

| Fase | Hvor ofte |
|---|---|
| Bulkheving | 1 bilde hvert 2. min (2–3 MP), og ett i full oppløsning hvert 10. min |
| Bretting | Like før hver bretting og 2 min etter |
| Elting | 1 bilde hvert 5.–10. sekund, eller video (datasett for feil, E17) |
| Hvile med bolle i maskinen | 1 bilde i timen (glemt deig, mugg) |

3. **Logg med hvert bilde:** fase, kroken parkert eller ikke, motorstrøm, temperatur og fukt, IR-temperatur, ToF-avstand og eksponering.
4. **Merk hver kjøring:** oppskrift og hydrering, heving målt i et måleglass i kammeret, når du selv mener deigen er klar for forming, resultatet (snittfoto og brødkort), og feil du ser (med en knapp i Home Assistant).
5. **Analyser i denne rekkefølgen:**
   1. Klassisk bildebehandling: rett opp fiskeøyet, masker kroken, finn kanten av deigen, tilpass en sirkel og regn om til høyde og volum.
   2. Glatting av hevekurven og toppdeteksjon.
   3. Tekstur og aktivitet.
   4. En ferdig bildemodell (lokalt eller i skyen) på feilbildene, sammenlignet med merkingen din. Tren en liten modell bare hvis den bommer for ofte.

**Realistisk mål:** ToF alene ±5–10 prosentpoeng, kamera alene ±5–10 og begge sammen ca. ±5 (beregnet, ikke publisert). Kameraets største gevinst er at det oppdager feil, og at det tåler kuppelformen på deigen bedre enn ett punkt med ToF.
