# CAD-kode for Surdeigsbaker

All mekanikk for v0 er Python-kode skrevet med [build123d](https://github.com/gumyr/build123d) ([ADR-005](../../docs/beslutninger/ADR-005-verktoykjede.md)). Alle mål leses fra [`../spec/v0.yaml`](../spec/v0.yaml). Ingen mål er skrevet inn for hånd i STL- eller DXF-filene.

## Kom i gang

```bash
python -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r hardware/cad/requirements.txt

python hardware/cad/bygg.py       # alt (ca. 1 min)
python hardware/cad/bygg.py --rask   # uten 3D-bildene (ca. 15 s)
```

Resultatet havner i [`../v0/`](../v0/): STL, STEP, DXF, bøyemal, bilder, `printliste.md` og `sjekkrapport.md`.

## Filene

| Fil | Innhold |
|---|---|
| `felles.py` | Leser spec-fila. Enkle byggeklosser (`box`, `cyl_z`, ...), kjeglemodellen av bollen, geometrien til kroken og rotasjon om hengselen |
| `deler.py` | De 26 printede delene (pluss én valgfri), modellert der de sitter i maskinen. `alle_deler()` gir også printretningen. |
| `innkjop.py` | Kjøpte deler som modeller: profiler, plater (med hull), isolasjon, bolle, varmeplate, krok, motor og elektronikk |
| `sjekk.py` | Kontroller: passer delene på printeren, klaring mellom krok og bolle, kollisjoner når lokket åpnes, hengselstopp, effekt |
| `bygg.py` | Bygger alt og skriver filene |

## Slik endrer du noe

1. Endre målet i `hardware/spec/v0.yaml` (f.eks. bollen din).
2. Kjør `python hardware/cad/bygg.py`.
3. Les `hardware/v0/sjekkrapport.md`. Alle deler skal passe (✅), kroken skal ha minst 5 mm klaring, og lokket skal kunne åpnes uten kollisjon.
4. Se på bildene i `hardware/v0/bilder/`.
5. Sjekk inn både spec-fila og de nye filene i `hardware/v0/`.

Delene er modellert i maskinens koordinater (origo midt i fotavtrykket, z = 0 under rammen, +y bakover mot hengselen). `bygg.py` snur hver del til printretningen før eksport. Derfor passer STEP-filene sammen i `montasje.step`, mens STL-filene er klare for sliceren.

## For AI-agenter

- Kjør `bygg.py` etter hver endring og sjekk at `sjekkrapport.md` fortsatt er grønn før du sjekker inn.
- Endre mål i spec-fila, ikke i koden, med mindre det er en ny del eller ny geometri.
- Hold build123d på 0.11.x til noen bevisst oppgraderer og tester (ADR-005).
- Kode og kommentarer skrives på engelsk. Delnavn og spec-nøkler er norske, fordi de vises i byggeveiledningen.
