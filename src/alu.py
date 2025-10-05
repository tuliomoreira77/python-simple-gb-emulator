class ALU:
    overflow = False

    def add_u8(self, a, b):
        self.overflow = False
        result = (a & 0xFF) + (b & 0xFF)
        self.overflow = result > 0xFF
        return result & 0xFF
    
    def add_u16(self, a, b):
        self.overflow = False
        result = (a & 0xFFFF) + (b & 0xFFFF)
        self.overflow = result > 0xFFFF
        return result & 0xFFFF
    
    def add_as_sig(self, u16, u8):
        self.overflow = False
        byte = self.to_signed(u8)
        return self.add_u16(u16, byte)
    
    def sub_u8(self, a, b):
        self.overflow = False
        result = (a & 0xFF) - (b & 0xFF)
        if result < 0:
            self.overflow = True
            return (256 + result) & 0xFF
        else:
            self.overflow = False
            return result & 0xFF
    
    def sub_u16(self, a, b):
        self.overflow = False
        result = (a & 0xFFFF) - (b & 0xFFFF)
        if(result < 0):
            self.overflow = True
            return (result + 0xFFFF + 1) & 0xFFFF
        self.overflow = False
        return result & 0xFFFF
    
    def and_u8(self, a, b):
        self.overflow = False
        return (a & b) & 0xFF
    
    def or_u8(self, a, b):
        self.overflow = False
        return (a | b) & 0xFF
    
    def xor_u8(self, a, b):
        self.overflow = False
        return (a ^ b) & 0xFF
    
    def to_signed(self, u8):
        self.overflow = False
        byte = u8 & 0xFF
        if byte > 127:
            return byte - (255 + 1)
        return byte
    
    def rotate_left(self, operand, carry):
        self.overflow = False
        operand = operand << 1
        if operand > 0xFF:
            self.overflow = True
        operand = operand | carry
        return operand & 0xFF
    
    def rotate_left_carry(self, operand):
        self.overflow = False
        operand = operand << 1
        carry = 0x00
        if operand > 0xFF:
            carry = 0x01
            self.overflow = True
        operand = operand | carry
        return operand & 0xFF
    
    def rotate_right(self, operand, carry):
        overflow = operand & 0x01
        operand = operand >> 1
        self.overflow = True if overflow == 1 else False
        operand = operand | (carry << 7)
        return operand

    def rotate_right_carry(self, operand):
        overflow = operand & 0x01
        operand = operand >> 1
        self.overflow = True if overflow == 1 else False
        operand = operand | (overflow << 7)
        return operand

    def shift_right_logical(self, operand):
        overflow = operand & 0x01
        operand = operand >> 1
        self.overflow = True if overflow == 1 else False
        return operand
    
    def shift_right_a(self, operand):
        overflow = operand & 0x01
        bit_7 = operand & 0x80
        result = operand >> 1
        result = result | bit_7
        self.overflow = overflow == 1
        return result
        
    def shift_left_a(self, operand):
        overflow = (operand & 0x80) >> 7
        result = (operand << 1) & 0xFF
        self.overflow = True if overflow == 1 else False
        return result
    
    def swap_u8(self, operand):
        lower = operand & 0xF
        upper = operand >> 4
        return (lower << 4) | upper
    
    def reset_bit(self, operand, bit):
        mask = ~(0x01 << bit)
        return (operand & mask) & 0xff
    
    def set_bit(self, operand, bit):
        mask = (0x01 << bit)
        return (operand | mask) & 0xff
    
    def verify_overflow(self, a, b, bit):
        mask = ((0xFFFF << bit + 1) ^ 0xFFFF) & 0xFFFF
        return True if ((a & mask) + (b & mask) > mask) else False
    
    def verify_borrow(self, a, b, bit):
        mask = ((0xFFFF << bit + 1) ^ 0xFFFF) & 0xFFFF
        return b & mask > a & mask
    
    def verify_bit(self, a, bit):
        return True if ((a >> bit) & 0x1 == 1) else False
    
    def not_u8(self, a):
        return ~a & 0xFF
