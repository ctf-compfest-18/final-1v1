vm = open("vm.ppm", "rb").read()
code = vm.split(b"\n", 3)[3]  # skip the three PPM header lines

regs = {0x5F: "PC", 0x6F: "R1", 0x7F: "R2", 0x8F: "R3", 0x9F: "R4", 0xAF: "R5"}
ops = {
    0x31: "MOV_REG",
    0x40: "ADD",
    0x41: "SUB",
    0x42: "XOR",
    0x70: "EXIT_IF_NOT_EQUAL",
}

for ip in range(0, len(code) - 2, 3):
    op, a, b = code[ip : ip + 3]
    ra = regs.get(a, f"R[{a:02x}]")
    rb = regs.get(b, f"R[{b:02x}]")

    if op == 0x30:
        text = f"MOV_IMM {ra}, 0x{b:02x}"
    elif op == 0x60:
        text = f"USER_BUF {ra}, {rb}"
    elif op == 0xFF:
        text = "HALT"
    elif op in ops:
        text = f"{ops[op]} {ra}, {rb}"
    else:
        text = f"UNKNOWN 0x{op:02x}"

    print(f"{ip:04x}: {text}")
    if op == 0xFF:
        break
