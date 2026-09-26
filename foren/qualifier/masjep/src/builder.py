import os
import json
import struct

def xor_data(data, key):
    return bytes([b ^ key for b in data])

def main():
    # 1. Buat isi dari sysinfo.json
    sysinfo_data = {
        "infected_user": "masjep",
        "os_build": "Windows 11 Pro",
        "suspicious_process": "pe64.exe",
    }
    sysinfo_bytes = json.dumps(sysinfo_data).encode()

    # 2. Baca shellcode.bin
    if not os.path.exists("shellcode.bin"):
        print("[-] Error: shellcode.bin tidak ditemukan!")
        return

    with open("shellcode.bin", "rb") as f:
        shellcode_bytes = f.read()

    # 3. Enkripsi Data
    sysinfo_key = 0x67
    shellcode_key = 0x67
    
    sysinfo_enc = xor_data(sysinfo_bytes, sysinfo_key)
    shellcode_enc = xor_data(shellcode_bytes, shellcode_key)

    # 4. Enkripsi Nama File
    name1 = b"sysinfo.json"
    name2 = b"shellcode.bin"

    name1_enc = xor_data(name1, sysinfo_key)
    name2_enc = xor_data(name2, shellcode_key)

    # 5. Bangun Struktur Header
    magic_bytes = b"masjep"
    end_header_marker = b"\x67\x67\x67\x67"
    header_size = len(magic_bytes) + (1 + len(name1_enc) + 8) + (1 + len(name2_enc) + 8) + len(end_header_marker)
    
    offset1 = header_size
    size1 = len(sysinfo_enc)
    
    offset2 = offset1 + size1
    size2 = len(shellcode_enc)

    # 6. Rakit File Kontainer Final
    with open("masjep", "wb") as f:
        f.write(magic_bytes)
        
        f.write(struct.pack("<B", len(name1_enc)))
        f.write(name1_enc)
        f.write(struct.pack("<II", offset1, size1)) 

        f.write(struct.pack("<B", len(name2_enc)))
        f.write(name2_enc)
        f.write(struct.pack("<II", offset2, size2))
        
        f.write(end_header_marker)

        f.write(sysinfo_enc)
        f.write(shellcode_enc)

        f.write(struct.pack("<BB", sysinfo_key, shellcode_key))
        f.write(b"END!")

    print("[+] Custom container 'masjep' berhasil dirakit!")
    print(f"    - Offset File 1 : {hex(offset1)} | Size: {hex(size1)}")
    print(f"    - Offset File 2 : {hex(offset2)} | Size: {hex(size2)}")

if __name__ == "__main__":
    main()