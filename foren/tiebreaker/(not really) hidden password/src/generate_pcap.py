import struct
import time
import random

random.seed(1337)  # hasil reproducible; hapus/ganti untuk capture yang berbeda

OUTFILE = "capture.pcap"
FLAG = "COMPFEST18{41w4y5_ch3ck_y0ur_c1ipb04rd}"
DECOY = "COMPFEST18{n0t_th3_fl4g_h3r3}"

# ===== Tingkat kesulitan (ubah sesuai kebutuhan) =====
BURSTS_PER_CHAR = (1, 3)   # jumlah burst junk sebelum tiap karakter flag
BURST_LEN = (3, 12)        # panjang tiap burst (minimal 3)
STACK_EXTRA = (2, 8)       # tambahan junk pada burst bertumpuk
# Contoh versi lebih berat: (3, 6), (10, 40), (5, 20)

# Hanya karakter yang di solver menjadi TEPAT 1 karakter.
# Jangan masukkan spasi, Enter, F1, dst. (jadi token "<SPACE>" dll.)
JUNK_ALPHABET = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789-_{}"
)

# USB HID usage IDs
KEYCODES = {
    **{chr(ord("a") + i): 0x04 + i for i in range(26)},
    "1": 0x1e, "2": 0x1f, "3": 0x20, "4": 0x21, "5": 0x22,
    "6": 0x23, "7": 0x24, "8": 0x25, "9": 0x26, "0": 0x27,
    "-": 0x2d,
    " ": 0x2c,
}

SHIFTED = {
    "_": 0x2d,
    "{": 0x2f,
    "}": 0x30,
}


def junk(n):
    return "".join(random.choice(JUNK_ALPHABET) for _ in range(n))


def simulate(actions):
    """Terapkan aksi seperti text field asli."""
    buf = []
    for kind, ch in actions:
        if kind == "key":
            buf.append(ch)
        elif buf:
            buf.pop()
    return "".join(buf)


def build_actions():
    actions = []

    def type_text(s):
        actions.extend(("key", c) for c in s)

    def backspace(n):
        actions.extend(("backspace", None) for _ in range(n))

    # Decoy: diketik lalu dihapus semuanya
    type_text(DECOY)
    backspace(len(DECOY))

    for ch in FLAG:
        for _ in range(random.randint(*BURSTS_PER_CHAR)):
            n = random.randint(*BURST_LEN)
            if random.random() < 0.5:
                # sederhana: ketik n junk, hapus n
                type_text(junk(n))
                backspace(n)
            else:
                # bertumpuk: ketik n, hapus k, ketik m, hapus semua sisanya
                k = random.randint(1, n - 1)
                m = random.randint(*STACK_EXTRA)
                type_text(junk(n))
                backspace(k)
                type_text(junk(m))
                backspace(n - k + m)
        actions.append(("key", ch))

    # Validasi: hasil akhir harus persis FLAG
    assert simulate(actions) == FLAG, "generator bug: net text != FLAG"
    # Validasi: setiap key yang diketik harus 1 karakter di solver
    assert all(
        c in KEYCODES or c in SHIFTED or c.isalpha()
        for k, c in actions if k == "key"
    ), "generator bug: karakter tidak didukung"
    assert " " not in "".join(c for k, c in actions if k == "key"), \
        "generator bug: spasi merusak solver modified"
    return actions


def hid_report(modifier, keycode):
    # 8 byte: modifier, reserved, key1..key6
    return bytes([modifier, 0x00, keycode, 0, 0, 0, 0, 0])


def char_to_report(ch):
    if ch in SHIFTED:
        return hid_report(0x02, SHIFTED[ch])  # Left Shift
    if ch.isalpha():
        return hid_report(0x02 if ch.isupper() else 0x00, KEYCODES[ch.lower()])
    if ch in KEYCODES:
        return hid_report(0x00, KEYCODES[ch])
    raise ValueError(f"Unsupported character: {ch!r}")


def usbpcap_header(irp_id, data_len, endpoint=0x81, device=5):
    # Header USBPcap 27 byte, DLT_USBPCAP = 249
    return struct.pack(
        "<HQIHBHHBBI",
        27,          # headerLen
        irp_id,      # IRP ID
        0,           # USBD status = success
        0x0009,      # URB_FUNCTION_BULK_OR_INTERRUPT_TRANSFER
        0x01,        # device -> host
        1,           # bus
        device,      # device address
        endpoint,    # 0x81 = IN
        1,           # interrupt transfer
        data_len,
    )


def write_packet(f, ts_sec, ts_usec, payload, irp_id, endpoint=0x81, device=5):
    packet = usbpcap_header(irp_id, len(payload), endpoint, device) + payload
    f.write(struct.pack("<IIII", ts_sec, ts_usec, len(packet), len(packet)))
    f.write(packet)


def main():
    actions = build_actions()  # assert dijalankan sebelum file dibuat

    with open(OUTFILE, "wb") as f:
        f.write(struct.pack(
            "<IHHIIII",
            0xA1B2C3D4,
            2, 4,
            0, 0,
            65535,
            249,
        ))

        ts_sec = int(time.time())
        ts_usec = 0
        irp_id = 0x1000

        # Beberapa report idle
        for _ in range(3):
            write_packet(f, ts_sec, ts_usec, b"\x00" * 8, irp_id)
            irp_id += 1
            ts_usec += 1000

        for kind, ch in actions:
            if kind == "key":
                report = char_to_report(ch)
            else:
                report = hid_report(0x00, 0x2a)  # Backspace

            write_packet(f, ts_sec, ts_usec, report, irp_id)       # press
            irp_id += 1
            ts_usec += 1000

            write_packet(f, ts_sec, ts_usec, b"\x00" * 8, irp_id)  # release
            irp_id += 1
            ts_usec += 1000

    n_bs = sum(1 for k, _ in actions if k == "backspace")
    print(f"[+] Generated: {OUTFILE}")
    print(f"[+] Intended flag: {FLAG}")
    print(f"[+] {len(actions)} key events, {n_bs} Backspace (0x2a).")


if __name__ == "__main__":
    main()