import csim
import assembler

if __name__ == '__main__':
    prg = assembler.assemble("programm.S")

    sim = csim.Csim()
    sim.load_mc("instruction_set.inst")
    # sim.load_mem("programm.mem")
    sim.set_mem(prg)
    sim.exec()
    sim.debug_flush()
