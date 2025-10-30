from motherboard import *
import pygame
import time

SCREEN_WIDTH = 160
SCREEN_LENGHT = 144
SCALE = 2
SCALED_SIZE = (SCREEN_WIDTH * SCALE, SCREEN_LENGHT * SCALE)

class MockScreen:
    def draw_line(self, position_y, pixels):
        pass

class MockJoypad:
    key_pressed = False
    
    def get_d_pad(self):
        return 0b1111
    
    def get_buttons(self):
        return 0b1111


class Screen:
    frame_buffer = bytearray(SCREEN_WIDTH * SCREEN_LENGHT * 3)
    white = (232, 252, 204)
    grey_2 = (172, 212, 144)
    grey_1 = (84, 140, 112)
    black = (20, 44, 56)
    

    palette = {
        0x00: white,
        0x01: grey_2,
        0x02: grey_1,
        0x03: black,
        0xF0: white,
        0xF1: grey_2,
        0xF2: grey_1,
        0xF3: black
    }

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Simple Gameboy")
        self.screen = pygame.display.set_mode(SCALED_SIZE)
        self.screen.fill(self.black)
        pygame.display.update()

    def draw_line(self, position_y, pixels):
        buffer = self.frame_buffer
        palete = self.palette

        offset_y = position_y * (SCREEN_WIDTH * 3)

        for x in range(SCREEN_WIDTH):
            r, g, b = palete[pixels[x]]
            offset_x = x * 3
            buffer[offset_x + offset_y] = r
            buffer[offset_x + offset_y + 1] = g
            buffer[offset_x + offset_y + 2] = b

        if position_y >= SCREEN_LENGHT-1:
            self.draw_frame()


    def draw_frame(self):
        surf = pygame.image.frombuffer(bytes(self.frame_buffer), (SCREEN_WIDTH, SCREEN_LENGHT), "RGB")
        scaled_surf = pygame.transform.scale(surf, SCALED_SIZE)
        self.screen.blit(scaled_surf, (0, 0))
        pygame.display.update()

class Joypad:
    key_pressed = False
    speed_up = False

    def __init__(self):
        self.d_pad = 0b1111
        self.buttons = 0b1111
        

    def update(self):
        keys = pygame.key.get_pressed()
        
        self.d_pad = 0b1111
        self.buttons = 0b1111

        d_pad = self.d_pad
        buttons = self.buttons

        if keys[pygame.K_DOWN]:
            self.d_pad = d_pad & 0b0111
        if keys[pygame.K_UP]:
            self.d_pad = d_pad & 0b1011
        if keys[pygame.K_LEFT]:
            self.d_pad = d_pad & 0b1101
        if keys[pygame.K_RIGHT]:
            self.d_pad = d_pad & 0b1110

        if keys[pygame.K_RETURN ]:
            self.buttons = buttons & 0b0111
        if keys[pygame.K_SPACE]:
            self.buttons = buttons & 0b1011
        if keys[pygame.K_a]:
            self.buttons = buttons & 0b1101
        if keys[pygame.K_x]:
            self.buttons = buttons & 0b1110

        if keys[pygame.K_LSHIFT]:
            self.speed_up = not self.speed_up


    
    def get_d_pad(self):
        return self.d_pad

    def get_buttons(self):
        return self.buttons


class Gameboy:
    
    def __init__(self):
        self.screen = Screen()
        self.joypad = Joypad()
        self.motherboard = Motherboard(self.screen, self.joypad)

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
                        running = False
                    
                    if event.type == pygame.KEYDOWN:
                        self.joypad.update()
                        self.joypad.key_pressed = True
                    
                    if event.type == pygame.KEYUP:
                        self.joypad.update()
            
            self.cycles += run_cycle()
            
                
file_name = 'tetris.gb'
def load_rom_file():
    with open('../roms/' + file_name, 'rb') as f:
        binary_data = f.read()
        return binary_data

game = Cartridge(load_rom_file(), file_name)
gameboy = Gameboy()
gameboy.play(game)


