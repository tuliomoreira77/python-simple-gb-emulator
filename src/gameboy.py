from motherboard import *
import multiprocessing
import pygame
import time

SCREEN_WIDTH = 160
SCREEN_LENGHT = 144

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
    white = (255,255,255)
    black = (0, 0, 0)
    grey_1 = (85, 85, 85)
    grey_2 = (170, 170, 170)

    palette = [white, grey_2, grey_1, black]

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_LENGHT))
        self.screen.fill(self.black)
        pygame.display.update()

    def draw_line(self, position_y, pixels):
        pixel_array = pygame.PixelArray(self.screen)
        for i in range(SCREEN_WIDTH):
            pixel_array[i, position_y] = self.palette[pixels[i]]
        pixel_array.close() 
        update_rect = pygame.Rect(0,position_y, SCREEN_WIDTH ,1)
        pygame.display.update(update_rect)


class Joypad:

    key_pressed = False
    
    def get_d_pad(self):
        d_pad = 0b1111
        keys=pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            d_pad = d_pad & 0b0111
        if keys[pygame.K_UP]:
            d_pad = d_pad & 0b1011
        if keys[pygame.K_LEFT]:
            d_pad = d_pad & 0b1101
        if keys[pygame.K_RIGHT]:
            d_pad = d_pad & 0b0110

        return d_pad

    def get_buttons(self):
        buttons = 0b1111
        keys=pygame.key.get_pressed()
        if keys[pygame.K_RETURN ]:
            buttons = buttons & 0b0111
        if keys[pygame.K_SPACE]:
            buttons = buttons & 0b1011
        if keys[pygame.K_a]:
            buttons = buttons & 0b1101
        if keys[pygame.K_x]:
            buttons = buttons & 0b1110
        return buttons


class Gameboy:
    
    def __init__(self):
        self.screen = Screen()
        self.joypad = Joypad()
        self.motherboard = Motherboard(self.screen, self.joypad)

    def play(self, cartridge:Cartridge):
        self.motherboard.insert_cartridge(cartridge)
        running = True
        start_time = time.perf_counter()
        count = 0

        run_cycle = self.motherboard.run_cycle
        get_event = pygame.event.get
        while running:
            count += 1
            for event in get_event():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    self.joypad.key_pressed = True
        
            run_cycle()

            if count % 100000 == 0:
                end_time = time.perf_counter()
                elapsed_time = end_time - start_time
                print(f"Execution time for 100K: {elapsed_time:.4f} seconds")
                start_time = time.perf_counter()
            
                

def load_rom_file():
    with open('../roms/tetris.gb', 'rb') as f:
        binary_data = f.read()
        return binary_data

game = Cartridge(load_rom_file())
gameboy = Gameboy()
gameboy.play(game)


