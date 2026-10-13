# Verktøy: 3D/mekanisk CAD for agent-arbeidsflyt

Sist verifisert: 2026-10-13

*Metode: GitHub-repo-, release- og commit-sider (WebFetch), README-er (raw.githubusercontent), PyPI-JSON for versjoner og datoer, og 15 nettsøk. Ingenting er installert eller kjørt. ⭐ er avrundet slik GitHub viser dem.*

## Sammendrag

- **Code-CAD med build123d er det klare tyngdepunktet for agenter.** De fleste nye agentverktøyene bygger på build123d/OCCT: build123d-mcp, agentcad, text-to-cad, MAC og referanseagenten i CADGenBench. Grunnen er at kode kan diffes, testes og kjøres headless, og at STEP kommer ut direkte.
- **FreeCAD 1.1.4 (28.09.2026) er siste stabile versjon.** 26.3 RC1 kom 08.10.2026, med ny kalenderbasert versjonering og endelig utgivelse planlagt i november. [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp) (2,8k ⭐, MIT) er klart største FreeCAD-MCP.
- **Plugin-et [text-to-cad](https://github.com/earthtojake/text-to-cad) for Claude Code har vokst svært raskt** (ca. 19,9k ⭐, MIT). Det har ferdige ferdigheter for CAD, DfAM, DFM (platearbeid), tegninger og innkjøpte STEP-deler. Telemetri er **på** som standard.
- **Versjonsfelle:** build123d 0.13 kom 21.09.2026 med OCP 8, men alle agentverktøyene låser seg til build123d < 0.12, og agentcad til < 0.11. Lås derfor build123d til 0.11.x.
- **OpenSCAD har fortsatt 2021.01 som siste stabile versjon.** Utviklingen skjer i nattlige snapshots med Manifold-motoren. Det egner seg til enkle printdeler, dårligere til plater og ramme.
- **Zoo/KCL er bare delvis åpent.** Appen og KCL-tolken er MIT-lisensiert, men geometrimotoren er en lukket skytjeneste som krever API-nøkkel.
- **Åpne text-to-CAD-modeller (cadrille, CAD-Recode, CAD-Coder) er forskningsprototyper.** Det er bedre å bruke en generell modell (Claude) med en lukket sløyfe: generer, render, mål og rett opp.
- **Hver dag dukker det opp nye CAD-MCP-repoer med 0–5 ⭐.** Mange av dem kjører vilkårlig Python. Hold deg til et fåtall vurderte verktøy.

## Anbefaling for Surdeigsbaker

**Hovedstakk: build123d som kildekode, med build123d-mcp for agentsløyfen og FreeCAD for det kode-CAD gjør dårlig.**

1. **[build123d](https://github.com/gumyr/build123d)** (Apache-2.0), låst til `>=0.11.1,<0.12`. Hver del er én `.py`-fil i `hardware/cad/` med parametre øverst og navngitte ledd (joints) for sammenstillingen. STEP er hovedformatet. STL/3MF lages bare for printdeler i kald sone.
2. **[build123d-mcp](https://github.com/pzfreo/build123d-mcp)** (Apache-2.0) i `.mcp.json`. Den har verktøy for kjøring, rendering (PNG/SVG), måling, printbarhet og eksport. Kjøringen er avgrenset med AST-sjekk og en tillatelsesliste for import.
3. **[OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer)** lar mennesker se på modellen, og `save_screenshot` lagrer bilder.
4. **FreeCAD 1.1.4** brukes til utbretting av plater ([SheetMetal](https://github.com/shaise/FreeCAD_SheetMetal) V0.8.24), TechDraw-tegninger, FEM med CalculiX og kontroll av STEP-filer. Agenten styrer den med headless `freecadcmd`-skript eller med neka-nat/freecad-mcp i en isolert container.
5. **CI:** Et pytest-steg regenererer STEP og PNG og sjekker mål, kollisjoner og minste godstykkelse med [trimesh](https://pypi.org/project/trimesh/) og [manifold3d](https://github.com/elalish/manifold).

**Hvorfor:** Tekstfiler fungerer med git og PR-gjennomgang. Lisensene (Apache/MIT/LGPL) er forenlige med CERN-OHL-S og GPL. Dessuten måler CADGenBench nettopp build123d-oppsett.

**Alternativ:** FreeCAD-sentrert arbeid (PartDesign, Sketcher, Assembly) via neka-nat/freecad-mcp, for bidragsytere som vil jobbe i et grafisk program. Ulempene er at `.FCStd` er binær (krever [DiffCAD](https://github.com/eblanshey/DiffCAD) eller [GitCAD](https://github.com/MikeOpsGit/GitCAD)), og at MCP-serveren kjører vilkårlig Python. **Vurder også** text-to-cad i en sandkasse (med `uvx cadgen telemetry off`), spesielt DFM-ferdigheten for platedeler.

## Oversikt

| Verktøy | Hva | Lisens | Siste versjon (dato) | Sist aktiv | ⭐ | MCP/agent | Modenhet | Relevans |
|---|---|---|---|---|---|---|---|---|
| [FreeCAD](https://github.com/FreeCAD/FreeCAD) | Parametrisk CAD med GUI | LGPL-2.1 | 1.1.4 (2026-09-28); 26.3rc1 (2026-10-08) | 2026-10-08 | 34,2k | Python-API, `freecadcmd` | moden | Høy |
| [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp) | MCP for FreeCAD | MIT | 0.1.27 (2026-10-13) | 2026-10-13 | 2,8k | 17 verktøy, skjermbilde, `execute_code`, headless, FEM | lovende | Høy |
| [spkane robust-mcp](https://github.com/spkane/freecad-addon-robust-mcp-server) | MCP for FreeCAD | MIT | 0.6.1 (2026-01-13) | ca. 2026-10-02 | 254 | 150+ verktøy, headless, `execute_python` | lovende | Middels |
| [ghbalf/freecad-ai](https://github.com/ghbalf/freecad-ai) | AI-arbeidsbenk i FreeCAD | LGPL-2.1 | v0.13.0-alpha ⚠️ | ca. 2026-10-10 | 562 | MCP-server og -klient | eksperimentell | Lav |
| [build123d](https://github.com/gumyr/build123d) | Code-CAD i Python (OCCT) | Apache-2.0 | 0.13.0 (2026-09-21) | 2026-10-09 | 3,4k | mål for de fleste agentverktøy | moden (før 1.0) | **Høy** |
| [build123d-mcp](https://github.com/pzfreo/build123d-mcp) | MCP for build123d | Apache-2.0 | 0.3.90 (2026-09-25) | 2026-09-25 | 112 | kjøring, rendering, måling, printbarhet, STEP/DXF | lovende | **Høy** |
| [agentcad](https://github.com/jdilla1277/agentcad) | CLI og MCP | Apache-2.0 | 0.6.0 (2026-09-11) | ca. 2026-10-06 | 161 | kjøring, forhåndsvisning, `diff`, måling | lovende | Middels |
| [text-to-cad](https://github.com/earthtojake/text-to-cad) | Plugin og ferdigheter for Claude Code (cadgen) | MIT | cadgen 0.7.21 (2026-10-11) | 2026-10-13 | ca. 19,9k | CAD, DfAM, DFM, tegning, visnings-MCP | lovende | Høy (evalueres) |
| [CadQuery](https://github.com/CadQuery/cadquery) | Code-CAD (OCCT) | Apache-2.0 | 2.8.0 (2026-06-21) | 2026-10-10 | 5,9k | [cadquery-mcp](https://github.com/CadQuery/cadquery-contrib/tree/master/mcp-server) 0.1.0 (2026-01-18) | moden | Middels |
| [OpenSCAD](https://github.com/openscad/openscad) | CSG-kode, mesh | GPL-2.0 | 2021.01; nattlige snapshots ⚠️ | 2026-10-11 | 10,4k | [openscad-mcp](https://github.com/RobertCoop/openscad-mcp) 0.6.1 (2026-09-10, 151 ⭐): kollisjon, printbarhet | moden | Lav–middels |
| [Zoo Design Studio/KCL](https://github.com/KittyCAD/modeling-app) | KCL-språk og app | MIT (motor lukket) | zoo-kcl 0.3.191 (2026-10-07) | 2026-10 | 1,3k | [zoo-mcp](https://github.com/KittyCAD/mcp) 0.28.9, krever API-nøkkel | moden, delvis åpen | Lav |
| [SolidCraft](https://github.com/bherbruck/solidcraft) | Parametrisk CAD i Rust (truck) | MIT/Apache-2.0 | 0.8 ⚠️ | 2026-10-13 | 1,7k | innebygd MCP, headless, skjermbilde | eksperimentell | Lav (følg med) |
| [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer) | Modellvisning (VS Code og frittstående) | Apache-2.0 | 4.2.0 / ocp-viewer 1.2.0 (2026-10-13) | 2026-10-13 | 414 | `save_screenshot`, ingen MCP | moden | Høy |
| [CADAM](https://github.com/Adam-CAD/CADAM) | Text-to-CAD-webapp (OpenSCAD-WASM) | GPL-3.0 | ⚠️ | ca. 2026-10-07 | 5,3k | web, LLM-API | lovende | Lav |
| [MAC](https://github.com/Pan-Chera/Multi-Agent-CAD) | Multi-agent text-to-CAD (build123d) | MIT | ⚠️ | ca. 2026-09-24 | ca. 1k | dommeragent, visuell sjekk | eksperimentell | Lav |
| [cadrille](https://github.com/col14m/cadrille) / [CAD-Recode](https://github.com/filaPro/cad-recode) | Bilde/punktsky → CadQuery | Apache-2.0 / ⚠️ | 2025 | 2025 | 188 / 269 | modellvekter på HF | forskning | Lav |
| [CADGenBench](https://github.com/huggingface/cadgenbench) | Benchmark (STEP) | Apache-2.0 | – | ⚠️ | 141 | referanseagent i build123d | – | Middels |
| [DiffCAD](https://github.com/eblanshey/DiffCAD) | Historikk og diff for FreeCAD | LGPL-2.1 | ⚠️ (krever FreeCAD 1.1+) | ⚠️ | 164 | – | lovende | Middels |
| trimesh / manifold3d | Meshanalyse og booleske operasjoner | MIT / Apache-2.0 | 5.1.1 (2026-10-02) / 3.5.4 (2026-09-25) | 2026-10 | – | bibliotek | moden | Middels |

## Detaljer per kategori

**GUI-parametrisk CAD.** FreeCAD 1.1 kom i mars 2026 ⚠️. Assembly-arbeidsbenken er innebygd siden 1.0, mens SheetMetal er et tillegg som installeres fra Addon Manager. Python-API-et dekker alt, og `freecadcmd` kjører uten GUI. Skjermbilder krever likevel GUI, eventuelt med xvfb. FreeCAD 1.1.4 tetter to sikkerhetshull som kan utløses av ondsinnede `.FCStd`-filer.

Blant MCP-serverne har neka-nat flest brukere og høyest aktivitet: tester, `isError`-rapportering og en egen headless-prosess som isolerer krasj. Mindre alternativer er [blwfish](https://github.com/blwfish/freecad-mcp) (59 ⭐, LGPL, med CAM og kollisjonssjekk) og [sandraschi](https://github.com/sandraschi/freecad-mcp) (32 ⭐). [bonninr](https://github.com/bonninr/freecad_mcp) (sist endret mars 2025) og [contextform](https://github.com/contextform/freecad-mcp) (august 2025) er i praksis forlatt.

**Code-CAD.** build123d er mer «pytonsk» enn CadQuery og har flest agentintegrasjoner. CadQuery er like modent, og MCP-serveren ligger i prosjektets egen organisasjon. OpenSCAD lager mesh uten ekte B-rep og gir ikke STEP. [PythonSCAD](https://github.com/pythonscad/pythonscad) (GPL-2.0+, 1.1.2) er OpenSCAD med Python. Zoo KCL krever skytjenesten deres.

Nye agentrettede verktøy finnes også: [SimpleCADAPI](https://github.com/PhySpace/SimpleCADAPI) (Apache-2.0, 144 ⭐), [nurb](https://github.com/Shpigford/nurb) (FSL, altså kildekode-tilgjengelig og *ikke* åpen kildekode) og ForgeCAD (proprietær).

**AI-native.** MUSE (juni 2026) ⚠️ viser at åpne modeller ligger langt bak de beste lukkede. [Text2CAD](https://github.com/SadilKhan/Text2CAD) har egen lisens som ikke er OSI-godkjent. Skills for Claude Code: [VibeCAD](https://github.com/rawwerks/VibeCAD) (MIT, build123d og `render-glb`). [flowful-ai/cad-skill](https://github.com/flowful-ai/cad-skill) (666 ⭐) har lisensen PolyForm Noncommercial og passer ikke prosjektets lisenser.

**Støtteverktøy.**

- *Rendering:* build123d-mcp (VTK), agentcad `--preview` (fire visninger), OpenSCAD `-o x.png` (trenger xvfb på 2021.01) og `bunx render-glb`.
- *Validering:* build123d `is_valid`, volum, masse og avgrensningsboks; kollisjon som volumet av snittet mellom to deler; openscad-mcp `check mode=interference`; DfAM-ferdigheten i text-to-cad (godstykkelse, overheng).
- *Versjonskontroll:* `.py` diffes direkte, og agentcad har `diff`. For FreeCAD brukes DiffCAD, GitCAD eller `fcinfo`.

## Slik kan en agent jobbe

Eksempel: **vippebraketten for bollen**, festet til aluminiumsprofil.

1. **Spesifikasjon:** `hardware/spec/vippebrakett.yaml` med last (bolle og deig, anslag ⚠️), akseldiameter, profilserie og spor, vippevinkel 0–110°, minste klaring til grytelokket, temperatursone (nær gryta: ingen print) og materiale (rustfritt 304 eller 6082-T6).
2. **Kode:** Claude Code skriver `hardware/cad/vippebrakett.py` i build123d. Alle mål kommer fra YAML-filen, og leddene navngis (`RevoluteJoint` for vippeaksen).
3. **Kjør:** build123d-mcp `execute` og deretter `validate`. Ved feil leser agenten `last_error` og retter.
4. **Se:** `render` gir isometrisk visning, forfra og snitt (PNG). Agenten vurderer bildet mot spesifikasjonen.
5. **Mål og sjekk:** avgrensningsboks og masse, hullavstand mot profilsporet, kollisjon ved 0°, 55° og 110° (snittvolum = 0) og minste klaring ≥ kravet.
6. **Eksporter:** STEP (hovedfil) og DXF-utbretting via FreeCAD SheetMetal (headless `freecadcmd`-skript). Eventuelt grov FEM med `run_fem_analysis` (CalculiX).
7. **Commit:** `.py`, `.yaml` og PNG-bilder legges i en PR. CI regenererer filene og kjører pytest-sjekkene. Et menneske går gjennom render-diffen.
8. **Iterer**, ved endrede krav eller funn fra eksperimentet E10.

Rammen følger samme oppskrift med profiler, plater og en sammenstilling av alle moduler. Kollisjonssjekk mot bollens bane er da det viktigste.

## Risiko og tillit

- **Kjøring av vilkårlig kode:** `execute_code` (neka-nat), `execute_python` (spkane) og «Dangerous mode» (freecad-ai) har alle FreeCADs fulle rettigheter. build123d-mcp har AST-sandkasse, men er ifølge dokumentasjonen et lokalt utviklingsverktøy. Ikke eksponer HTTP-modus. Kjør agenter i en devcontainer uten hemmeligheter.
- **Promptinjeksjon** kan komme via nedlastede STEP/FCStd-filer, README-er og «be agenten installere fra URL»-oppsett (text-to-cad, SimpleCADAPI). Bruk FreeCAD ≥ 1.1.4.
- **Små repoer:** Søket «cad mcp» oppdatert siste time ga flere repoer med 0–1 ⭐. Unngå dem.
- **Telemetri** er på som standard i text-to-cad.
- **Lisensfeller:** PolyForm-NC (cad-skill), FSL (nurb), Text2CAD-lisensen, ForgeCAD (proprietær) og Zoo-motoren (lukket sky).
- **Driftsrisiko:** Nesten alt er før 1.0 og endres ukentlig. Lås versjoner med `uv.lock`, og oppdater bevisst.
- **Benchmarktall** (build123d-mcp 0,360→0,457 og agentcad +48 % på CADGenBench) er oppgitt av utviklerne selv.

## Ikke verifisert

- OpenSCADs siste snapshot-versjon og at Manifold er standard i snapshots. openscad.org var blokkert, så dette bygger på e-postlister via søk.
- Funksjonslisten for FreeCAD 26.3 (wikien var blokkert) og datoen 24.03.2026 for 1.1.0 (fra Wikipedia via søk).
- Lisensene for modellvektene til CAD-Recode og CAD-Coder (Hugging Face var blokkert).
- Antall ⭐ fra GitHub-søkesider, som er lest av en oppsummeringsmodell og kan avvike noe. Den svært raske veksten til text-to-cad er ikke kryssjekket.
- Om FreeCAD kan ta skjermbilder helt uten skjerm (offscreen) uten xvfb.
- Ledertavlen i CADGenBench (nåværende rangering) og tilgjengeligheten til MUSE-datasettet.
