# ADR-002: Plattform for måleoppsettet og hevekassen (fase 1)

- **Status:** foreslått
- **Dato:** 2026-10-13
- **Port:** G0

## Kontekst

I fase 1 trengs et måleoppsett som raskt kan logge temperatur, heving og vekt under eksperimentene E01–E09. Det skal også styre hevekassen med både varme og kjøling. Det viktigste er å komme raskt i gang og få pålitelige data. Det er ikke viktig at oppsettet kan gjenbrukes i den endelige maskinen.

## Alternativer

1. **ESP32-S3 + ESPHome.** Oppsettet skrives i YAML. PID-regulering med varme- og kjøleutgang i samme sløyfe. Komponenter for DS18B20, SHT4x, VL53L0X/L1X, HX711, NAU7802 og MAX318xx. Data går til Home Assistant eller via MQTT til en enkel logger.
2. **ESP32 med egen Arduino- eller ESP-IDF-kode.** Full fleksibilitet, men mer kode å skrive og feilsøke.
3. **Raspberry Pi alene.** Gir kamera og logging lokalt, men GPIO og sanntid er svakere, og den er mer sårbar for strømbrudd.
4. **MadMachine SwiftIO Micro.** Swift og en kraftig MCU, men ingen Wi-Fi og flere drivere som mangler (se [arkitektur](../07-arkitektur.md)).

## Beslutning (forslag)

Vi velger **alternativ 1: ESP32-S3 med ESPHome**. Data logges til CSV via MQTT, eller til Home Assistant/InfluxDB hvis det finnes fra før. ESPHome-oppsettet legges i `firmware/lab/`.

## Konsekvenser

- Hevekassen kan styres med en ferdig PID-komponent, uten egen reguleringskode.
- Oppsettet gir erfaring med sensorene som også er aktuelle i prototypen.
- Hovedstyringen for prototypen velges senere (ADR-004, port G2). SwiftIO kan fortsatt prøves som et hobbyspor uten å forsinke eksperimentene.
