# Verktøy: simulering, produksjon og visualisering for agent-arbeidsflyt

Sist verifisert: 2026-10-13

> **Merknad (2026-10-13):** Etter at rapporten ble skrevet, er det bestemt at maskinen ikke skal steke ([ADR-006](../../beslutninger/ADR-006-steking-i-vanlig-ovn.md)). Eksempelet med forvarming av gryta er derfor ikke lenger en designoppgave. Den samme RC-metoden brukes nå på kjølekammeret.

*Metode: GitHub-repo-, release-, commit- og søkesider, README-er (raw.githubusercontent), PyPI/npm-registrene og 16 nettsøk. Ingenting er installert eller kjørt. ⚠️ = ikke verifisert direkte. CAD dekkes i [`3d-cad.md`](3d-cad.md).*

## Sammendrag

- **Claude Code trenger ikke MCP for verktøy med CLI eller Python-API** (løsere, MuJoCo, slicere, headless Blender). MCP gir mest for GUI-programmer og for maskinvare som trenger sikkerhetssperrer.
- **Termikk:** Start med et eget termisk RC-nettverk i Python (SciPy, `ht`, CoolProp); noe modent bibliotek eller MCP finnes ikke. Bruk Elmer eller FreeCAD FEM for kuldebroer, og OpenFOAM bare hvis luftstrømmen i bollekammeret må forstås.
- **CAE-MCP-er er mange, men små og ferske** (0–340 ⭐), og de fleste kjører vilkårlig kode. Mest etablert: neka-nat/freecad-mcp (2,8k ⭐, `run_fem_analysis`) og Foam-Agent (340 ⭐).
- **Mekanisme:** FreeCAD Assembly (kinematikk, klaring) og MuJoCo 3.15 (dynamikk). MuJoCo-MCP-ene har ≤ 9 ⭐.
- **3D-print:** OrcaSlicer 2.4.2 og PrusaSlicer 2.9.6 har CLI. mcp-3D-printer-server krever menneskelig bekreftelse før start og oppvarming.
- **Plate:** FreeCAD SheetMetal (V0.8.25, i dag) gir utbretting og DXF. Ingen moden, åpen MCP for plate eller CAM.
- **Visualisering:** Blender 5.2 LTS. [mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) (tidligere ahujasid/blender-mcp, 30,6k ⭐) er kraftig, men kjører vilkårlig Python. Socket-serveren har verken autentisering eller kryptering, og det er rapportert to CVE-er i 2026 ⚠️ (ikke bekreftet på repo-siden). [design-os-3d-blender](https://github.com/jangtrinh/design-os-3d-blender) finnes (94 ⭐, én vedlikeholder), men PyPI-navnet i installasjonsguiden er ikke registrert (risiko for navnekapring).
- **Byggeguide:** Ingen moden, åpen pipeline fra STEP til monteringsveiledning. Kombiner FreeCAD Assembly (stykkliste, eksplodert visning), headless Blender-render og GitBuilding.

## Anbefaling for Surdeigsbaker

| Oppgave | Bruk |
|---|---|
| Ovn/gryte, termisk modell | Python RC-nettverk i `sim/termikk/`, kalibrert mot E08. Deretter Elmer (eller FreeCAD FEM) for kuldebroer og overflatetemperatur, og CalculiX for termisk spenning i platedeler. |
| Bollekjøling | Samme RC-nettverk (bolle, deig, kappe, isolasjon, Peltier/kompressor med COP). OpenFOAM via [foamlib](https://pypi.org/project/foamlib/) bare ved luftkjøling. |
| Vippe- og lokkmekanisme | Momentberegning i Python, FreeCAD Assembly for bevegelse og klaring, MuJoCo (håndskrevet MJCF) for dynamikk, endestopp og nødstopp. |
| 3D-print | CAD → STL/3MF → trimesh-sjekk → PrusaSlicer- eller OrcaSlicer-CLI med låste profiler i repoet → mennesket starter printen. |
| Plate | FreeCAD SheetMetal → DXF → sjekk med ezdxf → laserleverandør. |
| Render og byggeguide | Blender 5.2 headless (`blender -b -P skript.py`) med versjonerte skript. mcp-for-blender bare til utforsking, med `BLENDER_MCP_SAFE_MODE=1` og `DISABLE_TELEMETRY=true`. |

## Oversikt

| Verktøy | Hva | Lisens | Siste versjon (dato) | Sist aktiv | ⭐ | MCP/agent | Modenhet | Relevans |
|---|---|---|---|---|---|---|---|---|
| FreeCAD FEM/Assembly/CAM | FEM-front, kinematikk, stykkliste, CAM | LGPL-2.1 | 1.1.4 (2026-09-28); 26.3rc1 (2026-10-08) | 2026-10 | 34,2k | Python, `freecadcmd`, neka-nat/freecad-mcp | moden | Høy |
| CalculiX | FEA-løser (mekanikk, varme) | GPL-2.0 ⚠️ | 2.23 (2025-10-18) | 2025 ⚠️ | – | via FreeCAD; mcp-calculix (0 ⭐) | moden | Høy |
| [Elmer FEM](https://github.com/ElmerCSC/elmerfem) | Multifysikk, varme, stråling, Joule-varme | GPL-2.0/LGPL-2.1 | 26.2.1 (2026-04-29) | 2026 | 1,7k | `.sif`-filer; FEP-Agent-Hub (4 ⭐) | moden | Høy |
| OpenFOAM | CFD | GPL-3.0 | v2606 (2026-06); Foundation 13 ⚠️ | 2026 | 2,3k | foamlib 1.8.1 (2026-09-03) | moden | Middels |
| [Foam-Agent](https://github.com/csml-rpi/Foam-Agent) | Multiagent for OpenFOAM | MIT | – | 2026-09-20 | 340 | MCP og Claude-skill | eksperimentell | Lav–middels |
| scikit-fem / DOLFINx / sfepy | Python-FEM | BSD-3 / LGPL-3.0 / BSD | 12.0.2 (2026-06-05) / 0.11.0.post0 (2026-06-10) / 2026.3 (2026-09-29) | 2026 | 663 / 1,2k / ⚠️ | Python | moden | Middels |
| Gmsh | Mesh-generator | GPL-2.0+ | 4.15.2 (2026-03-24) | 2026 | – | Python | moden | Høy |
| SciPy + [ht](https://pypi.org/project/ht/) + CoolProp | RC-nettverk og varmeovergang | BSD/MIT/MIT | ht 1.2.0 (2025-10-26), CoolProp 8.0.0 (2026-06-27) | 2026 | – | Python | moden | **Svært høy** |
| Små CAE-MCP-er: [AnkusDrive](https://github.com/gchen19/AnkusDrive), [cad-cae-copilot](https://github.com/armpro24-blip/cad-cae-copilot), [freecad-fem-mcp](https://github.com/ymiya55/freecad-fem-mcp), [openfoam-mcp-server](https://github.com/webworn/openfoam-mcp-server) | FreeCAD/CalculiX/Elmer/OpenFOAM for agenter | Apache-2.0 / MIT | v0.3.0, v0.1.0-alpha.4, – | 2026-01–10 | 0–121 | MCP, ofte vilkårlig kode | eksperimentell | Lav |
| MuJoCo | Fysikkmotor | Apache-2.0 | 3.15.0 (2026-10-05) | 2026-10 | 15,7k | Python; små MCP-er | moden | Middels |
| Genesis / Drake / PyBullet | Fysikk og robotikk | Apache-2.0 / BSD-3 ⚠️ / zlib | 1.4.4 (2026-10-11) / 1.57.0 (2026-09-10) / 3.2.7 (2025-01-30) | 2026 | 30,0k / 4,2k / 14,8k | Python | lovende / moden / vedlikehold | Lav |
| [OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer) | Slicer | AGPL-3.0 | 2.4.2 (2026-07-07) | 2026 | 15,9k | CLI (`--slice`, `--export-3mf`, `--info`); [orcaslicer-mcp](https://github.com/MaxEllis/orcaslicer-mcp) (70 ⭐, krever fork) | moden | Høy |
| PrusaSlicer | Slicer | AGPL-3.0 | 2.9.6 (2026-06-25); 3.0.0-alpha12 (2026-09-21) | 2026-09 | 9,4k | CLI | moden | Høy |
| Bambu Studio | Slicer med Assembly Guide | AGPL-3.0 | 2.8.2.61 (2026-08-21); 2.8.4 beta (2026-09-22) | 2026-09 | 5,1k | CLI ⚠️ | moden | Middels |
| [mcp-3D-printer-server](https://github.com/DMontgomery40/mcp-3D-printer-server) (+ Bambu-forken [bambu-printer-mcp](https://github.com/DMontgomery40/bambu-printer-mcp)) | MCP for OctoPrint, Klipper, Prusa, Bambu | GPL-2.0 | npm 1.2.12 (2026-10-13) / 1.1.26 (2026-10-10) | i dag | 251 / 198 | MCP med bekreftelse | lovende | Middels |
| [Kiln](https://github.com/codeofaxel/Kiln) | Print-MCP med printbarhetssjekk | AGPL-3.0 + kommersiell | ⚠️ | i dag | 92 | MCP | lovende | Lav–middels |
| [klipper-mcp](https://github.com/Charleslotto/klipper-mcp) | Moonraker-MCP | MIT ⚠️ | – | 2026-08 | 27 | MCP, rå G-kode | eksperimentell | Lav (risiko) |
| OctoPrint / Klipper / Moonraker | Printervert og API | AGPL-3.0 / GPL-3.0 / GPL-3.0 | 1.11.8, 2.0.0rc6 (2026-10-07) / v0.13.0 (2025-04-12) / – | 2026 | 9,1k / 12,0k / 1,5k | REST/WebSocket | moden | Høy |
| trimesh / manifold3d | Mesh-sjekk | MIT / Apache-2.0 ⚠️ | 5.1.1 (2026-10-02) / 3.5.4 (2026-09-25) | 2026-10 | ⚠️ | Python | moden | Høy |
| FreeCAD SheetMetal | Utbretting, DXF/SVG | LGPL-2.1 | V0.8.25 (2026-10-13) | i dag | 347 | Python i FreeCAD ⚠️ headless | moden | Høy |
| [Kiri:Moto](https://github.com/GridSpace/grid-apps) | Slicer, CAM og laser i nettleseren | MIT | 4.7.3 (2026-08-16) | 2026-08 | 919 | JS-API | moden | Lav |
| ezdxf | Lese, skrive og sjekke DXF | MIT ⚠️ | 1.4.4 (2026-05-14) | 2026 | ⚠️ | Python | moden | Høy |
| Blender | Render og animasjon | GPL-3.0 | 5.2 LTS (2026-07-14); bpy 5.2.2 (2026-09-15) | 2026 | 20,9k | Python, headless | moden | Høy |
| mcp-for-blender | Blender-MCP | MIT | PyPI 2.1.9 (2026-10-06) | 2026-10-06 | 30,6k | MCP, `execute_blender_code` | lovende | Middels |
| design-os-3d-blender | «Agent-OS» for Blender 5.2 | MIT | ingen release | i dag | 94 | MCP og skills | eksperimentell | Lav–middels |
| [GitBuilding](https://gitlab.com/gitbuilding/gitbuilding) | Byggeinstruksjoner fra Markdown | GPL-3.0 | 0.14.9 (2025-09-20) | 2026-09-30 | 29 (GitLab) | CLI | lovende | Høy |

## Detaljer per kategori

**Termikk og FEA/CFD.** FreeCAD 1.1 (mars 2026) fikk Elmer-løseren *Static Current*, som sammen med varmelikningen gir Joule-oppvarming (relevant for elementet). Elmer har strålingsutveksling mellom flater, viktig ved 250 °C. Foam-Agent bruker OpenFOAM v10 som standard og kjører `Allrun` uten tillatelsesliste. OpenModelica 1.27.1 (OMPython) er et alternativ for termiske nettverk.

**Mekanisme.** Vippa og lokket har få ledd og lave hastigheter, så statikk og kinematikk dekker det meste. MuJoCo trengs først for motorvalg, treghet og bremsing ved nødstopp.

**3D-print.** OrcaSlicers CLI er bekreftet i kildekoden. orcaslicer-mcp er sterk på analyse (`check_profile_physics`, `render_plate`) og sender ingenting til printeren, men krever en egen OrcaSlicer-fork. Kiln har overheng- og vridningssjekk, men også betalingsnivåer og CLA.

**Plate og CAM.** Treffene er SolidWorks/Inventor-MCP-er (lukkede verter) eller repoer med 0–1 ⭐. FreeCAD CAM og Kiri:Moto er bare aktuelle ved egen CNC.

**Visualisering og dokumentasjon.** design-os har en kunnskapsbase for bpy 5.2, en `AGENT_OK`/`AGENT_FAIL`-kontrakt og en «production gate» som etter eget utsagn ikke beviser passform, last eller temperatur. Bambu Studio 2.8 har en GUI-basert Assembly Guide. OSH Automated Documentation er forskningsprogramvare (v0.1.0, 2023). Eksploder-tillegg for Blender har 0–2 ⭐, så agenten bør skrive egne bpy-skript.

## Slik kan en agent jobbe

**A. «Estimer forvarmingstida for gryta med 1800 W og 40 mm steinull»**
1. Skriv `sim/termikk/forvarming.py` ut fra §4 i `07-arkitektur.md`. Nodene er element, gryte (4,5 kg støpejern), kammerplate, isolasjon og rom. Stråling element→gryte modelleres som εσ(T₁⁴−T₂⁴), steinull med k(T) fra datablad ⚠️, og utvendig konveksjon med `ht`.
2. Kontroll: Ideell kobling gir ca. 9 min (C ≈ 4 kJ/K, tap 90–140 W ved 250 °C), langt under de 30–60 min man ser i praksis. Flaskehalsen er koblingen element→gryte og elementets maksimale overflatetemperatur, ikke isolasjonen.
3. Parameterstudie (20–80 mm isolasjon, jern eller karbonstål, 1200–1800 W) med plott og CSV i `data/sim/`.
4. Aksesymmetrisk 2D-modell (Gmsh → ElmerSolver, headless) for kuldebroer og utvendig overflatetemperatur.
5. Kalibrer mot E08 og skriv inn i FO5-notatet. Et menneske går gjennom antakelsene.

**B. «Print og verifiser en sensorbrakett»**
1. CAD-skriptet gir STEP og 3MF (se `3d-cad.md`). Sjekk med trimesh at modellen er vanntett og har nok godstykkelse. Velg materiale etter temperaturen der braketten sitter (ASA/PC, 15–20 °C margin).
2. Slice med `prusa-slicer --export-gcode --load profil.ini` eller OrcaSlicer-CLI. Les tid og maks temperatur fra G-kode-headeren.
3. Last opp via mcp-3D-printer-server. Et menneske ved printeren bekrefter starten.
4. Mål braketten med skyvelære. Agenten justerer toleransen i CAD og lager en PR.

## Risiko og tillit

- **Vilkårlig kode:** `execute_blender_code` (socket-serveren har verken autentisering eller kryptering ifølge README; CVE-2026-10688 og CVE-2026-10661 er nevnt i søk ⚠️, men ikke bekreftet på repo-siden), neka-nat `execute_code`, AnkusDrive `run_script`, cad-cae-copilot `execute_build123d` og Foam-Agent `Allrun`. Kjør i container eller VM uten hemmeligheter, bundet til localhost.
- **Fysisk risiko:** Printer-MCP-er kan varme opp og bevege maskiner. Sett aldri `PRINT_REQUIRE_CONFIRMATION=0`. klipper-mcp (Charleslotto) binder til 0.0.0.0 og har `run_gcode`. **Gi aldri en agent skrivetilgang til Surdeigsbakerens egen Klipper eller 1800 W-elementet**, bare lesetilgang til loggene.
- **Navnekapring:** design-os sier `uvx design-os-3d-blender`, men pakken gir 404 på PyPI. Bruk `uvx --from git+https://github.com/jangtrinh/design-os-3d-blender@<commit>`. Kopirepoer med autogenererte brukernavn (f.eks. `offthehook-implication870/bambu-printer-mcp`) ligner et kjent mønster for skadevare ⚠️.
- **Telemetri:** mcp-for-blender sender anonym bruksstatistikk som standard, og asset- og 3D-generatorene sender data til tredjeparter. Slå begge av.
- **Små prosjekter** med én vedlikeholder og egenrapporterte påstander: lås til en commit og les koden før bruk. AGPL-verktøy er greie å bruke.
- **Simulering er ikke bevis:** Sikkerhetskritiske temperaturer må bekreftes med målinger.

## Ikke verifisert

- Lisensen til CalculiX, og om 2.23 fortsatt er siste. Datoene for OpenFOAM 13 og «v14».
- Lisensene til Drake, manifold3d og ezdxf (fra hukommelsen).
- Bambu Studios CLI, og eksport fra Assembly Guide uten GUI. Siste versjon av Kiln.
- CNC-MCP-ene (CNCjs-MCP, ugs-mcp), som bare er sett i søkeresultater.
- CVE-numrene for mcp-for-blender. De står ikke på repo-siden og må sjekkes i GitHubs sikkerhetsmeldinger eller i NVD.
- Bambus krav til Developer Mode i 2026, headless EEVEE uten GPU og headless SheetMetal.
- Steinullverdiene og varmekapasitetene i eksempel A, som bare er grove anslag.
