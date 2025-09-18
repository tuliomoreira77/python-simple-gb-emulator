from bus import *
from instructions_dict import *
import time


class Flags:
    z = 0x1
    n = 0x0
    h = 0x1
    c = 0x1

    def reset(self):
        self.z = 0x0
        self.n = 0x0
        self.h = 0x0
        self.c = 0x0
    
    def set_zero(self):
        self.z = 0x1
    
    def set_carry(self):
        self.c = 0x1
    
    def set_sub(self):
        self.n = 0x1
    
    def set_half_carry(self):
        self.c = 0x1

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


class CPU:
    r_a = 0x01
    r_b = 0x00
    r_c = 0x13
    r_d = 0x00
    r_e = 0xd8
    r_f = 0xb0
    r_h = 0x01
    r_l = 0x4d
    flags = Flags()

    program_counter = 0x0100
    stack_pointer = 0xfffe
    interrupts_enabled = True
    is_halt = False

    clock_cycle = 0

    memory_bus = MemoryBus()
    alu = ALU()

    def __init__(self, game_rom):
        self.memory_bus.load_rom(game_rom)

    def basic_debug(self):
        print("Register E: {}".format(self.r_e))
        print("Flags z: {}".format(self.flags.z)) 
        print("Flags n: {}".format(self.flags.n)) 
        print("Flags h: {}".format(self.flags.h)) 
        print("Flags c: {}".format(self.flags.c)) 

    def execute(self):
        while(True):
            ##time.sleep(0.1)

            instruction = self.get_instruction()

            print(instruction.definition.name)
            
            self.ir_jump(instruction)
            self.ir_add_u8(instruction)
            self.ir_add_u16(instruction)
            self.ir_and_u8(instruction)
            self.ir_opr_sp(instruction)
            self.ir_call(instruction)
            self.ir_ret(instruction)
            self.ir_bit_u8(instruction)
            self.ir_complement(instruction)
            self.ir_compare(instruction)
            self.ir_interrupt(instruction)
            self.ir_dec(instruction)
            self.ir_inc(instruction)
            self.ir_load(instruction)
            self.ir_or(instruction)
            self.ir_rl(instruction)
            self.ir_rr(instruction)
            self.ir_sub_u8(instruction)

            ##self.basic_debug()

    def get_instruction(self):
        instruction = self.memory_bus.read_byte(self.program_counter)
        program_step = 1
        instruction_definition = None
        if instruction == 0xCB:
            instruction = self.memory_bus.read_byte(self.program_counter + program_step)
            program_step = program_step + 1
            instruction_definition = PREFIX_INSTRUCTION_DICT.get(instruction, None)
        else:
            instruction_definition = INSTRUCTION_DICT.get(instruction, None)

        if(instruction_definition is None):
            self.program_counter = self.program_counter + program_step
            return Instruction(INSTRUCTION_DICT[0x00], [])

        operands = [0x00] * instruction_definition.operands_number
        if instruction_definition.operands_number > 0:
            for i in range(instruction_definition.operands_number):
                operands[i] = self.memory_bus.read_byte(self.program_counter + program_step)
                program_step = program_step + 1

        instruction = Instruction(instruction_definition, operands)
        self.program_counter = self.program_counter + program_step
        self.clock_cycle = self.clock_cycle + instruction.definition.cycles

        return instruction
    
    def ir_jump(self, instruction:Instruction):
        if instruction.definition.name == 'JP_HL':
            addr = self.get_r_hl()
            jump_location = self.memory_bus.read_byte(addr)
            self.program_counter = jump_location

        if instruction.definition.name == 'JP_D16':
            addr = instruction.operands[1] << 8 | instruction.operands[0]
            self.program_counter = addr

        if instruction.definition.name == 'JP_NZ':
            if self.flags.z == 0:
                self.jump_conditional(instruction)

        if instruction.definition.name == 'JP_NC':
            if self.flags.c == 0:
                self.jump_conditional(instruction)

        if instruction.definition.name == 'JP_Z':
            if self.flags.z == 1:
                self.jump_conditional(instruction)

        if instruction.definition.name == 'JP_C':
            if self.flags.c == 1:
                self.jump_conditional(instruction)

        if instruction.definition.name == 'JPR_D16':
            next_addr = self.program_counter + 1
            addr = self.alu.add_as_sig(next_addr, instruction.operands[0])
            self.program_counter = addr

        if instruction.definition.name == 'JPR_NZ':
            if self.flags.z == 0:
                self.jump_conditional_relative(instruction)

        if instruction.definition.name == 'JPR_NC':
            if self.flags.c == 0:
                self.jump_conditional_relative(instruction)


        if instruction.definition.name == 'JPR_Z':
            if self.flags.z == 1:
                self.jump_conditional_relative(instruction)


        if instruction.definition.name == 'JPR_C':
            if self.flags.c == 1:
                self.jump_conditional_relative(instruction)


    def ir_call(self, instruction:Instruction):
        if instruction.definition.name == 'CALL_D16':
            self.call(instruction)
        if instruction.definition.name == 'CALL_NZ':
            if self.flags.z == 0:
                self.call(instruction)
                self.clock_cycle = self.clock_cycle + 3
        if instruction.definition.name == 'CALL_NC':
            if self.flags.c == 0:
                self.call(instruction)
                self.clock_cycle = self.clock_cycle + 3
        if instruction.definition.name == 'CALL_Z':
            if self.flags.z == 1:
                self.call(instruction)
                self.clock_cycle = self.clock_cycle + 3
        if instruction.definition.name == 'CALL_C':
            if self.flags.c == 1:
                self.call(instruction)
                self.clock_cycle = self.clock_cycle + 3

    def ir_ret(self, instruction:Instruction):
        if instruction.definition.name == 'RET_D16':
            self.ret(instruction)
        if instruction.definition.name == 'RET_NZ':
            if self.flags.z == 0:
                self.ret(instruction)
                self.clock_cycle = self.clock_cycle + 3
        if instruction.definition.name == 'RET_NC':
            if self.flags.c == 0:
                self.ret(instruction)
                self.clock_cycle = self.clock_cycle + 3
        if instruction.definition.name == 'RET_Z':
            if self.flags.z == 1:
                self.ret(instruction)
                self.clock_cycle = self.clock_cycle + 3
        if instruction.definition.name == 'RET_C':
            if self.flags.c == 1:
                self.ret(instruction)
                self.clock_cycle = self.clock_cycle + 3


    def ir_add_u8(self, instruction:Instruction):
        if instruction.definition.name == 'ADD_B':
            self.add_u8(self.r_b)
        if instruction.definition.name == 'ADD_C':
            self.add_u8(self.r_c)
        if instruction.definition.name == 'ADD_D':
            self.add_u8(self.r_d)
        if instruction.definition.name == 'ADD_E':
            self.add_u8(self.r_e)
        if instruction.definition.name == 'ADD_H':
            self.add_u8(self.r_h)
        if instruction.definition.name == 'ADD_L':
            self.add_u8(self.r_l)
        if instruction.definition.name == 'ADD_A':
            self.add_u8(self.r_a)
        if instruction.definition.name == 'ADD_D8':
            self.add_u8(instruction.operands[0])
        if instruction.definition.name == 'ADD_HL':
            addr = self.get_r_hl()
            operand = self.memory_bus.read_byte(addr)
            self.add_u8(operand)

        if instruction.definition.name == 'ADDC_B':
            self.add_u8(self.r_b, True)
        if instruction.definition.name == 'ADDC_C':
            self.add_u8(self.r_c, True)
        if instruction.definition.name == 'ADDC_D':
            self.add_u8(self.r_d, True)
        if instruction.definition.name == 'ADDC_E':
            self.add_u8(self.r_e, True)
        if instruction.definition.name == 'ADDC_H':
            self.add_u8(self.r_h, True)
        if instruction.definition.name == 'ADDC_L':
            self.add_u8(self.r_l, True)
        if instruction.definition.name == 'ADDC_A':
            self.add_u8(self.r_a, True)
        if instruction.definition.name == 'ADDC_D8':
            self.add_u8(instruction.operands[0], True)
        if instruction.definition.name == 'ADDC_HL':
            addr = self.get_r_hl()
            operand = self.memory_bus.read_byte(addr)
            self.add_u8(operand, True)

    def ir_add_u16(self, instruction:Instruction):
        if instruction.definition.name == 'ADDHL_BC':
            self.add_u16(self.get_r_bc)
        if instruction.definition.name == 'ADDHL_DE':
            self.add_u16(self.get_r_de)
        if instruction.definition.name == 'ADDHL_HL':
            self.add_u16(self.get_r_hl)
        if instruction.definition.name == 'ADDHL_SP':
            operand = self.memory_bus.read_byte(self.stack_pointer)
            self.add_u16(operand)

    def ir_sub_u8(self, instruction:Instruction):
        match instruction.definition.name:
            case 'SUB_B':
                self.sub_u8(self.r_b)
            case 'SUB_C':
                self.sub_u8(self.r_c)
            case 'SUB_D':
                self.sub_u8(self.r_d)
            case 'SUB_E':
                self.sub_u8(self.r_e)
            case 'SUB_H':
                self.sub_u8(self.r_h)
            case 'SUB_L':
                self.sub_u8(self.r_l)
            case 'SUB_A':
                self.sub_u8(self.r_a)
            case 'SUB_HL':
                operand = self.memory_bus.read_byte(self.get_r_hl())
                self.sub_u8(operand)
            case 'SUB_D8':
                self.sub_u8(instruction.operands[0])

            case 'SUBC_B':
                self.sub_u8(self.r_b, True)
            case 'SUBC_C':
                self.sub_u8(self.r_c, True)
            case 'SUBC_D':
                self.sub_u8(self.r_d, True)
            case 'SUBC_E':
                self.sub_u8(self.r_e, True)
            case 'SUBC_H':
                self.sub_u8(self.r_h, True)
            case 'SUBC_L':
                self.sub_u8(self.r_l, True)
            case 'SUBC_A':
                self.sub_u8(self.r_a, True)
            case 'SUBC_HL':
                operand = self.memory_bus.read_byte(self.get_r_hl())
                self.sub_u8(operand, True)
            case 'SUBC_D8':
                self.sub_u8(instruction.operands[0], True)

    def ir_opr_sp(self, instruction:Instruction):
        match instruction.definition.name:
            case 'ADDSP_D8':
                operand = self.alu.to_signed(instruction.operands[0])
                new_sp = self.alu.add_as_sig(self.stack_pointer, instruction.operands[0])

                self.flags.reset()
                if ((self.stack_pointer & 0xF) + (operand & 0xF)) > 0xF:
                    self.flags.set_half_carry()
                if ((self.stack_pointer & 0xFF) + (operand & 0xFF)) > 0xFF:
                    self.flags.set_carry()

                self.stack_pointer = new_sp
            
            case 'PUSH_AF':
                self.stack_pointer = self.stack_pointer - 1
                self.memory_bus.write_byte(self.stack_pointer, self.r_a)
                self.stack_pointer = self.stack_pointer - 1
                self.memory_bus.write_byte(self.stack_pointer, self.r_f)
                self.flags.z = (self.r_f >> 7) & 0x01
                self.flags.n = (self.r_f >> 6) & 0x01
                self.flags.h = (self.r_f >> 5) & 0x01
                self.flags.c = (self.r_f >> 4) & 0x01

            case 'PUSH_BC':
                self.stack_pointer = self.stack_pointer - 1
                self.memory_bus.write_byte(self.stack_pointer, self.r_b)
                self.stack_pointer = self.stack_pointer - 1
                self.memory_bus.write_byte(self.stack_pointer, self.r_c)

            case 'PUSH_DE':
                self.stack_pointer = self.stack_pointer - 1
                self.memory_bus.write_byte(self.stack_pointer, self.r_d)
                self.stack_pointer = self.stack_pointer - 1
                self.memory_bus.write_byte(self.stack_pointer, self.r_e)

            case 'PUSH_HL':
                self.stack_pointer = self.stack_pointer - 1
                self.memory_bus.write_byte(self.stack_pointer, self.r_h)
                self.stack_pointer = self.stack_pointer - 1
                self.memory_bus.write_byte(self.stack_pointer, self.r_l)

            case 'POP_AF':
                self.r_f = self.memory_bus.read_byte(self.stack_pointer)
                self.stack_pointer = self.stack_pointer - 1
                self.r_a = self.memory_bus.read_byte(self.stack_pointer)
                self.stack_pointer = self.stack_pointer - 1
                self.flags.z = (self.r_f >> 7) & 0x01
                self.flags.n = (self.r_f >> 6) & 0x01
                self.flags.h = (self.r_f >> 5) & 0x01
                self.flags.c = (self.r_f >> 4) & 0x01

            case 'POP_BC':
                self.r_c = self.memory_bus.read_byte(self.stack_pointer)
                self.stack_pointer = self.stack_pointer - 1
                self.r_b = self.memory_bus.read_byte(self.stack_pointer)
                self.stack_pointer = self.stack_pointer - 1

            case 'POP_DE':
                self.r_e = self.memory_bus.read_byte(self.stack_pointer)
                self.stack_pointer = self.stack_pointer - 1
                self.r_d = self.memory_bus.read_byte(self.stack_pointer)
                self.stack_pointer = self.stack_pointer - 1

            case 'POP_HL':
                self.r_l = self.memory_bus.read_byte(self.stack_pointer)
                self.stack_pointer = self.stack_pointer - 1
                self.r_h = self.memory_bus.read_byte(self.stack_pointer)
                self.stack_pointer = self.stack_pointer - 1


    def ir_and_u8(self, instruction:Instruction):
        if instruction.definition.name == 'AND_B':
            self.and_u8(self.r_b)
        if instruction.definition.name == 'AND_C':
            self.and_u8(self.r_c)
        if instruction.definition.name == 'AND_D':
            self.and_u8(self.r_d)
        if instruction.definition.name == 'AND_E':
            self.and_u8(self.r_e)
        if instruction.definition.name == 'AND_H':
            self.and_u8(self.r_h)
        if instruction.definition.name == 'AND_L':
            self.and_u8(self.r_l)
        if instruction.definition.name == 'AND_A':
            self.and_u8(self.r_a)
        if instruction.definition.name == 'AND_HL':
            addr = self.get_r_hl()
            operand = self.memory_bus.read_byte(addr)
            self.and_u8(operand)
        if instruction.definition.name == 'AND_D8':
            self.and_u8(instruction.operands[0])

    #at this point I decided to use match case instead of if
    def ir_bit_u8(self, instruction:Instruction):
        base_instruction = instruction.definition.name[:-2]
        bit = instruction.definition.name[-1]
        bit = int(instruction.definition.name[-1]) if str.isnumeric(bit) else 0

        match base_instruction:
            case 'BIT_B':
                self.bit_u8(self.r_b, bit)
            case 'BIT_C':
                self.bit_u8(self.r_c, bit)
            case 'BIT_D':
                self.bit_u8(self.r_d, bit)
            case 'BIT_E':
                self.bit_u8(self.r_e, bit)
            case 'BIT_H':
                self.bit_u8(self.r_h, bit)
            case 'BIT_L':
                self.bit_u8(self.r_l, bit)
            case 'BIT_A':
                self.bit_u8(self.r_a, bit)
            case 'BIT_HL':
                operand = self.memory_bus.read_byte(self.get_r_hl())
                self.bit_u8(operand, bit)

    def ir_complement(self, instruction:Instruction):
        match instruction.definition.name:
            case 'CCF':
                self.flags.c = ~self.flags.c & 0x1
                self.flags.h = 0
                self.flags.n = 0
            case 'CPL':
                self.r_a = (~self.r_a) & 0xFF
                self.flags.h = 1
                self.flags.n = 1

    def ir_compare(self, instruction:Instruction):
        match instruction.definition.name:
            case 'CP_B':
                self.compare(self.r_b)
            case 'CP_C':
                self.compare(self.r_c)
            case 'CP_D':
                self.compare(self.r_d)
            case 'CP_E':
                self.compare(self.r_e)
            case 'CP_H':
                self.compare(self.r_h)
            case 'CP_L':
                self.compare(self.r_l)
            case 'CP_A':
                self.compare(self.r_a)
            case 'CP_HL':
                operand = self.memory_bus.read_byte(self.get_r_hl())
                self.compare(operand)
            case 'CP_D8':
                self.compare(instruction.operands[0])

    def ir_dec(self, instruction:Instruction):
        match instruction.definition.name:
            case 'DEC_B':
                self.r_b = self.alu.sub_u8(self.r_b , 1)
                self.set_flags_dec(self.r_b)
            case 'DEC_C':
                self.r_c = self.alu.sub_u8(self.r_c , 1)
                self.set_flags_dec(self.r_c)
            case 'DEC_D':
                self.r_d = self.alu.sub_u8(self.r_d , 1)
                self.set_flags_dec(self.r_d)
            case 'DEC_E':
                self.r_e = self.alu.sub_u8(self.r_e , 1)
                self.set_flags_dec(self.r_e)
            case 'DEC_H':
                self.r_h = self.alu.sub_u8(self.r_h , 1)
                self.set_flags_dec(self.r_h)
            case 'DEC_L':
                self.r_l = self.alu.sub_u8(self.r_l , 1)
                self.set_flags_dec(self.r_l)
            case 'DEC_A':
                self.r_a = self.alu.sub_u8(self.r_a , 1) - 1
                self.set_flags_dec(self.r_a)
            case 'DEC_HL':
                sub = self.memory_bus.read_byte(self.get_r_hl())
                new_value = self.alu.sub_u8(sub, 1)
                self.memory_bus.write_byte(self.get_r_hl(), new_value)

            case 'DEC16_HL':
                new_value = self.alu.sub_u16(self.get_r_hl(), 1)
                self.set_r_hl(new_value)

            case 'DEC16_BC':
                new_value = self.alu.sub_u16(self.get_r_bc(), 1)
                self.set_r_bc(new_value)

            case 'DEC16_DE':
                new_value = self.alu.sub_u16(self.get_r_de(), 1)
                self.set_r_de(new_value)

            case 'DEC16_SP':
                self.stack_pointer = self.alu.sub_u16(self.stack_pointer, 1)

    def ir_inc(self, instruction:Instruction):
        match instruction.definition.name:
            case 'INC_B':
                self.r_b = self.alu.add_u8(self.r_b, 1)
                self.set_flags_inc(self.r_b)
            case 'INC_C':
                self.r_c = self.alu.add_u8(self.r_c, 1)
                self.set_flags_inc(self.r_c)
            case 'INC_D':
                self.r_d = self.alu.add_u8(self.r_d, 1)
                self.set_flags_inc(self.r_d)
            case 'INC_E':
                self.r_e = self.alu.add_u8(self.r_e, 1)
                self.set_flags_inc(self.r_e)
            case 'INC_H':
                self.r_h = self.alu.add_u8(self.r_h, 1)
                self.set_flags_inc(self.r_h)
            case 'INC_L':
                self.r_l = self.alu.add_u8(self.r_l, 1)
                self.set_flags_inc(self.r_l)
            case 'INC_A':
                self.r_a = self.alu.add_u8(self.r_a, 1)
                self.set_flags_inc(self.r_a)
            case 'INC_HL':
                add = self.memory_bus.read_byte(self.get_r_hl())
                new_value = self.alu.add_u8(add, 1)
                self.memory_bus.write_byte(self.get_r_hl(), new_value)
                self.set_flags_inc(new_value)

            case 'INC16_HL':
                new_value = self.alu.add_u16(self.get_r_hl(), 1)
                self.set_r_hl(new_value)

            case 'INC16_BC':
                new_value = self.alu.add_u16(self.get_r_bc(), 1)
                self.set_r_bc(new_value)
                                   
            case 'INC16_DE':
                new_value = self.alu.add_u16(self.get_r_de(), 1)
                self.set_r_de(new_value)

            case 'INC16_SP':
                self.stack_pointer = self.alu.add_u16(self.stack_pointer, 1) 

    def ir_interrupt(self, instruction:Instruction):
        match instruction.definition.name:
            case 'DI':
                self.interrupts_enabled = False
            case 'EI':
                self.interrupts_enabled = True
            case 'HALT':
                self.is_halt = True

    def ir_or(self, instruction:Instruction):
        match instruction.definition.name:
            case 'OR_B':
                self.or_u8(self.r_b)
            case 'OR_C':
                self.or_u8(self.r_c)
            case 'OR_D':
                self.or_u8(self.r_d)
            case 'OR_E':
                self.or_u8(self.r_e)
            case 'OR_H':
                self.or_u8(self.r_h)
            case 'OR_L':
                self.or_u8(self.r_l) 
            case 'OR_A':
                self.or_u8(self.r_a)
            case 'OR_HL':
                operand = self.memory_bus.read_byte(self.get_r_hl())
                self.or_u8(operand)
            case 'OR_D8':
                self.or_u8(instruction.operands[0])

    def ir_rl(self, instruction:Instruction):
        match instruction.definition.name:
            case 'RL_B':
                self.r_b = self.rotate_l(self.r_b)
            case 'RL_C':
                self.r_c = self.rotate_l(self.r_c)
            case 'RL_D':
                self.r_d = self.rotate_l(self.r_d)
            case 'RL_E':
                self.r_e = self.rotate_l(self.r_e)
            case 'RL_H':
                self.r_h = self.rotate_l(self.r_h)
            case 'RL_L':
                self.r_l = self.rotate_l(self.r_l)
            case 'RL_HL':
                operand = self.memory_bus.read_byte(self.get_r_hl())
                result = self.rotate_l(operand)
                self.memory_bus.write_byte(self.get_r_hl(), result)
            case 'RL_A':
                self.r_a = self.rotate_l(self.r_a)
                self.flags.z = 0

            case 'RLC_B':
                self.r_b = self.rotate_l_carry(self.r_b)
            case 'RLC_C':
                self.r_c = self.rotate_l_carry(self.r_c)
            case 'RLC_D':
                self.r_d = self.rotate_l_carry(self.r_d)
            case 'RLC_E':
                self.r_e = self.rotate_l_carry(self.r_e)
            case 'RLC_H':
                self.r_h = self.rotate_l_carry(self.r_h)
            case 'RLC_L':
                self.r_l = self.rotate_l_carry(self.r_l)
            case 'RLC_HL':
                operand = self.memory_bus.read_byte(self.get_r_hl())
                result = self.rotate_l_carry(operand)
                self.memory_bus.write_byte(self.get_r_hl(), result)
            case 'RLC_A':
                self.r_a = self.rotate_l_carry(self.r_a)
                self.flags.z = 0

    def ir_rr(self, instruction:Instruction):
        match instruction.definition.name:
            case 'RR_B':
                self.r_b = self.rotate_r(self.r_b)
            case 'RR_C':
                self.r_c = self.rotate_r(self.r_c)
            case 'RR_D':
                self.r_d = self.rotate_r(self.r_d)
            case 'RR_E':
                self.r_e = self.rotate_r(self.r_e)
            case 'RR_H':
                self.r_h = self.rotate_r(self.r_h)
            case 'RR_L':
                self.r_l = self.rotate_r(self.r_l)
            case 'RR_HL':
                operand = self.memory_bus.read_byte(self.get_r_hl())
                result = self.rotate_r(operand)
                self.memory_bus.write_byte(self.get_r_hl(), result)
            case 'RR_A':
                self.r_a = self.rotate_r(self.r_a)
                self.flags.z = 0

            case 'RRC_B':
                self.r_b = self.rotate_r_carry(self.r_b)
            case 'RRC_C':
                self.r_c = self.rotate_r_carry(self.r_c)
            case 'RRC_D':
                self.r_d = self.rotate_r_carry(self.r_d)
            case 'RRC_E':
                self.r_e = self.rotate_r_carry(self.r_e)
            case 'RRC_H':
                self.r_h = self.rotate_r_carry(self.r_h)
            case 'RRC_L':
                self.r_l = self.rotate_r_carry(self.r_l)
            case 'RRC_HL':
                operand = self.memory_bus.read_byte(self.get_r_hl())
                result = self.rotate_r_carry(operand)
                self.memory_bus.write_byte(self.get_r_hl(), result)
            case 'RRC_A':
                self.r_a = self.rotate_r_carry(self.r_a)
                self.flags.z = 0


    def rotate_l_carry(self, operand):
        result = self.alu.rotate_left_carry(operand)
        self.flags.reset()
        self.flags.c = 0x01 if self.alu.overflow else 0x00
        self.flags.z = 0x01 if result == 0 else 0x00
        return result

    def rotate_l(self, operand):
        result = self.alu.rotate_left(operand, self.flags.c)
        self.flags.reset()
        self.flags.c = 0x01 if self.alu.overflow else 0x00
        self.flags.z = 0x01 if result == 0 else 0x00
        return result
    
    def rotate_r(self, operand):
        result = self.alu.rotate_right(operand, self.flags.c)
        self.flags.reset()
        self.flags.c = 0x01 if self.alu.overflow else 0x00
        self.flags.z = 0x01 if result == 0 else 0x00

    def rotate_r_carry(self, operand):
        result = self.alu.rotate_right_carry(operand)
        self.flags.reset()
        self.flags.c = 0x01 if self.alu.overflow else 0x00
        self.flags.z = 0x01 if result == 0 else 0x00


    def set_flags_inc(self, operand):
        self.flags.z = 0
        self.flags.n = 0
        self.flags. h = 0

        if (operand & 0xFF) == 0:
            self.flags.z = 1
        if (operand & 0xF) + 1 > 0xF:
            self.flags.h = 1


    def set_flags_dec(self, operand):
        self.flags.n = 1
        self.flags.z = 0
        self.flags.h = 0

        if (operand & 0xF) - 1 < 0:
            self.flags.h = 1

        if (operand & 0xFF) == 0:
            self.flags.z = 1

        self.flags.n = 1

    
    def compare(self, operand):
        self.flags.reset()
        self.flags.n = 1

        if self.r_a == operand:
            self.flags.z = 1

        if ((operand & 0xF) - (self.r_a & 0xF)) < 0:
            self.flags.h = 1
        
        if operand > self.r_a:
            self.flags.c = 1

    def jump_conditional(self, instruction:Instruction):
        addr = instruction.operands[1] << 8 | instruction.operands[0]
        self.program_counter = addr
        self.clock_cycle = self.clock_cycle + 1

    def jump_conditional_relative(self, instruction:Instruction):
        next_addr = self.program_counter
        addr = self.alu.add_as_sig(next_addr, instruction.operands[0])
        self.program_counter = addr
        self.clock_cycle = self.clock_cycle + 1

    def call(self, instruction:Instruction):
        next_line = self.program_counter
        least_byte = next_line & 0xFF
        most_byte = (next_line >> 8) & 0xFF
        self.memory_bus.write_byte(self.stack_pointer -1, most_byte)
        self.memory_bus.write_byte(self.stack_pointer -2, least_byte)
        self.stack_pointer = self.stack_pointer -2
        addr = instruction.operands[1] << 8 | instruction.operands[0]
        self.program_counter = addr

    def ret(self, instruction:Instruction):
        least_byte = self.memory_bus.read_byte(self.stack_pointer)
        most_byte = self.memory_bus.read_byte(self.stack_pointer + 1)
        self.program_counter = (most_byte << 8 & least_byte) & 0xFFFF
        self.stack_pointer = self.stack_pointer + 2

    def add_u8(self, operand, is_carry = False):
        carry = 0x01 if is_carry & self.flags.is_carry() else 0x00
        op_result = self.alu.add_u8(self.r_a, operand)
        first_op_carry = self.alu.overflow 
        op_result = self.alu.add_u8(op_result, carry)
        second_op_carry = self.alu.overflow

        self.flags.reset()
        if op_result == 00:
            self.flags.set_zero()
        if ((self.r_a & 0x0F) + (operand & 0x0F)) > 0x0F:
            self.flags.set_half_carry()
        if first_op_carry | second_op_carry:
            self.flags.set_carry()

        self.r_a = op_result & 0xFF

    def add_u16(self, operand):
        op_result = self.add_u16(self.get_r_hl(), operand)

        self.flags.n = 0
        if self.alu.overflow:
            self.flags.c = 1
        if ((self.get_r_hl() & 0xFFF) + (operand & 0xFFF)) > 0xFFF:
            self.flags.h = 1

        self.set_r_hl(op_result)

    def sub_u8(self, operand, is_carry = False):
        carry = 0x01 if is_carry & self.flags.is_carry() else 0x00
        op_result = self.alu.sub_u8(self.r_a, operand)
        first_op_carry = self.alu.overflow
        op_result = self.alu.sub_u8(op_result, carry)
        second_op_carry = self.alu.overflow

        self.flags.z = 0x01 if op_result == 0x00 else 0x00
        self.flags.n = 0x01
        self.flags.h = 0x01 if ((self.r_a & 0x0F) - (operand - 0x0f)) - carry < 0 else 0x00
        self.flags.c = 0x01 if first_op_carry | second_op_carry else 0x00

        self.r_a = op_result

    def and_u8(self, operand):
        op_result = self.alu.and_u8(self.r_a, operand)

        self.flags.reset()
        if op_result == 00:
            self.flags.set_zero()
        self.flags.set_half_carry()

        self.r_a = op_result

    def or_u8(self, operand):
        op_result = self.alu.or_u8(self.r_a, operand)

        self.flags.reset()
        if op_result == 0:
            self.flags.z = 1
        self.r_a = op_result

    def bit_u8(self, operand, bit):
        result = (operand >> bit) & 0x1
        
        self.flags.n = 0
        self.flags.h = 1
        if result == 0:
            self.flags.z = 1

    def get_r_hl(self):
        return (self.r_h << 8) | (self.r_l & 0xFF)
    
    def get_r_bc(self):
        return (self.r_b << 8) | (self.r_c & 0xFF)
    
    def get_r_de(self):
        return (self.r_d << 8) | (self.r_e & 0xFF)
    
    def set_r_hl(self, value):
        self.r_h = value >> 8
        self.r_l = value & 0xFF

    def set_r_bc(self, value):
        self.r_b = value >> 8
        self.r_c = value & 0xFF

    def set_r_de(self, value):
        self.r_d = value >> 8
        self.r_e = value & 0xFF


    ## changing the code convention only to write the infinite list of load instructions
    ## these are pretty simple instructions but this CPU has a lot of then
    def ir_load(self, instruction:Instruction):
        match instruction.definition.name:
            case 'LD_B_B':
                self.r_b = self.r_b
            case 'LD_B_C':
                self.r_b = self.r_c
            case 'LD_B_D':
                self.r_b = self.r_d
            case 'LD_B_E':
                self.r_b = self.r_e
            case 'LD_B_H':
                self.r_b = self.r_h
            case 'LD_B_L':
                self.r_b = self.r_l
            case 'LD_B_A':
                self.r_b = self.r_a

            case 'LD_C_B':
                self.r_c = self.r_b
            case 'LD_C_C':
                self.r_c = self.r_c
            case 'LD_c_D':
                self.r_c = self.r_d
            case 'LD_C_E':
                self.r_c = self.r_e
            case 'LD_C_H':
                self.r_c = self.r_h
            case 'LD_C_L':
                self.r_c = self.r_l
            case 'LD_C_A':
                self.r_c = self.r_a

            case 'LD_D_B':
                self.r_d = self.r_b
            case 'LD_D_C':
                self.r_d = self.r_c
            case 'LD_D_D':
                self.r_d = self.r_d
            case 'LD_D_E':
                self.r_d = self.r_e
            case 'LD_D_H':
                self.r_d = self.r_h
            case 'LD_D_L':
                self.r_d = self.r_l
            case 'LD_D_A':
                self.r_d = self.r_a

            case 'LD_E_B':
                self.r_e = self.r_b
            case 'LD_E_C':
                self.r_e = self.r_c
            case 'LD_E_D':
                self.r_e = self.r_d
            case 'LD_E_E':
                self.r_e = self.r_e
            case 'LD_E_H':
                self.r_e = self.r_h
            case 'LD_E_L':
                self.r_e = self.r_l
            case 'LD_E_A':
                self.r_e = self.r_a

            case 'LD_H_B':
                self.r_h = self.r_b
            case 'LD_H_C':
                self.r_h = self.r_c
            case 'LD_H_D':
                self.r_h = self.r_d
            case 'LD_H_E':
                self.r_h = self.r_e
            case 'LD_H_H':
                self.r_h = self.r_h
            case 'LD_H_L':
                self.r_h = self.r_l
            case 'LD_H_A':
                self.r_h = self.r_a

            case 'LD_L_B':
                self.r_l = self.r_b
            case 'LD_L_C':
                self.r_l = self.r_c
            case 'LD_L_D':
                self.r_l = self.r_d
            case 'LD_L_E':
                self.r_l = self.r_e
            case 'LD_L_H':
                self.r_l = self.r_h
            case 'LD_L_L':
                self.r_l = self.r_l
            case 'LD_L_A':
                self.r_l = self.r_a

            case 'LD_A_B':
                self.r_a = self.r_b
            case 'LD_A_C':
                self.r_a = self.r_c
            case 'LD_A_D':
                self.r_a = self.r_d
            case 'LD_A_E':
                self.r_a = self.r_e
            case 'LD_A_H':
                self.r_a = self.r_h
            case 'LD_A_L':
                self.r_a = self.r_l
            case 'LD_A_A':
                self.r_a = self.r_a

            case 'LD_HL_B':
                self.memory_bus.write_byte(self.get_r_hl(), self.r_b)
            case 'LD_HL_C':
                self.memory_bus.write_byte(self.get_r_hl(), self.r_c)
            case 'LD_HL_D':
                self.memory_bus.write_byte(self.get_r_hl(), self.r_d)
            case 'LD_HL_E':
                self.memory_bus.write_byte(self.get_r_hl(), self.r_e)
            case 'LD_HL_H':
                self.memory_bus.write_byte(self.get_r_hl(), self.r_h)
            case 'LD_HL_L':
                self.memory_bus.write_byte(self.get_r_hl(), self.r_l)
            case 'LD_HL_A':
                self.memory_bus.write_byte(self.get_r_hl(), self.r_a)

            case 'LD_B_HL':
                self.r_b = self.memory_bus.read_byte(self.get_r_hl())
            case 'LD_C_HL':
                self.r_c = self.memory_bus.read_byte(self.get_r_hl())
            case 'LD_D_HL':
                self.r_d = self.memory_bus.read_byte(self.get_r_hl())
            case 'LD_E_HL':
                self.r_e = self.memory_bus.read_byte(self.get_r_hl())
            case 'LD_H_HL':
                self.r_h = self.memory_bus.read_byte(self.get_r_hl())
            case 'LD_L_HL':
                self.r_l = self.memory_bus.read_byte(self.get_r_hl())
            case 'LD_A_HL':
                self.r_a = self.memory_bus.read_byte(self.get_r_hl())

            case 'LD_B_D8':
                self.r_b = instruction.operands[0]
            case 'LD_C_D8':
                self.r_c = instruction.operands[0]
            case 'LD_D_D8':
                self.r_d = instruction.operands[0]
            case 'LD_E_D8':
                self.r_e = instruction.operands[0]
            case 'LD_H_D8':
                self.r_h = instruction.operands[0]
            case 'LD_L_D8':
                self.r_l = instruction.operands[0]
            case 'LD_A_D8':
                self.r_a = instruction.operands[0]
            case 'LD_HL_D8':
                self.memory_bus.write_byte(self.get_r_hl(), instruction.operands[0])

            case 'LD_BC_D16':
                value = instruction.operands[0] | (instruction.operands[1] << 8)
                self.set_r_bc(value)
            case 'LD_DE_D16':
                value = instruction.operands[0] | (instruction.operands[1] << 8)
                self.set_r_de(value)
            case 'LD_HL_D16':
                value = instruction.operands[0] | (instruction.operands[1] << 8)
                self.set_r_hl(value)

            case 'LD_SP_D16':
                self.stack_pointer = instruction.operands[0] | instruction.operands[1] << 8
            case 'LD_D16_SP':
                least_byte = self.stack_pointer & 0xFF
                most_byte = self.stack_pointer >> 8 
                addr = instruction.operands[0] | instruction.operands[1] << 8
                self.memory_bus.write_byte(addr, least_byte)
                self.memory_bus.write_byte(addr, most_byte)
            case 'LD_SP_HL':
                self.stack_pointer = self.get_r_hl()
            case 'LD_HL_SPe':
                new_value = (self.stack_pointer + self.to_signed(instruction.operands[0])) & 0xFF
                self.set_r_hl(new_value)
                self.flags.z = 0
                self.flags.n = 0
                self.flags.h = (new_value & 0xF) + (self.stack_pointer & 0xF) > 0xF
                self.flags.c = (new_value & 0xFF) + (self.stack_pointer & 0xFF) > 0xFF

            case 'LD_BC_A':
                self.memory_bus.write_byte(self.get_r_bc(), self.r_a)
            case 'LD_DE_A':
                self.memory_bus.write_byte(self.get_r_de(), self.r_a)
            case 'LD_D16_A':
                addr = instruction.operands[0] | instruction.operands[1] << 8
                self.memory_bus.write_byte(addr, self.r_a)
            case 'LDH_D8_A':
                addr = 0xff00 + instruction.operands[0]
                self.memory_bus.write_byte(addr, self.r_a)
            case 'LDH_C_A':
                addr = 0xff00 + self.r_c
                self.memory_bus.write_byte(addr, self.r_a)
            case 'LD_HLI_A':
                self.memory_bus.write_byte(self.get_r_hl(), self.r_a)
                self.set_r_hl(self.get_r_hl() + 1)
            case 'LD_HLD_A':
                self.memory_bus.write_byte(self.get_r_hl(), self.r_a)
                self.set_r_hl(self.get_r_hl() - 1)

            case 'LD_A_BC':
                self.r_a = self.memory_bus.read_byte(self.get_r_bc())
            case 'LD_A_DE':
                self.r_a = self.memory_bus.read_byte(self.get_r_de())
            case 'LD_A_D16':
                addr = instruction.operands[0] | instruction.operands[1] << 8
                self.r_a = self.memory_bus.read_byte(addr)
            case 'LD_A_D8':
                addr = 0xff00 + instruction.operands[0]
                self.r_a = self.memory_bus.read_byte(addr)
            case 'LD_A_C':
                addr = 0xff00 + self.r_c
                self.r_a = self.memory_bus.read_byte(addr)
            case 'LD_A_HLI':
                self.r_a = self.memory_bus.read_byte(self.get_r_hl())
                self.set_r_hl(self.get_r_hl() + 1)
            case 'LD_A_HLD':
                self.r_a = self.memory_bus.read_byte(self.get_r_hl())
                self.set_r_hl(self.get_r_hl() - 1)