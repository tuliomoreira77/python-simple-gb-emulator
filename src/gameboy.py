from motherboard import *

### TESTE
#01 - PASSED
#02 - FAILED
#03 - PASSED
#04 - PASSED
#05 - PASSED
#06 - PASSED
#07 - PASSED 
#08 - PASSED
#09 - PASSED
#10 - PASSED
#11 - PASSED

def load_rom_file():
    with open('../roms/10.gb', 'rb') as f:
        binary_data = f.read()
        return binary_data

rom = load_rom_file()
motherboard = Motherboard(rom)

motherboard.memory_bus.write_byte(0xFF41, 0b01010011)
motherboard.cpu.execute_step(50000000000000)

