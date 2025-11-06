from emulator.core.motherboard import *
from emulator.periferials.joypad import *
from emulator.periferials.screeen import *
from emulator.periferials.serial import *
import pygame
import time


class Gameboy:
    
    def __init__(self, serial=None):
        is_server = True if serial == 'server' else False
        self.screen = Screen()
        self.joypad = Joypad()
        self.network = MockNetAdapter() if serial is None else SimpleNetworkAdapter()
        self.network.start()
        self.motherboard = Motherboard(self.screen, self.joypad, self.network)

        self.cycles = 0
        self.time_debit = 0
        self.start_time = 0
        self.sync_cycles = 17556 * 2
        self.sync_time = (self.sync_cycles / 1e6) - 0.005

    def sync_clock(self):
        if self.cycles >= self.sync_cycles:
            self.cycles = self.cycles - self.sync_cycles
            if not self.joypad.speed_up:
                end_time = time.perf_counter()
                elapsed_time = end_time - self.start_time + self.time_debit
                if elapsed_time < self.sync_time:
                    self.sleep_kernel(self.sync_time - elapsed_time)
                    self.time_debit = 0
                else:
                    diff = elapsed_time - self.sync_time
                    self.time_debit = diff if diff < self.sync_time else 0

            self.start_time = time.perf_counter()

    def sleep_kernel(self, sleep_time):
        if sleep_time < 0.01:
            return
        time.sleep(sleep_time)


    def sleep_cpu(self, sleep_time):
        sleep_time_ns = sleep_time * 1e9
        start = time.perf_counter_ns()
        end = time.perf_counter_ns()
        count = 0
        while end - start < sleep_time_ns:
            count += 1 * 10 * 10 / 10 * 5
            count += 1 * 10 * 10 / 10 * 5
            count += 1 * 10 * 10 / 10 * 5
            end = time.perf_counter_ns()


    def play(self, cartridge:Cartridge):
        self.motherboard.insert_cartridge(cartridge)
        self.cartridge = cartridge
        running = True
        count = 0

        run_cycle = self.motherboard.run_cycle
        while running:
            self.sync_clock()
            count += 1
            if count % 1000 == 0: 
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        cartridge.save_game()
                        self.network.stop()
                        running = False
                    
                    if event.type == pygame.KEYDOWN:
                        self.joypad.update()
                        self.joypad.key_pressed = True
                    
                    if event.type == pygame.KEYUP:
                        self.joypad.update()
            
            self.cycles += run_cycle()
            
                



