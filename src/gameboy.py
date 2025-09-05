from cpu import *

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
    with open('../roms/10-bit_ops.gb', 'rb') as f:
        binary_data = f.read()
        return binary_data


cpu = CPU(load_rom_file())

cpu.execute()