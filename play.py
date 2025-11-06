import argparse
from emulator.core.cartridge import *
from emulator.gameboy import *


def load_rom_file(filename):
    with open('./roms/' + filename, 'rb') as f:
        binary_data = f.read()
        return binary_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Gamboy Emulator")
    parser.add_argument("rom", help="Rom name inside folder roms")
    parser.add_argument("--serial", required=False, help="Selects if serial is enabled and if its server or client")

    args = parser.parse_args()
    file_name = args.rom
    serial = args.serial

    game = Cartridge(load_rom_file(file_name), file_name)
    gameboy = Gameboy(serial=serial)
    gameboy.play(game)