import array as arr
import os
import time

BANK_ROM_BASE = 0x4000
BANK_RAM_BASE = 0x2000

class Cartridge:
    rom_bank_offset = 0
    ram_bank_offset = 0

    def __init__(self, game_rom, rom_name = 'default'):
        self.mbc = self.get_mbc(game_rom, rom_name)

    def read_rom(self, addr):
        return self.mbc.read_rom(addr)

    def read_ram(self, addr):
        return self.mbc.read_ram(addr)
    
    def write_ram(self, addr, value):
        self.mbc.write_ram(addr, value)
    
    def select_rom(self, bank):
        self.mbc.select_rom(bank)

    def select_ram(self, bank):
        self.mbc.select_ram(bank)

    def select_extra(self, value):
        self.mbc.select_extra(value)

    def load_save(self):
        self.mbc.load_save()

    def save_game(self):
        self.mbc.save_game()


    def get_mbc(self, game_rom, rom_name):
        game_type = game_rom[0x147]
        if game_type == 0x00: ## ROM ONLY
            return MBC0(game_rom, rom_name)
        
        if game_type == 0x0F: ## MBC3 + BATTERY + TIMER
            return MBC3(game_rom, rom_name, with_ram=False, with_battery=True, with_rtc=True)
        
        if game_type == 0x10: ## MBC3 + RAM + BATTERY + TIMER
            return MBC3(game_rom, rom_name, with_ram=True, with_battery=True, with_rtc=True)
        
        if game_type == 0x11: ## MBC3
            return MBC3(game_rom, rom_name, with_ram=False, with_battery=False, with_rtc=False)
        
        if game_type == 0x12: ## MBC3 + RAM
            return MBC3(game_rom, rom_name, with_ram=True, with_battery=False, with_rtc=False)
        
        if game_type == 0x13: ## MBC3 + RAM + BATTERY
            return MBC3(game_rom, rom_name, with_ram=True, with_battery=True)
        
        if game_type == 0x01: ## MBC1 + RAM + BATTERY
            return MBC1(game_rom, rom_name, with_ram=False, with_battery=False)
        
        if game_type == 0x02: ## MBC1 + RAM
            return MBC1(game_rom, rom_name, with_ram=True, with_battery=False)
        
        if game_type == 0x03: ## MBC1 + RAM + BATTERY
            return MBC1(game_rom, rom_name, with_ram=True, with_battery=True)
    

class MBC0:
    def __init__(self, game_rom, rom_name = 'default'):
        self.game_rom = game_rom
        self.rom_size = len(game_rom)
        self.rom_name = rom_name

    def read_rom(self, addr):
        return self.game_rom[addr]

    def read_ram(self, addr):
        return 0x00
    
    def write_ram(self, addr, value):
        pass
    
    def select_rom(self, bank):
        pass

    def select_ram(self, bank):
        pass

    def select_extra(self, value):
        pass

    def load_save(self):
        pass

    def save_game(self):
        pass

class MBC3:
    RAM_SIZE = 0x8000

    rom_bank_offset = 0
    ram_bank_offset = 0
    rtc_register = 0x00

    def __init__(self, game_rom, rom_name = 'default', with_ram=False, with_battery=False, with_rtc=False):
        self.game_rom = game_rom
        self.rom_size = len(game_rom)
        self.rom_name = rom_name
        self._with_ram = with_ram
        self._with_battery = with_battery
        self._with_rtc = with_rtc
        self.save_handler = FileSystemSaveHandler(self.RAM_SIZE, rom_name)
        self.load_save()

    def read_rom(self, addr):
        if addr < 0x4000:
            return self.game_rom[addr]
        
        return self.game_rom[addr + self.rom_bank_offset]

    def read_ram(self, addr):
        if self.rtc_register != 0x00:
            return self.rtc_decode()
        
        if not self._with_ram:
            return 0x00
        
        return self.ext_ram[addr - 0xa000 + self.ram_bank_offset]
    
    def write_ram(self, addr, value):
        if not self._with_ram:
            return
        
        self.ext_ram[addr - 0xa000 + self.ram_bank_offset] = value & 0xFF
    
    def select_rom(self, bank):
        if bank == 0:
            self.rom_bank_offset = 0
            return
        
        self.rom_bank_offset = (bank - 1) * BANK_ROM_BASE

    def select_ram(self, bank):
        if bank > 0x07 and self._with_rtc:
            self.rtc_register = bank
            return
        
        self.rtc_register = 0x00
        self.ram_bank_offset = bank * BANK_RAM_BASE

    def select_extra(self, value):
        pass

    def rtc_decode(self):
        utc_time = time.time()
        if self.rtc_register == 0x08:
            return int(utc_time) % 60
        if self.rtc_register == 0x09:
            return int(utc_time / 60) % 60
        if self.rtc_register == 0x0A:
            return int(utc_time / 3600) % 24
        if self.rtc_register == 0x0b:
            return int(utc_time / 86400) % 256
        if self.rtc_register == 0x0C:
            return 0x00
        
    def load_save(self):
        if self._with_battery:
            self.ext_ram = self.save_handler.load_save()
        else:
            self.ext_ram = arr.array('B', [0x00] * (self.RAM_SIZE))

    def save_game(self):
        if self._with_battery:
            self.save_handler.save_game(self.ext_ram)
        else:
            self.ext_ram = arr.array('B', [0x00] * (self.RAM_SIZE))


