import pygame

class MockJoypad:
    key_pressed = False
    
    def get_d_pad(self):
        return 0b1111
    
    def get_buttons(self):
        return 0b1111
    

class Joypad:
    key_pressed = False
    speed_up = False
    link_cable = False

    def __init__(self):
        self.d_pad = 0b1111
        self.buttons = 0b1111
        

    def update(self, keys):
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

    
    def get_d_pad(self):
        return self.d_pad

    def get_buttons(self):
        return self.buttons