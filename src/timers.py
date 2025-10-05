from bus import *

class GameboyTimer:
    
    def __init__(self, memory_bus:MemoryBus):
        self.memory_bus = memory_bus