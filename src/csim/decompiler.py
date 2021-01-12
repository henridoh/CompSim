instructions = {
    0x00: ("fetch", 0),
    0x01: ("LDA ind", 1),
    0x02: ("LDA dir", 1),
    0x03: ("LDB ind", 1),
    0x04: ("LDB dir", 1),
    0x05: ("ADDAB", 0),
    0x06: ("JMD dir", 1),
    0x07: ("STA", 1),
    0x08: ("STB", 1),
    0x09: ("JZ", 1),
    0x0a: ("JNZ", 1),
    0x0b: ("JN", 1),
    0x0c: ("JP", 1),
    0x0d: ("OUTA", 0)
}

def decompile(data, addr, n=5, pc=None):
    for _ in range(n):
        name, args = instructions.get(data[addr], ("Unknown", 1))
        if name == "Unknown":
            addr -= 1
        if addr == pc:
            print(end="\033[92m")
        print(end=f"[0x{addr:04x}]: {name} ")
        addr += 1
        for _ in range(args):
            print(hex(data[addr]), end=" ")
            addr += 1
        print("\033[0m")
