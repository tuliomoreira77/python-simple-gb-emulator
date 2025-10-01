


class Registers:
    _a = 0x00
    _b = 0x00
    _c = 0x00
    _d = 0x00
    _e = 0x00
    _h = 0x00
    _l = 0x00

    zero:bool = False
    negative:bool = False
    half_carry:bool = False
    carry:bool = False

    def __init__(self):    
        self._get_8_map = {
            'A': lambda : self._a,
            'B': lambda : self._b,
            'C': lambda : self._c,
            'D': lambda : self._d,
            'E': lambda : self._e,
            'H': lambda : self._h,
            'L': lambda : self._l,
            'F': lambda : self.get_f()
        }

        self._set_8_map = {
            'A': self.set_a,
            'B': self.set_b,
            'C': self.set_c,
            'D': self.set_d,
            'E': self.set_e,
            'H': self.set_h,
            'L': self.set_l,
            'F': self.set_f
        }

        self._get_16_map = {
            'BC': self.get_bc,
            'DE': self.get_de,
            'HL': self.get_hl,
            'AF': self.get_af
        }

        self._set_16_map = {
            'BC': self.set_bc,
            'DE': self.set_de,
            'HL': self.set_hl,
            'AF': self.set_af
        }

    def get_a(self):
        return self._a 
    
    def set_a(self, value):
        self._a = value

    def get_b(self):
        return self._b 
    
    def set_b(self, value):
        self._b = value

    def get_c(self):
        return self._c
    
    def set_c(self, value):
        self._c = value
    
    def get_d(self):
        return self._d 
    
    def set_d(self, value):
        self._d = value

    def get_e(self):
        return self._e 
    
    def set_e(self, value):
        self._e = value

    def get_h(self):
        return self._h 
    
    def set_h(self, value):
        self._h = value

    def get_l(self):
        return self._l 
    
    def set_l(self, value):
        self._l = value

    def get_f(self):
        z = 0x1 if self.zero else 0x0
        n = 0x1 if self.negative else 0x0
        h = 0x1 if self.half_carry else 0x0
        c = 0x1 if self.carry else 0x0
        return z << 7 | n << 6 | h << 5 | c << 4
    
    def set_f(self, value):
        self.zero = ((value & 0b10000000) >> 7) == 0x1
        self.negative = ((value & 0b01000000) >> 6) == 0x1
        self.half_carry = ((value & 0b00100000) >> 5) == 0x1
        self.carry = ((value & 0b00010000) >> 4) == 0x1

    def get_hl(self):
        return (self._h << 8) | (self._l)
    
    def get_bc(self):
        return (self._b << 8) | (self._c)
    
    def get_de(self):
        return (self._d << 8) | (self._e)
    
    def get_af(self):
        return (self._a << 8) | self.get_f()
    
    def set_hl(self, value):
        self._h = value >> 8
        self._l = value & 0xFF

    def set_bc(self, value):
        self._b = value >> 8
        self._c = value & 0xFF

    def set_de(self, value):
        self._d = value >> 8
        self._e = value & 0xFF

    def set_af(self, value):
        self._a = value >> 8
        self.set_f(value & 0xFF)

    def get_8_from_id(self, id):
        get_func = self._get_8_map[id]
        return get_func()
    
    def set_8_from_id(self, id, value):
        set_func = self._set_8_map[id]
        set_func(value)

    def get_16_from_id(self, id):
        get_func = self._get_16_map[id]
        return get_func()

    def set_16_from_id(self, id, value):
        set_func = self._set_16_map[id]
        set_func(value)