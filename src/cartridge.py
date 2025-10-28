import array as arr
import os

BANK_ROM_BASE = 0x4000
BANK_RAM_BASE = 0x2000
SAVE_PATH = './game_saves'

class Cartridge:
    rom_bank_offset = 0
    ram_bank_offset = 0

    def __init__(self, game_rom, rom_name = 'default'):
        self.game_rom = game_rom
        self.rom_size = len(game_rom)
        self.rom_name = rom_name
        self.ext_ram = self.load_save()

    def read_rom(self, addr):
        return self.game_rom[addr + self.rom_bank_offset]

    def read_ram(self, addr):
        return self.ext_ram[addr - 0xa000 + self.ram_bank_offset]
    
    def write_ram(self, addr, value):
        self.ext_ram[addr - 0xa000 + self.ram_bank_offset] = value & 0xFF
    
    def select_rom(self, bank):
        if bank == 0:
            self.rom_bank_offset = BANK_ROM_BASE
            return
        
        self.rom_bank_offset = (bank - 1) * BANK_ROM_BASE

    def select_ram(self, bank):
        self.ram_bank_offset = bank * BANK_RAM_BASE

    def load_save(self):
        try:
            with open(SAVE_PATH + '/' + self.rom_name + ".sav", 'rb') as f:
                binary_data = f.read()
                return arr.array('I', binary_data)
        except:
            return arr.array('I', [0x00] * (0x7FFF +1))

    def save_game(self):
        if not os.path.exists(SAVE_PATH):
            os.makedirs(SAVE_PATH)
        with open(SAVE_PATH + '/' + self.rom_name + ".sav", "wb") as f:
            f.write(bytes(self.ext_ram))

    