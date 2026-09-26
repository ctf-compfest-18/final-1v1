a = open("fak", "rb").read()
enc = open("flag.enc", "rb").read()

from pwn import xor

stream = a[8 + 16 :]
ct = enc[8 + 16 :]

print(xor(stream, ct))
