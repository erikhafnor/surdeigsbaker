# ADR-010: Prototype v1 – brødmaskinform med vekt, dosering av mel, salt og vann, og tidsplanlegger

- **Status:** vedtatt som byggegrunnlag for v1. Erstatter [ADR-008](ADR-008-v0-design.md) (v0 bygges ikke).
- **Dato:** 2026-10-16
- **Port:** G3 (framskyndet)

## Kontekst

Eieren av prosjektet vil ikke bygge v0, men gå rett på v1: *«Bare gjør v1 god nok slik at det mest sannsynlig vil fungere godt, så får vi heller forbedre på sikt.»* v1 skal oppfylle scenariet i [`11-bruksscenarier.md`](../11-bruksscenarier.md):

- Brukeren fyller på mel, salt og vann.
- Om morgenen har brukeren 1 ss surdeig i formen og velger «klar for forming kl. 17».
- Maskinen doserer, lager saltlaken, elter, holder temperaturen, bretter, måler hevingen og treffer tiden uten kjøling ([ADR-007](ADR-007-ingen-kjoling.md)).

**Grunnlaget** er fire undersøkelser fra 2026-10-16:

- [elting](../forskning/v1-elting.md)
- [dosering](../forskning/v1-dosering.md)
- [varme og elektronikk](../forskning/v1-elektronikk.md)
- [gjæringsmodell](../forskning/v1-gjaeringsmodell.md)

Kamera kommer i tillegg ([ADR-009](ADR-009-kamera.md)).

**Hovedregelen for valgene:** Ta det som er velprøvd, selv om det blir større eller dyrere, og legg utvikling bare der det ikke finnes noe ferdig.

## Beslutninger

