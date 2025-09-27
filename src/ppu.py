import pygame
from bus import *

SCREEN_WIDTH = 256
SCREEN_LENGHT = 256

TILE_MAP_1_START = 0x9800
TILE_MAP_1_END = 0x9BFF
TILE_MAP_2_START = 0x9C00
TILE_MAP_2_END = 0x9FFF

TILE_DATA_START = 0x8000
TILE_DATA_END = 0x97FF

class Screen:
    white = (255,255,255)
    black = (0, 0, 0)
    grey_1 = (85, 85, 85)
    grey_2 = (170, 170, 170)

    palette = [black, grey_1, grey_2, white]

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_LENGHT))

        self.screen.fill((0, 0, 0))
        self.screen.set_at((100, 100), self.palette[3])

        pygame.display.flip()

    def draw_line(self, position_y, pixels):
        for i in range(SCREEN_WIDTH):
            self.screen.set_at((i, position_y), self.palette[pixels[i]])

        pygame.display.flip()


## steps to render BG
## go to fist line of  tilemap and find first tile
## render first 8 pixel it will be encoded in two bytes, the first byte is the least bit of each pixel and the second byte is the most bit
## like 1100 1011   1101 1001 -> 11 11 00 10 11 00 10 11
## go to tile map and find next tile
## repeat until end of line
## go to fist line of tilemap again and find first tile
## repeat this for 8 lines
## go to second line of tilemap 
## and so on

class PPU:
    horizontal_pixel = 0x00
    vertical_pixel = 0x00
    total_pixels = 256
    grid_size = 32
    

    def __init__(self, memory_bus:MemoryBus):
        self.screen = Screen()
        self.memory_bus = memory_bus

    def basic_render(self):
        tile_map_addr = TILE_MAP_1_START
        for k in range (32):
            for j in range(8):
                pixel_line = []
                for i in range(32):
                    tile_map_addr = (TILE_MAP_1_START + i) + (k * 32)
                    tile_index = self.memory_bus.read_byte(tile_map_addr)
                    tile_addr = self.tile_add_resolver(tile_index, False)
                    pixels = self.read_tile_line(tile_addr, j)
                    pixel_line.extend(pixels)

                self.screen.draw_line((k * 32) + j, pixel_line)

        

    def tile_add_resolver(self, tile_index, signed):
        return (tile_index * 16) + TILE_DATA_START

    def read_tile_line(self, tile_addr, line_index):
        line_addr = tile_addr + (line_index * 2)
        least_byte_addr = self.memory_bus.read_byte(line_addr)
        most_byte_addr = self.memory_bus.read_byte(line_addr + 1)

        pixels = [0x0] * 8
        mask = 0b10000000
        for i in range(8):
            pixel = ((most_byte_addr & mask) >> 6) | (least_byte_addr & mask)
            pixels[i] = pixel
        return pixels