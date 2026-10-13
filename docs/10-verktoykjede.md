# 10 – Verktøykjede: design med AI-agenter

> Sist verifisert: 2026-10-13. Feltet endrer seg svært raskt, og nye MCP-servere og agentverktøy for CAD og elektronikk dukker opp daglig. Dokumentet bygger på fire verktøyrapporter i [`forskning/verktoy/`](forskning/verktoy/) og skal skannes på nytt hver måned (se [«Holde seg oppdatert»](#holde-seg-oppdatert)).

<!-- ANBEFALT-STACK -->

## Prinsipper for agentstyrt maskinvaredesign

1. **Tekst framfor binærfiler.** Velg kildeformater som er lesbare og kan diffes i git: kode-CAD (Python), KiCad-filer (s-uttrykk), YAML for oppskrifter og ESPHome-oppsett. Da kan agenten lese og endre designet, og mennesket kan se gjennom endringen som en vanlig diff.
2. **Lukk sløyfen: agenten må kunne kontrollere sitt eget arbeid.** Hver endring etterfølges av en sjekk agenten kan lese: rendret bilde, målinger, ERC/DRC, simulering eller test i simulator. Ingen endring regnes som ferdig uten en slik sjekk.
3. **Mennesket godkjenner det som kan skade.** Alt som har med 230 V, varme, matkontakt eller fysisk handling å gjøre, skal godkjennes av et menneske. Det gjelder blant annet flashing av fastvare, utskrift på 3D-skriveren og påslag av varmeelementer eller instrumenter. Agenten får aldri gå forbi sikkerhetslagene i [`06-sikkerhet.md`](06-sikkerhet.md).
4. **Åpne formater i grensesnittene:** STEP og 3MF for mekanikk, KiCad og Gerber for kretskort, CSV for stykkliste og data. Da er prosjektet ikke låst til ett verktøy eller én MCP-server.
5. **Vurder MCP-servere før de tas i bruk** (se under). Mange er små hobbyprosjekter, og noen kan kjøre vilkårlig kode i CAD-programmet eller på maskinen.
6. **Lås versjonene.** Når et verktøy eller en MCP-server tas i bruk, noteres versjon eller commit i [`verktoy/`](../verktoy/). Da kan andre gjenskape arbeidsflyten.

## Kriterier for å vurdere en MCP-server

| Kriterium | Grønt | Rødt |
|---|---|---|
| Vedlikeholder | Kjent organisasjon, eller flere bidragsytere | Ukjent enkeltperson, ny konto |
| Aktivitet | Commits siste måned, utgitte versjoner | Ingen aktivitet på 6+ måneder |
| Bruk | Mange stjerner og issues som blir besvart | 0–5 stjerner |
| Lisens | OSI-godkjent, kompatibel med GPL-3.0 | Mangler lisens |
| Rettigheter | Bare lesing, eller tydelig avgrenset skriving | Kjører vilkårlig Python/shell, styrer maskinvare |
| Hemmeligheter | Ingen, eller lokale nøkler med minst mulig tilgang | Krever API-nøkler med full tilgang |
| Gjennomgang | Koden er lest før første bruk | «Bare installer og kjør» |

<!-- DETALJER -->

## Holde seg oppdatert

<!-- RESKANN -->
