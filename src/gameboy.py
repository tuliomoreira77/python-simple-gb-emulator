from motherboard import *

basic_rom = [
    0xc6,
    0x01,
    0xCB,
    0x47,
    0xc6,
    0x01,
    0xCB,
    0x47,
    0x00
]


def load_rom_file():
    with open('../roms/06.gb', 'rb') as f:
        binary_data = f.read()
        return binary_data

rom = load_rom_file()
motherboard = Motherboard(rom)
##tests = CPUTests(motherboard)

motherboard.memory_bus.write_byte(0xFF41, 0b01010011)
motherboard.cpu.execute_step(1000000)

#print('Register A: {}', hex(motherboard.cpu.r_a))
#print('Register B: {}', hex(motherboard.cpu.r_b))
#print('Register C: {}', hex(motherboard.cpu.r_c))
#print('Register D: {}', hex(motherboard.cpu.r_d))
#print('Register E: {}', hex(motherboard.cpu.r_e))
#print('Register H: {}', hex(motherboard.cpu.r_h))
#print('Register L: {}', hex(motherboard.cpu.r_l))
#print('PC: {}', hex(motherboard.cpu.program_counter))

