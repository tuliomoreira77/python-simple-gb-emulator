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

LCD_Y = 0xFF44
LCD_YC = 0xFF45
LCD_STAT = 0xFF41
LCD_CONTROL = 0xFF40

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
        update_rect = pygame.Rect(0,position_y,256,1)
        pygame.display.update(update_rect)

class PPU:
    cycles = 0
    line_max_cycles = 456
    mode_0_cycles = 80
    mode_1_cycles = 172
    mode_2_cycles = 204
    mode_3_cycles = 4560


    tile_line_offset = 0
    tile_map_offset = 0
    line_rendered = 0

    actual_mode = 'MODE_2'

    total_pixels = 256
    grid_size = 32
    
    calculator = Calculator()

    def __init__(self, memory_bus:MemoryBus):
        self.screen = Screen()
        self.memory_bus = memory_bus

    def step(self, cycles):
        self.cycles += cycles

        lcd_control = self.get_lcd_control()
        new_mode = self.get_scanline_mode()
        changed = self.actual_mode != new_mode
        if changed:
            self.actual_mode = new_mode
            self.update_stat()

        if self.actual_mode == 'MODE_1' and changed:
            self.memory_bus.request_vblank_interrupt()

        if self.actual_mode == 'MODE_2' and changed:
            pass
        
        if self.actual_mode == 'MODE_3' and changed and lcd_control['LCD_ENABLE'] and lcd_control['BG_W_ENABLE']:
            self.render_line(self.tile_line_offset, self.tile_map_offset)
            self.tile_line_offset += 1
            if self.tile_line_offset == 8:
                self.tile_line_offset = 0
                self.tile_map_offset += 1
                if self.tile_map_offset == 32:
                    self.tile_map_offset = 0
        
        if self.actual_mode == 'MODE_0' and changed:
            pass
        
        if self.cycles >= 456:
            self.update_stat()
            self.update_y_coordinate()
            self.line_rendered += 1
            if self.line_rendered > 153:
                self.line_rendered = 0

            self.cycles = self.cycles % 456
        
    def get_scanline_mode(self):
        if self.line_rendered > 143:
            return 'MODE_1'
        
        if self.cycles < 80:
            return 'MODE_2'
        
        if self.cycles >= 80 and self.cycles < 256:
            return 'MODE_3'

        if self.cycles >= 256 and self.cycles < 456:
            return 'MODE_0'

    def render_line(self, tile_line_offset, tile_map_offset):
        pixel_line = []
        for i in range(32):
            tile_map_addr = (TILE_MAP_1_START + i) + (tile_map_offset * 32)
            tile_index = self.memory_bus.read_byte(tile_map_addr)
            tile_addr = self.tile_add_resolver(tile_index, False)
            pixels = self.read_tile_line(tile_addr, tile_line_offset)
            pixel_line.extend(pixels)

        self.screen.draw_line((tile_map_offset * 8) + tile_line_offset, pixel_line)

    def tile_add_resolver(self, tile_index, signed):
        return (tile_index * 16) + TILE_DATA_START

    def read_tile_line(self, tile_addr, line_index):
        line_addr = tile_addr + (line_index * 2)
        least_byte_addr = self.memory_bus.read_byte(line_addr)
        most_byte_addr = self.memory_bus.read_byte(line_addr + 1)

        pixels = [0x0] * 8
        mask = 0b10000000
        for i in range(8):
            most_bit = (most_byte_addr & mask) >> 7-i
            least_bit = (least_byte_addr & mask) >> 7-i
            pixel = most_bit << 1 | least_bit
            pixels[i] = pixel
            mask = mask >> 1
        return pixels
    

    def update_y_coordinate(self):
        self.memory_bus.write_byte(LCD_Y, self.line_rendered)

    def update_stat(self):
        lyc = self.memory_bus.read_byte(LCD_YC)
        ly = self.memory_bus.read_byte(LCD_Y)

        mode_interrupt = 0x00
        mode_ind = 0x00
        match self.actual_mode:
            case 'MODE_0':
                mode_interrupt = 0xb1000
                mode_ind = 0
            case 'MODE_1':
                mode_interrupt = 0xb10000
                mode_ind = 1
            case 'MODE_2':
                mode_interrupt = 0xb100000
                mode_ind = 2
            case 'MODE_3':
                mode_ind = 3

        ly_lyc_i = 0xb1000000 if lyc == ly else 0x0
        ly_lyc = 0xb100 if lyc == ly else 0x0

        stat = ly_lyc_i | mode_interrupt | ly_lyc | mode_ind
        self.memory_bus.write_byte(LCD_Y, self.line_rendered)
        self.memory_bus.write_byte(LCD_STAT, stat)
        self.memory_bus.request_stat_interrupt()

    def get_lcd_control(self):
        lcd_control_register = self.memory_bus.read_byte(LCD_CONTROL)
        return {
            'LCD_ENABLE': self.calculator.verify_bit(lcd_control_register, 7),
            'W_TILE_MAP': self.calculator.verify_bit(lcd_control_register, 6),
            'WINDOW_ENABLE': self.calculator.verify_bit(lcd_control_register, 5),
            'BG_W_TILE_MAP': self.calculator.verify_bit(lcd_control_register, 4),
            'BG_TILE_MAP': self.calculator.verify_bit(lcd_control_register, 3),
            'OBJ_SIZE': self.calculator.verify_bit(lcd_control_register, 2),
            'OBJ_ENABLE': self.calculator.verify_bit(lcd_control_register, 1),
            'BG_W_ENABLE': self.calculator.verify_bit(lcd_control_register, 0),
        }

