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

    args = parser.parse_args()
    file_name = args.rom

    game = Cartridge(load_rom_file(file_name), file_name)
    gameboy = Gameboy()
    gameboy.play(game)