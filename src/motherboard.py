from bus import *
from calculator import *
from ppu import *
from cpu_v2 import *
from timers import *
import time 

class Motherboard:
    clock_cycle = 0

    def __init__(self, game_rom):
        self.memory_bus = MemoryBus()
        self.ppu = PPU(self.memory_bus)
        self.cpu = CPU_V2(self.memory_bus)
        self.timer = GameboyTimer(self.memory_bus)

        self.memory_bus.load_rom(game_rom)

    def run_cycles(self, cycles):
        count = 0
        while count < cycles:
            m_cycles = self.cpu.execute_step()
            global_cycles = m_cycles * 4
            self.timer.step(global_cycles)
            self.clock_cycle += global_cycles

            if count % 69905 == 0:
                self.ppu.basic_render()
            count += 1

            ##time.sleep(0.0000002384185791015625)
