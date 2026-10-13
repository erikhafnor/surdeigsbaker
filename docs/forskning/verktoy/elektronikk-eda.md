# Verktøy: elektronikkdesign (EDA) for agent-arbeidsflyt

Sist verifisert: 2026-10-13

*Metode: GitHub-repo-, søke-, release- og commit-sider (WebFetch), README-er (raw.githubusercontent), PyPI/npm-JSON, KiCads GitLab-API og dokumentasjonskilde, Docker Hub og 17 nettsøk. Ingenting er installert eller kjørt. ⭐ er avrundet slik GitHub viser dem.*

## Sammendrag

- **KiCad 10 er stabil** (10.0.0 kom 20.03.2026, 10.0.7 kom 06.10.2026). IPC-API-et ([kicad-python](https://gitlab.com/kicad/code/kicad-python) 0.8.0) virker **bare mot et kjørende GUI og bare i PCB-editoren**. Headless `kicad-cli api-server` og skjema-plugins kommer i KiCad 11, som også **fjerner SWIG** (`pcbnew`).
- **`kicad-cli` dekker CI:** `sch erc`, `pcb drc --schematic-parity --exit-code-violations`, Gerber/drill/pos/BOM/IPC-2581/ODB++/STEP, `pcb render` og `jobset run`. Det offisielle Docker-bildet er `kicad/kicad:10.0`.
- **Viktigst for 230 V:** KiCad 10 har en `creepage`-constraint i DRC-regler, og PCB Calculator har kalkulatorer etter IEC 60664 og IPC-2221. Ingen MCP-server sjekker krypeavstand mot standard.
- **MCP-feltet er stort og ustabilt** (223 treff på «kicad mcp»). Ledende: [mixelpixx/KiCAD-MCP-Server](https://github.com/mixelpixx/KiCAD-MCP-Server) (2,7k ⭐), [Konnect](https://github.com/mixelpixx/Konnect) (961 ⭐, AGPL), [kicad-mcp-pro](https://github.com/oaslananka/kicad-mcp-pro) (126 ⭐, 387 verktøy) og [Seeed-Studio/kicad-mcp-server](https://github.com/Seeed-Studio/kicad-mcp-server). [lamaalrajih/kicad-mcp](https://github.com/lamaalrajih/kicad-mcp) (525 ⭐) har stått stille siden oktober 2025.
- **Beste review-lag for Claude Code:** [kicad-happy](https://github.com/aklofas/kicad-happy) (1,4k ⭐, MIT), med analyse, DFM, EMC, SPICE, datablad og innkjøp, men uten kontroll av krypeavstand.
- **Kode først:** atopile (4,0k ⭐, `ato mcp`), tscircuit (2,8k ⭐, offisiell agent-skill) og SKiDL (1,7k ⭐) leverer til KiCad. JITX er **ikke** åpen. zaptrace, etchwork og perfboard-studio er eksperimentelle (0–4 ⭐).
- **Ruting:** Freerouting 2.5.0 (05.10.2026) har MCP-server og CLI. Ingen åpen ML-ruter har dokumentert kvalitet. 230 V rutes for hånd.
- **Innkjøp:** DigiKey, Mouser og Nexar har ingen offisielle MCP-servere. Tredjepartsserverne krever egne API-nøkler, bortsett fra for JLCPCB/LCSC.

## Anbefaling for Surdeigsbaker

**Hovedstakk: KiCad først, med agenten som assistent og kontrollør, ikke som eneste konstruktør.**

1. **KiCad 10.0.x** som kildeformat. Del elektronikken i et **strømkort** (230 V) og et **styrekort** (SELV), og minimer kobber med nettspenning med sertifiserte AC/DC- og SSR-moduler.
2. **`kicad-cli` + [KiBot](https://github.com/INTI-CMNB/KiBot)** i GitHub Actions (`kicad/kicad:10.0`), med ERC/DRC som porter, fabrikkfiler, [iBoM](https://github.com/openscopeproject/InteractiveHtmlBom) og [KiRI](https://github.com/leoheck/kiri)-diff. Deterministisk og uavhengig av MCP-servere.
3. **Claude Code med kicad-happy** til review og innkjøp, pluss **én skrivende MCP-server**: kicad-mcp-pro med lesebeskyttet profil som standard og `build` bare på grener. Alternativet er mixelpixx/KiCAD-MCP-Server (størst brukermiljø).
4. **Egen `.kicad_dru`** med nettklassene `MAINS_L`, `MAINS_N`, `PE` og `SELV` og regler for `clearance`/`creepage`. Verdiene beregnes i PCB Calculator (IEC 60664), kontrolleres mot IEC 60335-1 og dokumenteres i en ADR.
5. **Freerouting lokalt**, bare for SELV-delen.

**Hvorfor:** KiCad er de facto-standard for åpen maskinvare, har best CI-økosystem, og nesten alle agentverktøy bygger på det. MCP-serverne endrer seg ukentlig, så sikkerhetsportene skal ikke avhenge av dem.

**Alternativ:** Skjema som kode med [atopile](https://github.com/atopile/atopile) eller [SKiDL](https://github.com/devbisme/skidl) og layout i KiCad. Det gir diffbar tekst som agenter håndterer godt, og passer for styrekortet, ikke strømkortet. Vurder Konnect og KiCad 11 på nytt i fase 3.

## Oversikt

| Verktøy | Hva | Lisens | Siste versjon (dato) | Sist aktiv | ⭐ | MCP/agent | Modenhet | Relevans |
|---|---|---|---|---|---|---|---|---|
| [KiCad](https://gitlab.com/kicad/code/kicad) | EDA-suite | GPL-3.0 | 10.0.7 (06.10.2026) | 13.10.2026 | – | IPC-API (PCB, GUI), `kicad-cli` | moden | ★★★ kjerne |
| kicad-python (kipy) | Offisiell IPC-binding | MIT | 0.8.0 (30.08.2026) | 29.09.2026 | – | Grunnlag for MCP | lovende | ★★ |
| mixelpixx/KiCAD-MCP-Server | MCP-server | MIT | v2.8.2 (25.09.2026) | 01.10.2026 | 2,7k | Ca. 244 verktøy: skjema, plassering, Freerouting, ERC/DRC, JLCPCB; IPC + SWIG | lovende | ★★★ |
| mixelpixx/Konnect | KiCad-plugin og MCP (Rust) | AGPL-3.0 + kommersiell | v0.13.0 (02.10.2026) | 12.10.2026 | 961 | 217–228 verktøy, IPC, bare KiCad 10 | lovende (beta) | ★★ |
| oaslananka/kicad-mcp-pro | MCP-server | MIT | 4.3.0 (11.10.2026) | 13.10.2026 | 126 | 387 verktøy i profiler (standard: 24 lesebeskyttede), ERC/DRC/DFM, heuristisk krypesjekk | lovende | ★★★ |
| Seeed-Studio/kicad-mcp-server | MCP-server | MIT | – | 28.09.2026 | 149 | 24 verktøy: analyse, ERC/DRC, enkel redigering | lovende | ★★ |
| blwfish/kicad-mcp | MCP-server | MIT | 0.18.1 (05.10.2026) | 12.10.2026 | 25 | 18 rutere (oppgir «71 verktøy»), FreeRouter, LCSC | eksperimentell | ★ |
| lamaalrajih/kicad-mcp | MCP-server | MIT | – | 17.10.2025 | 525 | Analyse, DRC, BOM | stagnert | ★ |
| [kicad-happy](https://github.com/aklofas/kicad-happy) | Claude Code-skills | MIT | v2.3.1 (06.10.2026) | 06.10.2026 | 1,4k | 11 skills: review, DFM, EMC, SPICE, datablad, innkjøp | lovende | ★★★ |
| atopile | Kode-først-språk (`.ato`) | MIT | 0.15.9 (12.09.2026) | ⚠️ | 4,0k | `ato mcp start`, LLM-avhengigheter | lovende | ★★ |
| [tscircuit](https://github.com/tscircuit/tscircuit) | EDA i TSX/React | MIT | 0.0.2870 (13.10.2026) | 13.10.2026 | 2,8k | [Agent-skill](https://github.com/tscircuit/skill), KiCad-eksport | lovende | ★ |
| SKiDL | Netliste fra Python | MIT | 2.3.0 (28.07.2026) | ⚠️ | 1,7k | Ingen MCP (brukes av etchwork) | moden | ★★ |
| [circuit-synth](https://github.com/circuit-synth/circuit-synth) | Python → KiCad | MIT | 0.12.1 (09.01.2026) | 08.03.2026 | 285 | Claude Code-agenter | eksperimentell | ★ |
| JITX | Kode-først | Proprietær | 4.4.3 (01.10.2026) | – | – | ⚠️ | moden (kommersiell) | – |
| [copperhead](https://github.com/copperheadhq/copperhead) | Agent for KiCad-repoer | Apache-2.0 | – | 13.10.2026 | 354 | `copperhead mcp` (5 verktøy) | eksperimentell | ★ |
| [zaptrace](https://github.com/oaslananka/zaptrace) | AI-EDA-kjerne | PolyForm NC (før: MIT) | 0.3.5 (03.09.2026) | 13.10.2026 | 0 | 96 MCP-verktøy | eksperimentell | – |
| [etchwork](https://github.com/FlologixAI/etchwork) | Prompt → KiCad-kort | MIT | v0.2 «pilot» | 12.10.2026 | 1 | MCP i Docker, SKiDL + Freerouting | eksperimentell | – |
| [perfboard-studio](https://github.com/medinstech/perfboard-studio) | Hullkort og stripboard | Apache-2.0 | 0.17.0 (12.10.2026) | 12.10.2026 | 4 | 53–54 MCP-verktøy | eksperimentell | ★ (prototyper) |
| [kicad-tools](https://github.com/rjwalters/kicad-tools) | Filverktøy og A*-ruter | MIT | v0.21.1 (09.2026) | ⚠️ | 68 | 18 MCP-verktøy | eksperimentell | ★ |
| [Freerouting](https://github.com/freerouting/freerouting) | Autoruter | GPL-3.0 | 2.5.0 (05.10.2026) | 05.10.2026 | 2,1k | MCP (npm 2.5.0), CLI, REST (beta) | moden | ★★ |
| [pcbparts-mcp](https://github.com/Averyy/pcbparts-mcp) | MCP for innkjøp | MIT | – | 13.10.2026 | 123 | 14 verktøy; JLCPCB uten nøkkel | lovende | ★★ |
| [easyeda2kicad](https://github.com/uPesy/easyeda2kicad.py) | LCSC → KiCad-bibliotek | AGPL-3.0 | 1.0.1 (06.04.2026) | ⚠️ | 1,7k | CLI | moden | ★★ |
| KiBot | CI-generator | AGPL-3.0 | 1.9.1 (28.07.2026) | ⚠️ | 753 | GitHub Action, Docker for KiCad 10 | moden | ★★★ |
| KiRI | Visuell diff | MIT | – | 22.06.2026 | 711 | Via KiBot | moden | ★★ |
| InteractiveHtmlBom | Interaktiv BOM | MIT | 2.12.0 (10.09.2026) | ⚠️ | 4,6k | – | moden | ★★ |
| [KiKit](https://github.com/yaqwsx/KiKit) | Panelering og fabrikkfiler | MIT | 1.8.1 (05.08.2026) | ⚠️ | 2,0k | – | moden | ★ |
| [KiClearance](https://github.com/upb-lea/kiclearance) | Tabell → `.kicad_dru` | ⚠️ | 0.2.1 (01.10.2025) | ⚠️ | 16 | – | eksperimentell | ★★ |

## Detaljer per kategori

**KiCad og MCP-servere.** I KiCad 9 og 10 krever IPC-API-et et åpent GUI, dekker bare PCB-editoren og kan ikke eksportere. Alle MCP-serverne skriver derfor `.kicad_sch` direkte, ofte via [kicad-sch-api](https://github.com/circuit-synth/kicad-sch-api). Det har gitt filkorrupsjon: mixelpixx rettet to slike feil i v2.7.0 og én i v2.8.2. Servere som bygger på SWIG/`pcbnew` (blwfish, Seeed og delvis mixelpixx) må skrives om før KiCad 11, mens kicad-mcp-pro og Konnect bruker IPC. kicad-mcp-pro har en god sikkerhetsmodell (plan, forhåndsvisning, utføring, tilbakerulling og VCS-sjekkpunkter). Men den har én vedlikeholder og over 1200 commits, og egen evaluering gir `insufficient_evidence`.

**Kode først.** atopile oppdaterer `.kicad_pcb` og velger komponenter parametrisk. Den krever Python 3.14 og har telemetri **på** som standard. tscircuit henter deler fra JLCPCB og eksporterer til KiCad via [circuit-json-to-kicad](https://github.com/tscircuit/circuit-json-to-kicad) (0.0.x, ustabil). Gratisversjonen av JITX krever CERN-OHL, og JITX beholder en kopi av designet. zaptrace har byttet til en ikke-kommersiell lisens. etchwork garanterer DRC-rene tolagskort, men ikke at kretsen virker. perfboard-studio kan være nyttig for hullkortprototyper i fase 1–2, men ingen har ennå bygget et kort fra loddeguiden.

**Ruting, plassering og DFM.** Freeroutings MCP-server kjører online mot det offentlige API-et (krever tilgang) eller offline. tscircuits *capacity-autorouter* og A*-ruteren i kicad-tools er eksperimentelle. DeepPCB har en KiCad-plugin, men krever API-nøkkel og skytjeneste ⚠️. Quilter er kommersiell. DFM-kontroll finnes i kicad-happy (JLCPCB/PCBWay), kicad-mcp-pro og pcbparts-mcp (41 regelfiler).

**Komponenter og innkjøp.** pcbparts-mcp har en lokal JLCPCB-database (ca. 575 000 deler på lager), SamacSys-modeller og ca. 285 åpne referansekort, og kan selvhostes. kicad-happy har skills for DigiKey, Mouser, element14 og LCSC, og et skill som trekker ut spesifikasjoner fra datablad. Den største DigiKey-MCP-en ([bengineer19](https://github.com/bengineer19/digikey_mcp), 35 ⭐) har ikke vært oppdatert siden juni 2025. For Nexar/Octopart finnes bare servere med 0 ⭐. Vi fant ingen MCP for SnapEDA eller Ultra Librarian.

**CI og review.** KiBot 1.9.1 støtter KiCad 10, ERC/DRC, iBoM, KiRI, diff og panelering. `kicad-cli` gir avslutningskode 0 ved brudd uten `--exit-code-violations`. Claude Code-pakker: kicad-happy, tscircuit/skill, circuit-synth-agentene og `/etchwork`. [daishuge/pcb-skill](https://github.com/daishuge/pcb-skill) (150 ⭐) er ikke vurdert.

**230 V-sikkerhet.**
- **Regler:** `(constraint creepage (min …))` med betingelse på nettklasse, og DRC viser krypebanen. PCB Calculator (*Electrical Spacing*) har IEC 60664 og IPC-2221. KiClearance (Universitetet i Paderborn) gjør en avstandstabell om til `.kicad_dru` (KiCad 9+).
- **Verdier:** Forsterket isolasjon ved 230 V krever ofte 5–8 mm krypeavstand ⚠️. Tallene må beregnes og begrunnes av et menneske.
- **Referansedesign:**
  - [Olimex ESP32-EVB](https://github.com/OLIMEX/ESP32-EVB): OSHW-sertifisert, Apache-2.0, 286 ⭐, to releer for 10 A/250 VAC, KiCad ⚠️. Isolasjonen er ikke vurdert mot våre krav.
  - [ReflowMaster](https://github.com/UnexpectedMaker/ReflowMaster) (CERN-OHL, Eagle 9.1) og [Adafruit MAX31865](https://github.com/adafruit/Adafruit-MAX31865-PCB) (Eagle, CC BY-SA) for RTD-inngangen.
  - [Erhannis/KilnController](https://github.com/Erhannis/KilnController): ESP32, KiCad, tre elementer, 1 ⭐ ⚠️.
  - GaggiMate (ESP32-S3, SSR, MAX31855) har bare tilgjengelig kildekode og er ikke åpen.

## Slik kan en agent jobbe

👤 betyr at et menneske må godkjenne trinnet.

1. **Krav.** Claude Code lager `hardware/elektronikk-krav.md` ut fra `07-arkitektur.md`, med I/O-liste (MAX31865, NAU7802/HX711, ToF, SHT4x, steppere, SSR, relédriver, vakt-MCU), effektbudsjett og kortoppdeling. 👤
2. **Komponentvalg.** Bruk pcbparts-mcp (selvhostet) og kicad-happy (`lcsc`, `digikey`, `datasheets`). Mennesket bekrefter CE/ENEC/VDE for SSR, relé, AC/DC-modul og apparatinntak. 👤
3. **Fotavtrykk.** Bruk KiCads standardbibliotek først, så easyeda2kicad. Fotavtrykk for nettspenning kontrolleres mot databladet. 👤
4. **Skjema.** Agenten skriver SKiDL/atopile, eller bruker kicad-mcp-pro (`sch_plan_from_spec` → `sch_preview_plan` → `sch_apply_plan`) på en gren. Deretter kjøres `kicad-cli sch erc --exit-code-violations` og review med kicad-happy. 👤 for nettspenningsdelen.
5. **Regler.** Mennesket beregner avstandene (IEC 60664/60335). Agenten lager nettklasser og `.kicad_dru` med KiClearance. 👤
6. **Plassering.** Mennesket plasserer 230 V-sonen, isolasjonsbarrieren og fresesporene. Agenten plasserer SELV-delene via Konnect eller mixelpixx (IPC).
7. **Ruting.** 230 V rutes for hånd. SELV rutes med Freerouting lokalt via MCP.
8. **DRC.** Kjør `kicad-cli pcb drc --schematic-parity --refill-zones --exit-code-violations`, med `pcb_check_creepage_clearance` (kicad-mcp-pro) og DFM/EMC (kicad-happy) som ekstra kontroll. Agenten får ikke legge inn DRC-unntak på nett med nettspenning. 👤
9. **Fabrikkfiler.** KiBot eller `kicad-cli jobset run` lager Gerber, drill, pos, BOM, iBoM, STEP (til 3D-CAD) og PDF.
10. **CI og review.** GitHub Actions med `kicad/kicad:10.0` og KiBot har ERC/DRC som port og legger ved KiRI-diff. Claude Code gjør review av PR-en. Mennesket godkjenner merge etter sjekklisten i `06-sikkerhet.md`. 👤
11. **Før bestilling.** Gerber-filene sjekkes visuelt i GerbView, og en fagperson ser på strømkortet. 👤

## Risiko og tillit

- **Skrivetilgang:** MCP-serverne skriver direkte i designfilene, og flere korrupsjonsfeil er kjent. Arbeid bare på git-grener med sjekkpunkt før hver økt, bruk lesebeskyttede profiler som standard, og godkjenn aldri skriveverktøy automatisk.
- **Utviklingstempo:** kicad-mcp-pro, Konnect og flere andre endres daglig, med tydelig AI-generert kode. Lås versjoner og les endringsloggen.
- **Små repoer:** Repoer med 0–5 ⭐ og dusinvis av «kicad-mcp»-varianter skal ikke få legitimasjon. Navneforveksling er reell: npm-pakken `kicad-mcp` er ikke lamaalrajih/kicad-mcp.
- **Lisenser:** AGPL (Konnect, KiBot) er greit for verktøy. zaptrace (PolyForm NC) og JITX (proprietær) bør unngås. Lisensen for biblioteker fra EasyEDA/LCSC må avklares ⚠️.
- **API-nøkler og data:** Bruk egne nøkler med minimale rettigheter, og aldri verktøy for handlekurv eller bestilling. Åpne tjenester (pcbparts.dev, api.freerouting.app, DeepPCB) mottar designdata eller søk. atopile har telemetri på som standard.
- **KiCad 11:** Når SWIG fjernes, slutter servere som bygger på `pcbnew`, å virke.
- **Ingen verktøy validerer elsikkerhet.** Layout for nettspenning laget av AI skal alltid gjennomgås av et menneske. Datablad og nettsider som agenten henter, er upålitelige data (prompt-injeksjon).

## Ikke verifisert

- Når KiCad 11 kommer (trolig tidlig i 2027 ⚠️).
- Siste commit for atopile, SKiDL, KiBot, KiKit, iBoM, easyeda2kicad og kicad-tools (bare PyPI-datoer eller README sjekket).
- Nøyaktig antall verktøy i mixelpixx (244 ifølge v2.8.0), Konnect (217 eller 228) og blwfish (71 eller 18), og om mixelpixx bruker IPC eller SWIG som standard.
- EDA-format for Olimex ESP32-EVB, lisensen til KiClearance og om GaggiMates kort er åpent.
- Om DeepPCB-pluginen er åpen og hva den koster, og vilkårene for Freeroutings offentlige API.
- Typiske krypeavstander (5–8 mm). Må beregnes etter IEC 60335-1/60664-1.
- daishuge/pcb-skill, Keitark/pcba-design-skills og BeckhamLabsLLC/kicad-jlcpcb er ikke lest, og SnapEDA- og Ultra Librarian-integrasjon i KiCad 10 er ikke sjekket.
