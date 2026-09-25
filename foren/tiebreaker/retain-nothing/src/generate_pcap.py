from pathlib import Path
import ipaddress
import struct
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".build/retain-nothing.pcap"
STATE = b'{"device":"gateway-07","mode":"armed","slot":"night","revision":42,"receipt":"905d0841228374f176ba0a98f1910c9b"}'
CLIENT = ipaddress.IPv4Address("10.14.8.21").packed
BROKER = ipaddress.IPv4Address("10.14.8.53").packed
CLIENT_PORT, BROKER_PORT = 42000, 1883


def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\0"
    total = sum(int.from_bytes(data[index:index + 2], "big") for index in range(0, len(data), 2))
    while total > 0xFFFF:
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def remaining_length(value: int) -> bytes:
    result = bytearray()
    while True:
        digit = value % 128
        value //= 128
        result.append(digit | (0x80 if value else 0))
        if not value:
            return bytes(result)


def mqtt_connect() -> bytes:
    payload = b"\0\4MQTT\4\2\0<\0\x0agateway-07"
    return b"\x10" + remaining_length(len(payload)) + payload


def mqtt_publish(payload: bytes, retained: bool = True) -> bytes:
    topic = b"gateway/07/config"
    body = struct.pack(">H", len(topic)) + topic + payload
    return bytes([0x31 if retained else 0x30]) + remaining_length(len(body)) + body


def tcp_packet(src: bytes, dst: bytes, sport: int, dport: int, seq: int, ack: int, flags: int, payload: bytes = b"") -> bytes:
    tcp = struct.pack(">HHIIBBHHH", sport, dport, seq, ack, 5 << 4, flags, 65535, 0, 0) + payload
    pseudo = src + dst + struct.pack(">BBH", 0, 6, len(tcp))
    tcp = tcp[:16] + struct.pack(">H", checksum(pseudo + tcp)) + tcp[18:]
    ip = struct.pack(">BBHHHBBH4s4s", 0x45, 0, 20 + len(tcp), 0x5000 + seq % 1000, 0x4000, 64, 6, 0, src, dst)
    ip = ip[:10] + struct.pack(">H", checksum(ip)) + ip[12:]
    ethernet = b"\x02\0\0\0\0\21\x02\0\0\0\0\53\x08\0"
    return ethernet + ip + tcp


PAYLOADS = [
    mqtt_connect(),
    mqtt_publish(b'{"device":"gateway-07","mode":"standby","revision":41}'),
    mqtt_publish(STATE),
    mqtt_publish(b'{"device":"gateway-07","mode":"test","revision":43}', retained=False),
    mqtt_publish(b""),
]
OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("wb") as handle:
    handle.write(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
    sequence = 1000
    for index, payload in enumerate(PAYLOADS):
        packet = tcp_packet(CLIENT, BROKER, CLIENT_PORT, BROKER_PORT, sequence, 2000, 0x18, payload)
        handle.write(struct.pack("<IIII", 1787440000 + index, 0, len(packet), len(packet)))
        handle.write(packet)
        sequence += len(payload)
flag = "COMPFEST18{" + hashlib.sha256(STATE).hexdigest() + "}"
metadata = ROOT / "challenge.yml"
metadata.write_text(re.sub(r"COMPFEST18\{[0-9a-f]+\}", flag, metadata.read_text()))
print(OUT)
