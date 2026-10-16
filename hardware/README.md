# Maskinvare

**v0 er klar til bygging: [byggeveiledning](v0/README.md).**

| Mappe | Innhold |
|---|---|
| [`spec/`](spec/v0.yaml) | Parameterfila som alle mål leses fra |
| [`cad/`](cad/README.md) | build123d-koden som lager STL, STEP, DXF, bilder og sjekkrapport |
| [`v0/`](v0/README.md) | Det genererte designet, stykkliste, koblingsskjema og byggeveiledning |

Opprinnelig planlagt struktur (før ADR-008). Elektronikken i v0 er bare 24 V, så det blir ikke noe eget 230 V-kort:

```text
hardware/
  spec/          YAML-spesifikasjoner som CAD-koden leser mål fra
  cad/           build123d-kode (.py) per del. STEP genereres i CI.
  mekanikk/      FreeCAD-filer (plate, TechDraw), STEP-eksport og tegninger
  elektronikk/   KiCad 10-prosjekter: strom-230v/ og styring-selv/, .kicad_dru med regler for isolasjonsavstand
  bom.csv        stykkliste (BOM) med leverandør og pris
  innkjop.csv    logg over innkjøp (se docs/09-budsjett-og-innkjop.md)
```

Verktøy og arbeidsflyt: [`docs/10-verktoykjede.md`](../docs/10-verktoykjede.md).

Lisens: CERN-OHL-S-2.0. Les [`docs/06-sikkerhet.md`](../docs/06-sikkerhet.md) før du kobler noe til 230 V.
