def bitfield(n):
    return [digit == "1" for digit in (bin(n)[-1:1:-1])]

class MicroInstruction:
    def __init__(self, instruction):
        self.data = instruction

    def __getitem__(self, item):
        if item >= len(self.data):
            return 0
        return self.data[item]

    a_in = 15
    a_out = 14

    b_in = 13
    b_out = 12

    op_in = 11

    pc_in = 10
    pc_out = 9

    add_out = 8

    adr_in = 7

    inst_in = 6

    ram_in = 5
    ram_out = 4

    pc_inc = 3

    inst_cl = 2

    noop = 0  # active low

    @staticmethod
    def get(instruction: int):
        return MicroInstruction(bitfield(instruction))
