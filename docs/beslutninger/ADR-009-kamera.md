# ADR-009: Kamera i maskinen – analysen gjøres utenfor maskinen («tynn kant»)

- **Status:** foreslått. Avgjøres etter E14 og E18 med kamera i v0.
- **Dato:** 2026-10-16
- **Port:** G3 (for v1). Kameraet for forsøkene i v0 kan kjøpes nå.

## Kontekst

Eieren av prosjektet vil ha et kamera i maskinen som kan følge med på hevingen og boblene og varsle om feil, og spør om det trengs en egen AI-enhet til det.

Undersøkelsen ligger i [`forskning/kamera-og-ai.md`](../forskning/kamera-og-ai.md). Hovedfunnene:

- Maskinen trenger bare ett bilde hvert 1.–10. minutt. Med den bildetakten kan bildene analyseres hvor som helst: på et ESP32-kort, en Raspberry Pi, i Home Assistant eller i skyen.
- Ingen andre ser ut til å ha målt hevingen ovenfra i en kjegleformet bolle. Geometrien gjør det likevel mulig: linjen der deigen møter bolleveggen, gir høyden direkte.
- Feil under eltingen oppdages best med motorstrømmen. Ferdige bildemodeller som ikke er trent på deig, er usikre på fine vurderinger.
- Dugg, mel og lys er de praktiske problemene. Vinduet må varmes opp (0,5–1 W).

## Alternativer

1. **Ingen kamera.** Bare ToF-sensoren og motorstrømmen. Billigst, men måler hevingen bare i ett punkt og ser ingen feil.
2. **Tynn kant (anbefalt).** Kameraet tar bilder og sender dem videre. Analysen skjer i Home Assistant, på en PC eller i skyen (AI Task, LLM Vision eller egne skript). Kameraet koster 300–800 kr.
3. **AI i maskinen.** MaixCAM2 (ca. 1 200 kr), ESP32-P4 med ESP-DL (ca. 500–700 kr, krevende fastvare) eller Raspberry Pi 5 med AI HAT+ 2 (ca. 3 800 kr). Maskinen kan da tolke bildene selv uten nett, men det koster mer og gir mer kode å vedlikeholde.

## Beslutning (forslag)

- **v0 (nå): kamera som tillegg for forsøk.**
  - **Maskinvare:** Raspberry Pi Zero 2 W med Camera Module 3 Wide (120°, autofokus fra 5 cm og HDR, ca. 700–800 kr), bak et oppvarmet glassvindu i lokket, med hvitt LED-lys.
  - **Bilder:** De lagres og sendes til Home Assistant eller en PC.
  - **Rolle:** Kameraet er et tillegg. Maskinen virker som før uten det.
  - **Billigere alternativ:** et ESP32-S3-kamerakort med en OV5640-vidvinkellinse i ESPHome.
- **v1: tynn kant.**
  - **Maskinvare:** et kamera i ESPHome. ESP32-S3 nå, ESP32-P4 når ESPHome har fått støtte for MIPI-CSI ([PR #19480](https://github.com/esphome/esphome/pull/19480)). Raspberry Pi Zero beholdes hvis den gir klart bedre bilder.
  - **Analyse:** utenfor maskinen.
  - **Grunnfunksjonene virker uten kameraet:** varme, elting, ToF-heving og varsler.
- **Ikke AI i maskinen i v1.** Det vurderes på nytt hvis maskinen må kunne tolke bilder uten nett, eller hvis vi har trent egne modeller som er små nok.

## Konsekvenser

**Dette får vi:**
- Bedre hevemåling ved å kombinere kanthøyden fra kameraet med midthøyden fra ToF-sensoren (mål: ±5 prosentpoeng, E14).
- Bilde i varselet («klar for forming» med foto).
- Video av eltingen til E17.
- Data til å oppdage feil (E18).

**Dette må på plass:**
- Hull og feste for kamerahuset i foringen i lokket.
- Vindu av glass. Ikke polykarbonat, fordi EU har forbudt BPA i matkontaktmaterialer.
- Varme på vinduet og hvitt LED-lys.
- To ekstra ledere med 5 V i lokkabelen.

**Risiko:**
- Bildemodeller i skyen kan endre seg, bli dyrere eller forsvinne (som June Oven i 2026). Derfor må alt det viktigste kunne analyseres lokalt, og maskinen skal virke uten kamera.

**Personvern:** Kameraet tar bare bilder når lokket er lukket, og ser bare inn i bollen.
