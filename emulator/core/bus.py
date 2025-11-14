from emulator.core.calculator import *
from emulator.core.cartridge import *
from emulator.periferials.serial import *
from emulator.periferials.joypad import *
import array as arr

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
ROM_BANK_N_END = 0x7FFF

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
JOYPAD = 0xFF00
DMA = 0xFF46

SB = 0xFF01
SC = 0xFF02


class MemoryBus:
    calculator = Calculator()
    memory = arr.array('I', [0x00] * (0xFFFF +1))
    allow_write_vram = True
    cartridge:Cartridge = None

    def __init__(self, joypad:Joypad, serial_port:SimpleNetworkAdapter):
        self.joypad = joypad
        self.serial_port = serial_port
        self.serial_port.register_incoming_handler(self.wire_incoming_serial)

    def insert_cartridge(self, cartridge:Cartridge):
        self.cartridge = cartridge

    def read_byte(self, addr):
        if addr >= 0 and addr <= ROM_BANK_N_END:
            return self.cartridge.read_rom(addr)
        
        if addr >= EXTERNAL_RAM_BEGIN and addr <= EXTERNAL_RAM_END:
            return self.cartridge.read_ram(addr)

        if addr == JOYPAD:
            return self.wire_joypad()
        
        return self.memory[addr]
    
    def write_byte(self, addr, value):
        if addr >= 0x8000:
            if(addr == TIMER_DIV) :
                self.memory[addr] = 0x00
                return

            if addr >= EXTERNAL_RAM_BEGIN and addr <= EXTERNAL_RAM_END:
                self.cartridge.write_ram(addr, value)
                return
            
            if addr == DMA:
                self.dma(value)

            if addr == SC and (value == 0x81 or value == 0x80):
                self.wire_outcome_serial(value)
            
            self.memory[addr] = value & 0xFF
            return

        if addr < 0x2000:
            return

        if addr < 0x4000:
            self.cartridge.select_rom(value)
            return
        
        if addr < 0x6000:
            self.cartridge.select_ram(value)
            return 

        if addr < 0x8000:
            self.cartridge.select_extra(value)
            return

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

    def request_joypad_interrupt(self):
        interrupt_request = self.memory[INTERRUPT_FLAG]
        interrupt_request = self.calculator.set_bit(interrupt_request, 4)
        self.memory[INTERRUPT_FLAG] = interrupt_request

    def request_serial_interrupt(self):
        interrupt_request = self.memory[INTERRUPT_FLAG]
        interrupt_request = self.calculator.set_bit(interrupt_request, 3)
        self.memory[INTERRUPT_FLAG] = interrupt_request

    def clear_interruption_request(self, interrupt):
        interrupt_request = self.memory[INTERRUPT_FLAG]
        interrupt_request = self.calculator.reset_bit(interrupt_request, interrupt)
        self.memory[INTERRUPT_FLAG] = interrupt_request

    def wire_joypad(self):
        j_register = self.memory[JOYPAD]
        selector = j_register & 0b110000
        d_pad = self.joypad.get_d_pad()
        buttons = self.joypad.get_buttons()

        if selector == 48:
            return 0x3F
        if selector == 32:
            return j_register | d_pad
        if selector == 16:
            return j_register | buttons
    
    def wire_outcome_serial(self, value):
        self.memory[SC] = value
        self.serial_port.send_byte(self.memory[SB])
        
    def wire_incoming_serial(self, value):
        serial_control = self.memory[SC]
        if self.calculator.verify_bit(serial_control, 7):
            self.memory[SB] = value & 0xFF
            self.memory[SC] = self.calculator.reset_bit(serial_control, 7)
            self.request_serial_interrupt()
        
    def dma(self, addr):
        base_addr = addr << 8
        base_oam = OAM_BEGIN
        read_byte = self.read_byte
        for i in range (160):
            self.memory[base_oam] = read_byte(base_addr)
            base_addr += 1
            base_oam += 1
