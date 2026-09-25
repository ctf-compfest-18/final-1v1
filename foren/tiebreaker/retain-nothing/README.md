# Retain Nothing

`Retain Nothing` is a tiebreaker focused on MQTT state recovery. The capture contains normal traffic followed by a retained-message deletion event.

## Release

- Author: Kyraux
- Connection: none; this is an offline challenge.
- Public attachment: `public/retain-nothing.zip`
- Dist password: `RN-6bR3wY8nT5kQ`

The password is included here for committee distribution. The participant README (`public/README.md`: name, author, description, connection, hint 1) is published both next to and inside the password-protected ZIP `public/retain-nothing.zip`, which also contains the capture `retain-nothing.pcap`. One participant hint ships in the ZIP; the reserve hint below is given via Discord only if both teams are stuck.

## Hint (reserve; give via Discord only if both teams are stuck)

"List the MQTT publishes with `tshark -r retain-nothing.pcap -Y mqtt -T fields -e mqtt.topic -e mqtt.retain`. The last retained payload on `gateway/07/config` before the empty (clear) publish is the configuration. Submit the lowercase SHA-256 of that payload's exact bytes as `COMPFEST18{sha256}`."

## Local QA

```bash
python src/generate_pcap.py
tshark -r .build/retain-nothing.pcap -Y mqtt
```

The public artifact is the encrypted ZIP. Derive the static flag by hashing the exact last retained configuration payload before deletion, as specified in challenge.yml. The capture does not contain a literal flag. An unrelated live broker is not needed.

## Technical focus

MQTT packet interpretation, retained-message semantics, and packet-order reconstruction. This is based on the MQTT standard rather than a CVE.
