MODE_DIRECT = 0
MODE_INDIRECT = 1

def get_hex(num, base=10):
    if type(num) == int:
        return hex(int(num))[2::].zfill(2)
    elif type(num) == str:
        return hex(int(num, base))[2::].zfill(2)

def get_num(p):
    if p.startswith('0x'):
        op_val = int(p, 16)
    elif p.startswith('0b'):
        op_val = int(p, 2)
    elif p.startswith("'") and p.endswith("'"):
        op_val = ord(p[1:-1:])
    else:
        op_val = int(p)
    return op_val

def assemble(filename, instruction_set_filename="instruction_set.inst"):
    # load instruction set
    instruction_table = {}
    # {("NAME", mode), ID)
    with open(instruction_set_filename, "r") as file:
        for line in file.readlines():
            if line.startswith(":"):
                name, address, *_ = line[1::].strip().replace('\n', '').split(' ')

                mode = None

                if "_" in name:
                    name, mode_str = name.split('_')
                    if mode_str == 'i':
                        mode = MODE_INDIRECT
                    elif mode_str == 'd':
                        mode = MODE_DIRECT
                else:
                    mode = MODE_DIRECT

                instruction_table[(name.lower(), mode)] = int(address, 16)

    # load instructions
    instructions = []
    with open(filename, "r") as file:

        for line in file.readlines():
            actual_line = ""
            for c in line.strip().replace('\n', ''):
                if c == ";":
                    break
                actual_line += c
            if not actual_line:
                continue

            command, *ops = actual_line.split()
            instructions.append((command, ops))

    output = []
    labels = {}
    address = 0
    for instruction, op in instructions:
        if instruction.startswith('.'):  # asm instruction
            if instruction == '.const':
                for o in op:
                    output.append(get_hex(get_num(o)))
                    address += 1
            elif instruction == '.ascii':
                text = "".join(op)
                assert text.startswith('"') and text.endswith('"')
                for c in text:
                    output.append(get_hex(ord(c)))
                    address += 1
        elif instruction.endswith(':'):  # label
            labels[instruction[:-1:]] = address
        else:  # normal instruction
            mode = MODE_DIRECT
            if op:
                if op[0].startswith('[') and op[0].endswith(']'):
                    mode = MODE_INDIRECT
                    operator = op[0][1:-1:]
                else:
                    operator = op[0]

            output.append(get_hex(instruction_table[(instruction.lower(), mode)]))
            address += 1
            if op:
                if operator.startswith(':'):
                    output.append(operator)
                else:
                    output.append(get_hex(get_num(operator)))
                address += 1

    real_output = []
    for val in output:
        if val.startswith(':'):
            real_output.append(get_hex(labels[val[1::]]))
        else:
            real_output.append(val)
    print(real_output)
    return "".join(real_output)
