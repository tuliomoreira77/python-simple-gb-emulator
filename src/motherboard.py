from bus import *
from alu import *
from ppu import *
from cpu_v2 import *

class VirtualClock:
    clock_cycle = 0

class Motherboard:

    def __init__(self, game_rom):
        self.memory_bus = MemoryBus()
        self.ppu = PPU(self.memory_bus)
        self.cpu = CPU_V2(self.memory_bus)

        self.memory_bus.load_rom(game_rom)

    def run_cycles(self, cycles):
        count = 0
        while count < cycles:
            self.cpu.execute_step()

            if count % 100000 == 0:
                self.ppu.basic_render()

            count += 1
