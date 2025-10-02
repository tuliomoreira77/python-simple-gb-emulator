from motherboard import *

### TESTE
#01 - PASSED
#02 - FAILED
#03 - PASSED
#04 - PASSED
#05 - PASSED
#06 - PASSED
#07 - FAILED 
#08 - PASSED
#09 - FAILED
#10 - FAILED
#11 - FAILED

def load_rom_file():
    with open('../roms/02.gb', 'rb') as f:
        binary_data = f.read()
        return binary_data

rom = load_rom_file()
motherboard = Motherboard(rom)

motherboard.memory_bus.write_byte(0xFF41, 0b01010011)
motherboard.cpu.execute_step(50000000000000)

