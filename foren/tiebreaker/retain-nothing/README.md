# Retain Nothing

`Retain Nothing` is a tiebreaker focused on MQTT state recovery. The PCAP contains normal traffic followed by a retained-message deletion event.

## Release

- Author: PolarBear7
- Connection: none; this is an offline challenge.
- Public attachment: `public/retain-nothing.pcap`

This tiebreaker has no participant hint and does not use a password-protected ZIP.

## Local QA

```bash
python src/generate_pcap.py
tshark -r public/retain-nothing.pcap -Y mqtt
```

The public artifact is the PCAP. Derive the static flag by hashing the exact last retained configuration payload before deletion, as specified in challenge.yml. The PCAP does not contain a literal flag. An unrelated live broker is not needed.

## Technical focus

MQTT packet interpretation, retained-message semantics, and packet-order reconstruction. This is based on the MQTT standard rather than a CVE.
