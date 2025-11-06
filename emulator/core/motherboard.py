from emulator.core.bus import *
from emulator.core.calculator import *
from emulator.core.ppu import *
from emulator.core.cpu_v2 import *
from emulator.core.timers import *
from emulator.core.cartridge import *

class Motherboard:
    clock_cycle = 0
    start_time = 0

    def __init__(self, screen, joypad, network_adapter):
        self.serial_port = network_adapter
        self.joypad = joypad
        self.memory_bus = MemoryBus(joypad, self.serial_port)
        self.ppu = PPU(self.memory_bus, screen)
        self.cpu = CPU_V2(self.memory_bus)
        self.timer = GameboyTimer(self.memory_bus)
        self.memory_bus.write_byte(JOYPAD, 0x3F)

    def insert_cartridge(self, cartridge:Cartridge):
        self.memory_bus.insert_cartridge(cartridge)

    def run_cycle(self):
        try:
            if self.joypad.key_pressed:
                self.memory_bus.request_joypad_interrupt()
                self.joypad.key_pressed = False

            m_cycles = self.cpu.execute_step()
            global_cycles = m_cycles * 4
            self.timer.step(global_cycles)
            self.ppu.step(global_cycles)
            self.clock_cycle += m_cycles

            return m_cycles
        except Exception as e:
            self.cpu.print_debug()
            raise e
        
