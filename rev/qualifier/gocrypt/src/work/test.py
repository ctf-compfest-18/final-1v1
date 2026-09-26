from pwn import *

a = open("flag.enc", "rb").read() + b"\0" * 3
info(a.__len__())
info(unpack_many(a, 64))

print(hex())
