from emulator.core.motherboard import *
from emulator.periferials.joypad import *
from emulator.periferials.screeen import *
from emulator.periferials.serial import *
import time
import pygame


class Gameboy:
    
    def __init__(self):
        self.screen = Screen()
        self.joypad = Joypad()
        self.network = SimpleNetworkAdapter()
        self.motherboard = Motherboard(self.screen, self.joypad, self.network)

        self.cycles = 0
        self.time_debit = 0
        self.start_time = 0
        self.sync_cycles = 17556 * 2
        self.sync_time = (self.sync_cycles / 1e6) - 0.005

        self.speed_up = False
        self.link_cable = False

    def sync_clock(self):
        if self.cycles >= self.sync_cycles:
            self.cycles = self.cycles - self.sync_cycles
            if not self.speed_up:
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

    def connect_serial_link(self):
        if self.link_cable and not self.network.in_use:
            self.network.start()

        else:
            if not self.link_cable and self.network.in_use:
                self.network.stop()


    def play(self, cartridge:Cartridge):
        self.motherboard.insert_cartridge(cartridge)
        self.cartridge = cartridge
        running = True
        count = 0

        run_cycle = self.motherboard.run_cycle
        while running:
            count += 1
            self.sync_clock()
            self.connect_serial_link()
            if count % 1000 == 0: 
                count = 0
                for event in pygame.event.get():
                    keys = None
                    if event.type == pygame.QUIT:
                        cartridge.save_game()
                        self.network.stop()
                        running = False
                    
                    if event.type == pygame.KEYDOWN:
                        keys = pygame.key.get_pressed()
                        self.joypad.update(keys)
                        self.joypad.key_pressed = True
                    
                    if event.type == pygame.KEYUP:
                        keys = pygame.key.get_pressed()
                        self.joypad.update(keys)

                    if keys is not None:
                        if keys[pygame.K_LSHIFT]:
                            self.speed_up = not self.speed_up
                        if keys[pygame.K_s]:
                            print("Flushing save to hard disk...")
                            cartridge.save_game()
                        if keys[pygame.K_i]:
                            self.link_cable = True
                        if keys[pygame.K_p]:
                            self.link_cable = False
                            
            self.cycles += run_cycle()
            
                



