import donut

shellcode = donut.create(file="loader.exe", arch=2)

with open("shellcode.bin", "wb") as f:
    f.write(shellcode)

print("[+] shellcode.bin berhasil dibuat!")