from bus import *

TILE_MAP_1_START = 0x9800
TILE_MAP_1_END = 0x9BFF
TILE_MAP_2_START = 0x9C00
TILE_MAP_2_END = 0x9FFF

TILE_DATA_START = 0x8000
TILE_DATA_END = 0x97FF

OAM_START = 0xFE00

LCD_Y = 0xFF44
LCD_YC = 0xFF45
LCD_STAT = 0xFF41
LCD_CONTROL = 0xFF40


class OAMObject:
    y_position = 0x00
    x_position = 0x00
    tile_index = 0x00
    tile_line = 0x00
    extended_size = False
    attributes = 0x00
    pixels = [0x00] * 8

    def __init__(self, y, x, t, tl, a, extended_size):
        self.y_position = y
        self.x_position = x
        self.tile_index = t
        self.attributes = a
        self.tile_line = tl
        self.extended_size = extended_size


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
    
    oam_objects:list[OAMObject] = []
    calculator = Calculator()

    bg_pixel_buffer = [0x00] * 160
    obj_pixel_buffer = [0x00] * 160
    pixel_buffer = [0x00] * 160
    raw_lcd_control = 0x00
    decoded_lcd_control = {}

    render_next_frame = True

    def __init__(self, memory_bus:MemoryBus, screen):
        self.screen = screen
        self.memory_bus = memory_bus

    def step(self, cycles):
        self.cycles += cycles

        self.get_lcd_control()
        new_mode = self.get_scanline_mode()
        changed = self.actual_mode != new_mode
        if changed:
            self.actual_mode = new_mode
            self.update_stat()

        if self.actual_mode == 'MODE_1' and changed:
            self.render_next_frame = not self.render_next_frame
            self.memory_bus.request_vblank_interrupt()

        if self.actual_mode == 'MODE_2' and changed and self.render_next_frame:
            self.oam_objects = self.oam_scan((self.tile_map_offset * 8) + self.tile_line_offset)
            self.oam_fetch()
        
        if self.actual_mode == 'MODE_3' and changed and self.render_next_frame:
            pixel_bg_line = self.render_bg_line(self.tile_line_offset, self.tile_map_offset)
            pixel_obj_line = self.render_obj_line()

            for i in range(160):
                if pixel_obj_line[i] != 0:
                    self.pixel_buffer[i] = pixel_obj_line[i]
                else:
                    self.pixel_buffer[i] = pixel_bg_line[i]

            self.screen.draw_line((self.tile_map_offset * 8) + self.tile_line_offset, self.pixel_buffer)

            self.tile_line_offset += 1
            if self.tile_line_offset == 8:
                self.tile_line_offset = 0
                self.tile_map_offset += 1
                if self.tile_map_offset == 18: ## y_tiles_size
                    self.tile_map_offset = 0
        
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

    def render_bg_line(self, tile_line_offset, tile_map_offset):
        for i in range(20): ## x tile size
            tile_map_addr = (TILE_MAP_1_START + i) + (tile_map_offset * 32)
            tile_index = self.memory_bus.read_byte(tile_map_addr)
            tile_addr = self.tile_add_resolver(tile_index, False)
            pixels = self.read_tile_line(tile_addr, tile_line_offset)

            for p  in range(8):
                self.bg_pixel_buffer[p + i * 8] = pixels[p]

        return self.bg_pixel_buffer
    
    def render_obj_line(self):
        self.obj_pixel_buffer = [0x00] * 160
        for obj in self.oam_objects:
            for i in range(8):
                if obj.x_position >= 8 and obj.x_position < 168:
                    self.obj_pixel_buffer[(obj.x_position - 8) + i] = obj.pixels[i]
            
        return self.obj_pixel_buffer

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
    
    def oam_scan(self, line_index):
        lcd_control = self.memory_bus.read_byte(LCD_CONTROL)
        obj_extended = self.calculator.verify_bit(lcd_control, 2)
        addr = OAM_START
        oam_objects = []

        obj_size = 8
        if obj_extended:
            obj_size = 16

        for i in range(40):
            y = self.memory_bus.read_byte(addr)

            if line_index >= (y - 16) and line_index < (y - 16 + obj_size):
                x = self.memory_bus.read_byte(addr + 1)
                t = self.memory_bus.read_byte(addr + 2)
                a = self.memory_bus.read_byte(addr + 3)
                tl = line_index - (y - 16)
                oam_objects.append(OAMObject(y,x,t,tl,a, obj_extended))
            addr += 4
        return oam_objects
    
    def oam_fetch(self):
        for obj in self.oam_objects:
            tile_line = obj.tile_line
            if obj.extended_size:
                if obj.tile_line >= 8:
                    tile_addr = self.tile_add_resolver(obj.tile_index | 0x01, False)
                    tile_line -= 8
                else:
                    tile_addr = self.tile_add_resolver(obj.tile_index & 0xFE, False)
            else:
                tile_addr = self.tile_add_resolver(obj.tile_index, False)

            tile_line = self.read_tile_line(tile_addr, tile_line)
            obj.pixels = tile_line

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

        if self.raw_lcd_control != lcd_control_register:
            self.raw_lcd_control = lcd_control_register
            self.decoded_lcd_control = {
            'LCD_ENABLE': self.calculator.verify_bit(lcd_control_register, 7),
            'W_TILE_MAP': self.calculator.verify_bit(lcd_control_register, 6),
            'WINDOW_ENABLE': self.calculator.verify_bit(lcd_control_register, 5),
            'BG_W_TILE_MAP': self.calculator.verify_bit(lcd_control_register, 4),
            'BG_TILE_MAP': self.calculator.verify_bit(lcd_control_register, 3),
            'OBJ_SIZE': self.calculator.verify_bit(lcd_control_register, 2),
            'OBJ_ENABLE': self.calculator.verify_bit(lcd_control_register, 1),
            'BG_W_ENABLE': self.calculator.verify_bit(lcd_control_register, 0),
        }

