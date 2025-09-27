class ALU:
    overflow = False

    def add_u8(self, a, b):
        result = (a & 0xFF) + (b & 0xFF)
        self.overflow = result > 0xFF
        return result & 0xFF
    
    def add_u16(self, a, b):
        result = (a & 0xFFFF) + (b & 0xFFFF)
        self.overflow = result > 0xFFFF
        return result & 0xFFFF
    
    def add_as_sig(self, u16, u8):
        byte = u8 & 0xFF
        if byte > 127:
            byte = byte - (255 + 1)
        return (u16 + byte) & 0xFFFF
    
    def sub_u8(self, a, b):
        result = ((~(a & 0xFF)) + 1) + (b & 0xFF)
        if(result > 0xFF):
            return result & 0xFF
        self.overflow = True
        result = ~(result & 0xFF) + 1
        return result & 0xFF
    
    def sub_u16(self, a, b):
        result = ((~(a & 0xFFFF)) + 1) + (b & 0xFFFF)
        if(result > 0xFFFF):
            return result & 0xFFFF
        self.overflow = True
        result = ~(result & 0xFFFF) + 1
        return result & 0xFFFF
    
    def and_u8(self, a, b):
        return (a & b) & 0xFF
    
    def or_u8(self, a, b):
        return (a | b) & 0xFF
    
    def to_signed(self, u8):
        byte = u8 & 0xFF
        if byte > 127:
            return byte - (255 + 1)
        return byte
    
    def rotate_left(self, operand, carry):
        operand = operand << 1
        if operand > 0xFF:
            self.overflow = True
        operand = operand | carry
        return operand & 0xFF
    
    def rotate_left_carry(self, operand):
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

    def rotate_right_carry(self, operand):
        overflow = operand & 0x01
        operand = operand >> 1
        self.overflow = True if overflow == 1 else False
        operand = operand | (overflow << 7)
