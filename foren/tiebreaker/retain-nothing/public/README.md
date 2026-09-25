# Retain Nothing

by Kyraux

---

## Description

An IoT gateway stopped serving its last configuration after a short MQTT incident. The attached capture records the broker traffic immediately before the outage.

Recover the last retained configuration published on the topic `gateway/07/config` before it was cleared.

The configuration payload is plain ASCII JSON. Submit the lowercase SHA-256 of the exact bytes of that retained PUBLISH payload as they appear in the capture: the full JSON text verbatim, including braces and quotes, with no added whitespace, trailing newline, or re-encoding. Wrap it as `COMPFEST18{sha256}`.

## Connection

None. This is an offline packet-capture challenge; no live broker is required.

## Hint

An MQTT broker keeps one retained message per topic: a later retained publish replaces it, and an empty retained publish clears it.
