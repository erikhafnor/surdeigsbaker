# ADR-005: Verktøykjede for design med AI-agenter

- **Status:** foreslått
- **Dato:** 2026-10-13
- **Port:** G0

## Kontekst

Prosjektet skal bruke AI-agenter (Claude Code) mye i designarbeidet, innen mekanikk, elektronikk, simulering og fastvare. Per oktober 2026 finnes det mange åpne verktøy og MCP-servere, men de fleste er ferske prosjekter med én vedlikeholder. Flere kan kjøre vilkårlig kode eller styre fysisk utstyr. Se [`10-verktoykjede.md`](../10-verktoykjede.md) og rapportene i [`forskning/verktoy/`](../forskning/verktoy/).

## Alternativer

1. **GUI-sentrert**, med FreeCAD- og KiCad-MCP-er som hovedverktøy. Det er lett å komme i gang, men filene er binære eller vanskelige å diffe, og MCP-serverne endrer seg ukentlig og har kjente feil som ødelegger filer.
2. **Tekst og CLI først, med MCP som hjelpemiddel:** build123d, KiCad med `kicad-cli`/KiBot og ESPHome-CLI, og MCP til rendering, gjennomgang og simulering. Sjekkene som avgjør om noe godkjennes, kjøres med offisielle CLI-verktøy.
3. **Kommersielle AI-verktøy** (JITX, Zoo og lignende). De er modne, men lukket eller skybaserte, og passer ikke med åpen maskinvare.

## Beslutning (forslag)

Vi velger **alternativ 2**, med disse hovedvalgene:

- **Mekanikk:** build123d (låst til 0.11.x) med build123d-mcp. FreeCAD 1.1.4 headless brukes til plate, tegninger og FEM.
- **Elektronikk:** KiCad 10, delt i et 230 V-kort og et lavspenningskort (SELV), med `kicad-cli` og KiBot i CI og kicad-happy til gjennomgang.
- **Fastvare:** ESPHome via CLI og Wokwi som simulator. Flashing godkjennes alltid av et menneske.
- **Data:** Agenten får bare lesetilgang.
- **Sperrer** i [`.claude/settings.json`](../../.claude/settings.json).

## Konsekvenser

- CI må settes opp tidlig (pytest for CAD, KiBot for KiCad, `esphome compile`).
- Bidragsytere som foretrekker GUI, kan fortsatt bruke FreeCAD og KiCad, men endringer må komme som filer som kan gjennomgås.
- Verktøylisten skal skannes på nytt hver måned. Nye MCP-servere vurderes mot kriteriene før de tas i bruk.
- Valget vurderes på nytt ved port G2, når KiCad 11 og eventuelle nye agentverktøy kan endre bildet.
