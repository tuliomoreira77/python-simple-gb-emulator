from bus import *
from calculator import *
from ppu import *
from cpu_v2 import *
from timers import *
from cartridge import *
import time

class Motherboard:
    clock_cycle = 0
    start_time = 0

    def __init__(self, screen, joypad):
        self.memory_bus = MemoryBus(joypad)
        self.ppu = PPU(self.memory_bus, screen)
        self.cpu = CPU_V2(self.memory_bus)
        self.timer = GameboyTimer(self.memory_bus)
        self.joypad = joypad
        self.memory_bus.write_byte(JOYPAD, 0x3F)

    def insert_cartridge(self, cartridge:Cartridge):
        self.memory_bus.insert_cartridge(cartridge)

    def sync_clock(self):
        if self.clock_cycle >= 10000:
            end_time = time.perf_counter()
            elapsed_time = end_time - self.start_time
            self.start_time = end_time
            self.clock_cycle = self.clock_cycle - 10000
            if elapsed_time < 0.007:
                time.sleep(0.007 - elapsed_time)

    def run_cycle(self):
        try:
            self.sync_clock()

            if self.joypad.key_pressed:
                self.memory_bus.request_joypad_interrupt()
                self.joypad.key_pressed = False

            m_cycles = self.cpu.execute_step()
            global_cycles = m_cycles * 4
            self.timer.step(global_cycles)
            self.ppu.step(global_cycles)
            self.clock_cycle += m_cycles
        except Exception as e:
            self.cpu.print_debug()
            raise e
        