| Område | Valg | Hvorfor | Forkastet |
|---|---|---|---|
| **Elting** | **Brødmaskinform fra Panasonic XL (SD-2500/2501/ZB2502)** med elteblad i bunnen, drevet av vår egen 24 V girmotor via reim | Velprøvd for 1–1,3 kg deig. Reservedeler finnes, og formen tas ut. Lokket og taket blir ledige for dosering og sensorer. | C-krok fra lokket (v0, ikke prøvd), spiralelter (230 V og sperrer for dosering), planetrører |
| **Deigmengde** | 560 g mel (ca. 1,05 kg deig) som standard | Panasonic oppgir maks 600 g mel | 610 g som i referansen |
| **Uttak** | **Frontdør** på kammeret. Formen dreies løs, løftes 2 cm og trekkes ut. | Taket kan være fast, med dosering og sensorer uten bevegelige ledninger | Vippelokk (høyere og med ledninger i hengselen) |
| **Vekt** | Hele drivverket (holder, aksel, reim og motor) står på en plattform med **én enpunkts lastcelle på 10 kg** og NAU7802 | Ingenting annet bærer formen, så vekta blir riktig. Reimkraften holder seg innenfor det som veies. | Lastcelle bare under formen (motoren ville bære den) |
| **Mel** | **Én beholder med melblanding** (ca. 1,5 kg, to brød) og en **vannrett skrue på 28 mm** med røreverk, stoppet av vekta (grovt, så fint). Klaff ved utløpet. | Ingen åpne løsninger har vist at de klarer mel. En vannrett skrue med røreverk og vektstyring er det beste kjente, og v1 er laget for å teste den (E11). | Skråskrue eller loddrett skrue (lavere, men mer risiko), to beholdere (dobbelt så mye) |
| **Salt** | Liten beholder med **10 mm skrue** og egen klaff. Saltet og vannet doseres rett på deigen (saltlake i formen). | Salt renner lett, og vekta gir nøyaktigheten | Vibrasjonsrenne, ferdig saltlake på tank |
| **Vann** | **Peristaltisk 24 V-pumpe** (Kamoer KPHM400) fra en tank på 1 l foran i tårnet, styrt av vekta. Pumpen går baklengs etter dosering. | Drypper ikke og er lett å rengjøre. Tanken fylles per baking. | Membranpumpe (drypper), vann på tank i en uke (biofilm) |
| **Varme** | **Silikonmatte på 60 W** på en ribbeplate i kammergulvet, med **vifte**. PID-regulering på en føler mot bunnen av formen. Platen holdes ≤ 38 °C. | En vifte gir mer enn flere watt. Den holder deigen jevnt varm uten varme flekker. | PTC-vifteovn (for stor og ikke sikker i seg selv) |
| **Varmevern** | **KSD301** (manuell reset) i spolekretsen til varmereléet, **termosikring** 72–77 °C rett i varmekretsen, og grenser i fastvaren | Virker selv om MOSFET-en kortslutter eller reléet henger | – |
| **Strøm** | **Mean Well GST220A24-R7B** (24 V, 221 W) med 4-pinners DIN-kontakt (KPJX-PM-4S) | Fatkontakten fra v0 klarer ikke strømmen. Fortsatt ingen 230 V i maskinen. | 150 W med fatkontakt |
| **Sikkerhet** | **Dørbryter** forsyner spolen til motorreléet. **Nødstopp** forsyner begge reléene. Strømgrense i motordriveren. | Som i v0: virker uten fastvare | – |
| **Eltemotor** | **24 V børstet girmotor på 90–120 W** med Hall-teller, ca. 300–400 o/min, og HTD-reim ca. 2:1 til eltebladet (ca. 150–200 o/min) | Brødmaskiner kjører ca. 230 o/min med ca. 2,9 N·m | Girmotoren på 57 mm fra v0 (for treg), stepper (for svak) |
| **Motordriver** | **Pololu G2 24v13** (PWM og retning, strømgrense, strømsignal) | Tåler 3,3 V-logikk, og strømgrensen hindrer at strømforsyningen slår seg ut | BTS7960 |
| **Styring** | **ESP32-S3-DevKitC-1 med ESPHome 2026.9**, moduler på et bærekort | Samme plattform som før. NAU7802, PID, PWM-styrt motor og nettside er innebygd. | Klipper (trenger Linux og er laget for printere), egen fastvare |
| **Programlogikk** | Egen C++-komponent `bakeplan`: tidsplanlegger og regulator med enhetstester og simulering. Dosering etter vekt i C++. | Testbar på PC. Simuleringen viser at deigen ender på riktig heving og normalt treffer innen ±40 min (ca. 10 min etter læring). | Logikk i YAML-skript |
| **Hevemåling** | **ToF** (VL53L0X) i taket og **kamera** (Pi Zero 2 W + Camera Module 3 Wide) | Rette vegger i formen gir heving direkte fra høyden. Kameraet gir en ekstra måling og ser feil. | Bare modellen, uten måling: deigen ender på 47–184 % av målet |
| **Levain** | Bygges i formen. Styres av modellen, fordi laget er for tynt til å måles. **Maskinen veier surdeigen.** | Bulkhevingen måles og retter opp. Simuleringen viser at det holder. | Egen levainkopp (plass og helleretning, som i v0) |
| **Læring** | Aktiviteten til surdeigen lagres etter hver baking og brukes neste gang | Etter én baking er tidsfeilen ca. 10 min i simuleringen | – |
| **Form og mål** | Kammer til høyre, tårn til venstre (vann, motor og elektronikk), mel og salt over taket. 48 × 31 × 53 cm (fra CAD). | En vannrett melskrue må sitte over formen | Under 45 cm (krever skrå skrue eller mindre melbeholder, kan komme i v2) |

## Konsekvenser

**Positivt:**
- Det mest usikre i v0 (eltingen) er byttet ut med en løsning som er velprøvd.
- Vekta gir nøyaktig dosering og veier surdeigen. Den ser også når mel- eller vannbeholderen er tom, siden vekta da ikke øker.
- Tidsplanleggeren er testet i simulering før noe er bygget.

**Risiko som må følges opp:**
- **Melskruen (E11)** er den største utviklingsjobben. Reserveplanen er at du heller i forhåndsveid mel og maskinen gjør resten (N2).
- **Formen og koblingen** må måles på en giver før CAD-målene låses. Holderen for formen printes etter målene.
- **Høyden** (53 cm) og bredden (48 cm) er over rammen på 45 cm i [kravene](../00-visjon-og-suksesskriterier.md). Melbeholderen rommer to brød, ikke fire.
- **Tidspresisjonen ved første baking** med en ukjent surdeig er ±40–60 min. Mål nær det tidligst mulige gir varsel om liten margin.
- **ESPHome-støtten for TMC2209 over UART** er ny. Stepperne kjøres med step/dir til den er sluppet.

**Endringer i planen:**
- v0 i [`hardware/v0/`](../../hardware/v0/README.md) og [`firmware/v0/`](../../firmware/v0/README.md) beholdes som referanse, men bygges ikke.
- Veikartet hopper over byggefasen for v0 og går rett til v1.
