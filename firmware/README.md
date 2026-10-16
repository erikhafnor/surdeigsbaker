# Fastvare og programvare

**[`v0/`](v0/README.md): ESPHome-fastvaren for maskinen i [`hardware/v0/`](../hardware/v0/README.md).** Validert med `esphome config`, ikke testet på maskinvare ennå.

Opprinnelig planlagt struktur (før ADR-008):

```text
firmware/
  lab/         ESPHome-oppsett for måleoppsett og hevekasse (fase 1, ADR-002)
  skjelett/    styring av den hackede brødmaskinen (fase 2)
  maskin/      vert (oppskriftsmotor, tidsplan, brukergrensesnitt) og MCU-fastvare (fase 3–4, ADR-004)
  sikkerhet/   sikkerhetsvakt (lag 2)
```

Arkitektur: [`docs/07-arkitektur.md`](../docs/07-arkitektur.md). Oppskriftsformat (utkast): [`oppskrifter/maskinvennlig-v0.yaml`](../oppskrifter/maskinvennlig-v0.yaml).

**Sperrer for AI-agenter:** Flashing krever alltid at et menneske godkjenner (se [`.claude/settings.json`](../.claude/settings.json) og [`docs/10-verktoykjede.md`](../docs/10-verktoykjede.md)). Endringer i `sikkerhet/` krever også godkjenning. Ny fastvare testes først i simulator (Wokwi eller ESPHome `host`) og deretter med dummylast.

Kode og kommentarer skrives på engelsk. Lisens: GPL-3.0-or-later.
