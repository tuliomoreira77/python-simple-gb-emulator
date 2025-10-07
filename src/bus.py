from calculator import *

VBLANK_VECTOR = 0x40
TIMER_VECTOR = 0x50
LCDSTAT_VECTOR = 0x48
SERIAL_VECTOR = 0x58
JOYPAD_VECTOR = 0x60

INTERRUPT_VECTOR_MAP = {
    0: VBLANK_VECTOR,
    1: LCDSTAT_VECTOR,
    2: TIMER_VECTOR,
    3: SERIAL_VECTOR,
    4: JOYPAD_VECTOR
}

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
INTERRUPT_FLAG = 0xFF0F

VRAM_BEGIN = 0x8000
VRAM_END = 0x9fff
OAM_BEGIN = 0xfe00
OAM_END = 0xfe9f

TIMER_DIV = 0xFF04
TIMER_COUNTER = 0xFF05
TIMER_MODULO = 0xFF06
TIMER_CONTROL = 0xFF07

LCD_CONTROL = 0xFF40


class MemoryBus:
    calculator = Calculator()
    memory = [0x00] * (0xFFFF +1)
    allow_write_vram = True

    def load_rom(self, rom):
        if(len(rom) > (ROM_END + 1)):
            raise "ROM SIZE INVALID" # pyright: ignore[reportGeneralTypeIssues]

        for i, rom_byte in enumerate(rom):
            self.memory[i] = rom_byte

    def read_byte(self, addr):
        return self.memory[addr] & 0xFF
    
    def write_byte(self, addr, value):
        if not self.allow_write_vram and addr >= VRAM_BEGIN and addr <= VRAM_END:
            return

        if(addr == TIMER_DIV) :
            self.memory[addr] = 0x00
            return
        
        self.memory[addr] = value & 0xFF

    def inc_timer_div(self):
        value = self.memory[TIMER_DIV]
        value = value + 1
        self.memory[TIMER_DIV] = value & 0xFF

    def inc_timer_counter(self):
        value = self.memory[TIMER_COUNTER]
        value = value + 1

        if value > 0xFF:
            self.request_timer_interrupt()
            value = self.memory[TIMER_MODULO]

        self.memory[TIMER_COUNTER] = value

    def request_timer_interrupt(self):
        interrupt_request = self.memory[INTERRUPT_FLAG]
        interrupt_request = self.calculator.set_bit(interrupt_request, 2)
        self.memory[INTERRUPT_FLAG] = interrupt_request

    def request_stat_interrupt(self):
        interrupt_request = self.memory[INTERRUPT_FLAG]
        interrupt_request = self.calculator.set_bit(interrupt_request, 1)
        self.memory[INTERRUPT_FLAG] = interrupt_request

    def request_vblank_interrupt(self):
        interrupt_request = self.memory[INTERRUPT_FLAG]
        interrupt_request = self.calculator.set_bit(interrupt_request, 0)
        self.memory[INTERRUPT_FLAG] = interrupt_request

    def block_vram(self):
        self.allow_write_vram = True

    def free_vram(self):
        self.allow_write_vram = True

