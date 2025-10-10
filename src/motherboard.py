from bus import *
from calculator import *
from ppu import *
from cpu_v2 import *
from timers import *
from cartridge import *

class Motherboard:
    clock_cycle = 0
    d_pad = 0xF
    buttons = 0xF

    def __init__(self, screen, joypad):
        self.memory_bus = MemoryBus(joypad)
        self.ppu = PPU(self.memory_bus, screen)
        self.cpu = CPU_V2(self.memory_bus)
        self.timer = GameboyTimer(self.memory_bus)
        self.joypad = joypad
        self.memory_bus.write_byte(JOYPAD, 0x3F)

    def insert_cartridge(self, cartridge:Cartridge):
        self.memory_bus.load_rom(cartridge.game_rom)

    def run_cycle(self):
        try:
            if self.joypad.key_pressed:
                self.memory_bus.request_joypad_interrupt()
                self.joypad.key_pressed = False

            m_cycles = self.cpu.execute_step()
            global_cycles = m_cycles * 4
            ##self.timer.step(global_cycles)
            self.ppu.step(global_cycles)
            self.clock_cycle += global_cycles
        except Exception as e:
            self.cpu.print_debug()
            raise e
        