class MBC1:
    RAM_SIZE = 0x8000

    rom_bank_offset = 0
    ram_bank_offset = 0

    second_rom_bank = 0
    banking_mode = 0

    def __init__(self, game_rom, rom_name = 'default', with_ram=False, with_battery=False):
        self.game_rom = game_rom
        self.rom_size = len(game_rom)
        self.rom_name = rom_name
        self._with_ram = with_ram
        self._with_battery = with_battery 
        self.save_handler = FileSystemSaveHandler(self.RAM_SIZE, rom_name)

        self.ext_ram = self.load_save()

    def read_rom(self, addr):
        if addr < 0x4000 and not self.banking_mode:
            return self.game_rom[addr]
        
        if addr < 0x4000 and self.banking_mode:
            return self.game_rom[addr + self.second_rom_bank * BANK_ROM_BASE]
        
        return self.game_rom[addr + self.rom_bank_offset]

    def read_ram(self, addr):
        if not self._with_ram:
            return 0x00
        
        return self.ext_ram[addr - 0xa000 + self.ram_bank_offset]
    
    def write_ram(self, addr, value):
        if not self._with_ram:
            return
        
        self.ext_ram[addr - 0xa000 + self.ram_bank_offset] = value & 0xFF
    
    def select_rom(self, bank):
        bank = bank & 0x1F
        if bank == 0:
            self.rom_bank_offset = self.second_rom_bank | 0
            return
        
        self.rom_bank_offset = ((self.second_rom_bank | bank) - 1) * BANK_ROM_BASE

    def select_ram(self, bank):
        if self.banking_mode == 0:
            self.ram_bank_offset = bank * BANK_RAM_BASE
        else:
            self.second_rom_bank_offset = (bank & 0x11) << 5

    def select_extra(self, value):
        self.banking_mode = value & 0x1
        
    def load_save(self):
        if self._with_battery:
            self.ext_ram = self.save_handler.load_save()
        else:
            self.ext_ram = arr.array('B', [0x00] * (self.RAM_SIZE))

    def save_game(self):
        if self._with_battery:
            self.save_handler.save_game(self.ext_ram)
        else:
            self.ext_ram = arr.array('B', [0x00] * (self.RAM_SIZE))


class FileSystemSaveHandler:
    SAVE_PATH = './game_saves'

    def __init__(self, ram_size, rom_name):
        self.ram_size = ram_size
        self.rom_name = rom_name

    def load_save(self):
        try:
            with open(self.SAVE_PATH + '/' + self.rom_name + ".sav", 'rb') as f:
                binary_data = f.read()

                ## ENSURE COMPATIBILITY WITH OLD SAVE GAMES
                if len(binary_data) == self.ram_size: 
                    return arr.array('B', binary_data)
                else:
                    return arr.array('I', binary_data)
        except:
            return arr.array('B', [0x00] * (self.ram_size))

    def save_game(self, ext_ram):
        if not os.path.exists(self.SAVE_PATH):
            os.makedirs(self.SAVE_PATH)
        with open(self.SAVE_PATH + '/' + self.rom_name + ".sav", "wb") as f:
            f.write(bytes([i & 0xFF for i in ext_ram]))