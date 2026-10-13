# Maskinvare

Mappen er tom inntil videre. Mekanikk og elektronikk kommer i fase 2–4 (se [veikartet](../docs/04-veikart.md)).

Planlagt struktur:

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
