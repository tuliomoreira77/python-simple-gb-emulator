import pygame

SCREEN_WIDTH = 160
SCREEN_LENGHT = 144
SCALE = 2
SCALED_SIZE = (SCREEN_WIDTH * SCALE, SCREEN_LENGHT * SCALE)


class MockScreen:
    def draw_line(self, position_y, pixels):
        pass

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