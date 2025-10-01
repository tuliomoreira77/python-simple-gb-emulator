from bus import *
from alu import *
from ppu import *
from cpu import *
from cpu_v2 import *

class Motherboard:

    def __init__(self, game_rom):
        self.memory_bus = MemoryBus()
        self.ppu = PPU(self.memory_bus)
        self.cpu = CPU_V2(self.memory_bus, self.ppu)
        #self.cpu = CPU(self.memory_bus, self.ppu)

        self.memory_bus.load_rom(game_rom)