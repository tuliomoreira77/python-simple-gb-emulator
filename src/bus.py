
VBLANK_VECTOR = 0x40
TIMER_VECTOR = 0x50
LCDSTAT_VECTOR = 0x48

BIOS_END = 0xff
ROM_BEGIN = 0x100
ROM_END = 0x7fff
ROM_BANK_0_END = 0x3fff
ROM_BANK_N_BEGIN = 0x4000

EXTERNAL_RAM_BEGIN = 0xa000
EXTERNAL_RAM_END = 0xbfff
WORKING_RAM_BEGIN = 0xc000
WORKING_RAM_END = 0xdfff
MEMORY_MAPPED_IO_BEGIN = 0xff00
MEMORY_MAPPED_IO_END = 0xff7f
ZERO_PAGE_BEGIN = 0xff80
ZERO_PAGE_END = 0xfffe
INTERRUPT_ENABLE_REGISTER = 0xffff

VRAM_BEGIN = 0x8000
VRAM_END = 0x9fff
OAM_BEGIN = 0xfe00
OAM_END = 0xfe9f

class MemoryBus:
    memory = [0x00] * (0xFFFF +1)

    def load_rom(self, rom):
        if(len(rom) > (ROM_END + 1)):
            raise "ROM SIZE INVALID"

        for i, rom_byte in enumerate(rom):
            self.memory[i] = rom_byte

    def read_byte(self, addr):
        return self.memory[addr] & 0xFF
    
    def write_byte(self, addr, value):
        self.memory[addr] = value & 0xFF
