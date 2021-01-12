from csim.register import Register, Adder, FlagRegister
from csim.bus import Bus
from csim.memory import Memory
from csim.mc import MicroInstruction
from csim.constants import memory_size, memory_word_cap, microcode_size,\
                           microcode_word_cap, microcode_si_size, microcode_flags_size
from csim.decompiler import decompile

F_ZERO = 0
F_NEGATIVE = 1

class Csim:
    def __init__(self):
        self.bus = Bus()

        self.reg_a = Register()  # accumulator
        self.reg_b = Register()  # general purpose register

        self.reg_pc = Register()  # program counter

        self.reg_add = Adder(self.reg_a, self.reg_b)  # adder (holds reg_a + reg_b)

        self.reg_adr = Register()  # address register

        self.reg_inst = Register(cap=0xFFFF)  # instruction register
        
        self.reg_status = FlagRegister(cap=2**microcode_flags_size-1)

        self.reg_op = Register(cap=0xFFFFFFFFF)

        self.ram = Memory(word_cap=memory_word_cap, size=memory_size)  # ram
        self.mc = Memory(word_cap=microcode_word_cap, size=microcode_size)  # Micro code

        self.logging = False

        self.output = []

    def run(self, instruction=1):
        self._tick()
        while self.reg_inst.value:
            self._tick()

    def log(self, text):
        print(f"[*] {text}")

    def exec(self):
        while self.ram[self.reg_pc.value]:
            self.run()
        for v in self.output:
            print(v, end=", ")
        print()
        for v in self.output:
            print(chr(v), end="")
        print()

    def debug_flush(self):
        print(
            f"\n\n\nA: 0x{self.reg_a.value:02X}; B: 0x{self.reg_b.value:02X}\n"
            f"PC: 0x{self.reg_pc.value:02X}\n"
            f"INST: 0x{self.reg_inst.value:03X} [{self.mc[self.reg_inst.value]}]\n"
            f"ADDR: 0x{self.reg_adr.value:02X}\n"
            f"FLAGS: Z:{self.reg_status[F_ZERO]} N:{self.reg_status[F_NEGATIVE]}"
        )
        for i in range(256):
            if not i % 16:
                print(f"\n{hex(i)[2:].zfill(2)}| ", end="")
            if i == self.reg_pc.value:
                print(end="\u001b[31m")
            elif i == self.reg_adr.value:
                print(end="\033[92m")
            print(hex(self.ram[i])[2:].zfill(2), end=" ")
            print(end="\033[0m")
        print("\n")
        start = self.reg_pc.value - min(self.reg_pc.value, 5)
        decompile(self.ram.data, start, pc=self.reg_pc.value, n=20)

    def _tick(self):
        self._run(self.mc[(self.reg_inst.value << 2) | self.reg_status.value])

    def _run(self, micro_instruction):
        # TODO: just loop over every register

        mc = MicroInstruction.get(micro_instruction)

        set_zero = False
        set_negative = False

        if not mc[mc.noop]:  # active low
            self.log("NOOP")
            self.reg_pc.value += 1
            self.reg_inst.value = 0
            return

        if mc[mc.a_out]:
            self.bus.value = self.reg_a.value
            self.log(f"A out [{self.bus.value:02x}]")
        if mc[mc.b_out]:
            self.bus.value = self.reg_b.value
            self.log(f"B out [{self.bus.value:02x}]")
        if mc[mc.pc_out]:
            self.bus.value = self.reg_pc.value
            self.log(f"PC out [{self.bus.value:02x}]")
        if mc[mc.add_out]:
            self.bus.value = self.reg_add.value
            self.log(f"ADD out [{self.bus.value:02x}]")

        if mc[mc.ram_out]:
            self.bus.value = self.ram[self.reg_adr.value]
            self.log(f"RAM out [{self.bus.value:02x}]")

        if mc[mc.a_in]:
            self.reg_a.value = self.bus.value
            self.log(f"A in [{self.bus.value:02x}]")
            set_zero = True
            set_negative = True
        if mc[mc.b_in]:
            self.reg_b.value = self.bus.value
            self.log(f"B in [{self.bus.value:02x}]")
            set_zero = True
            set_negative = True

        if mc[mc.op_in]:
            self.reg_op.value = self.bus.value
            self.log(f"OP in [{self.bus.value:02x}]")
            print(f"Output recieved: {self.reg_op.value} {chr(self.reg_op.value)}")
            self.output.append(self.reg_op.value)
        if mc[mc.pc_in]:
            self.reg_pc.value = self.bus.value
            self.log(f"PC in [{self.bus.value:02x}]")
        if mc[mc.adr_in]:
            self.reg_adr.value = self.bus.value
            self.log(f"ADR in [{self.bus.value:02x}]")

        if mc[mc.inst_in]:  # Load instruction from ram into reg_inst
            self.reg_inst.value = ((self.bus.value << microcode_si_size) & ~(2 ** microcode_si_size - 1))
            self.log(f"INST in [{self.bus.value:02x}/{self.reg_inst.value:04x}]")

        if mc[mc.ram_in]:
            self.ram[self.reg_adr.value] = self.bus.value
            self.log(f"RAM in [{self.bus.value:02x}]")

        if mc[mc.pc_inc]:
            self.reg_pc.value += 1
            self.log(f"PC increase [{self.reg_pc.value:02x}]")

        if mc[mc.inst_cl]:
            self.log("INST clear")
            self.reg_inst.value = 0
        elif not mc[mc.inst_in]:
            self.reg_inst.value += 1
            self.log(f"INST increase [{self.reg_inst.value}]")

        if set_zero:
            self.reg_status[F_ZERO] = not self.bus.value
        if set_negative:
            self.reg_status[F_NEGATIVE] = self.bus.value & ((self.bus.cap + 1) >> 1) != 0

        self.log("")

    def load_mc(self, filename):
        with open(filename, "r") as file:
            flags = "_"
            addr = -1
            sub_addr = 0
            for line in file:
                if line[0] in ('#', '\n'):
                    continue
                if line[0] == ':':
                    addr = int(line.split(' ')[1], 16)
                    sub_addr = 0
                    flags = file.readline().replace('\n', '')
                    continue
                full_address = ((addr << microcode_si_size) | sub_addr) << 2
                for state in self.get_all_states(flags.lower()):
                    self.mc[full_address | state] = int(line.split('#')[0], 2)
                sub_addr += 1

    def get_all_states(self, flags):
        if flags == '_':
            for i in range(2**microcode_flags_size):
                yield i
            return

        flags = list(flags)

        dyn_pos = []
        for index, flag in enumerate(flags):
            if flag == 'x':
                dyn_pos += [index]

        for i in range(2**len(dyn_pos)):
            i_bits = bin(i)[2::].zfill(len(dyn_pos))
            for index, pos in enumerate(dyn_pos):
                flags[pos] = i_bits[index]
            yield int("".join(flags), 2)


    def load_mem(self, filename):
        with open(filename, "r") as file:
            addr = 0
            hexdump = file.read().replace('\n', '').replace(' ', '')
            for i in range(0, len(hexdump), 2):
                self.ram[addr] = int(hexdump[i:i+2], 16)
                addr += 1

    def set_mem(self, mem=""):
        hexdump = mem.replace('\n', '').replace(' ', '')
        addr = 0
        for i in range(0, len(hexdump), 2):
            self.ram[addr] = int(hexdump[i:i + 2], 16)
            addr += 1