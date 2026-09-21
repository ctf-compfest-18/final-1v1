with open("deloken.zip", "rb") as f:
    data = f.read()

encrypted = bytes([b ^ 0x67 for b in data])

c_array = ", ".join([f"0x{b:02x}" for b in encrypted])
print(c_array)