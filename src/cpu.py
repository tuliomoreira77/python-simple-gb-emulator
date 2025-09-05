from bus import *
from instructions_dict import *


class Flags:
    z = 0x0
    n = 0x0
    h = 0x0
    c = 0x0

    def reset(self):
        self.z = 0x0
        self.n = 0x0
        self.h = 0x0
        self.c = 0x0

    def is_zero(self):
        return self.z & 0x1
    
    def is_carry(self):
        return self.c & 0x1
    
    def is_sub(self):
        return self.n & 0x1
    
    def is_half_carry(self):
        return self.h & 0x1
    
    def set_zero(self):
        self.z = 0x1
    
    def set_carry(self):
        self.c = 0x1
    
    def set_sub(self):
        self.n = 0x1
    
    def set_half_carry(self):
        self.c = 0x1

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

    def __init__(self, game_rom):
        self.memory_bus.load_rom(game_rom)

    def basic_debug(self):
        print("Register A: {}".format(self.r_a))
        print("Flags z: {}".format(self.flags.z)) 
        print("Flags n: {}".format(self.flags.n)) 
        print("Flags h: {}".format(self.flags.h)) 
        print("Flags c: {}".format(self.flags.c)) 

    def execute(self):
        while(True):
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

            ##self.basic_debug()

            if self.program_counter > ROM_END:
                break

    def get_instruction(self):
        instruction = self.memory_bus.read_byte(self.program_counter)
        print(instruction)
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
            if not self.flags.is_zero:
                self.jump_conditional(instruction)

        if instruction.definition.name == 'JP_NC':
            if not self.flags.is_carry == 0:
                self.jump_conditional(instruction)

        if instruction.definition.name == 'JP_Z':
            if self.flags.is_zero:
                self.jump_conditional(instruction)

        if instruction.definition.name == 'JP_C':
            if self.flags.is_carry:
                self.jump_conditional(instruction)

        if instruction.definition.name == 'JPR_D16':
            next_addr = self.program_counter + 1
            addr = (next_addr + instruction.operands[0] - 128) & 0xFFFF
            self.program_counter = addr

        if instruction.definition.name == 'JPR_NZ':
            if not self.flags.is_zero:
                self.jump_conditional_relative(instruction)

        if instruction.definition.name == 'JPR_NC':
            if not self.flags.is_carry == 0:
                self.jump_conditional_relative(instruction)


        if instruction.definition.name == 'JPR_Z':
            if self.flags.is_zero:
                self.jump_conditional_relative(instruction)


        if instruction.definition.name == 'JPR_C':
            if self.flags.is_carry:
                self.jump_conditional_relative(instruction)


    def ir_call(self, instruction:Instruction):
        if instruction.definition.name == 'CALL_D16':
            self.call(instruction)
        if instruction.definition.name == 'CALL_NZ':
            if not self.flags.is_zero():
                self.call(instruction)
                self.clock_cycle = self.clock_cycle + 3
        if instruction.definition.name == 'CALL_NC':
            if not self.flags.is_carry():
                self.call(instruction)
                self.clock_cycle = self.clock_cycle + 3
        if instruction.definition.name == 'CALL_Z':
            if self.flags.is_zero():
                self.call(instruction)
                self.clock_cycle = self.clock_cycle + 3
        if instruction.definition.name == 'CALL_C':
            if self.flags.is_carry():
                self.call(instruction)
                self.clock_cycle = self.clock_cycle + 3

    def ir_ret(self, instruction:Instruction):
        if instruction.definition.name == 'RET_D16':
            self.ret(instruction)
        if instruction.definition.name == 'RET_NZ':
            if not self.flags.is_zero():
                self.ret(instruction)
                self.clock_cycle = self.clock_cycle + 3
        if instruction.definition.name == 'RET_NC':
            if not self.flags.is_carry():
                self.ret(instruction)
                self.clock_cycle = self.clock_cycle + 3
        if instruction.definition.name == 'RET_Z':
            if self.flags.is_zero():
                self.ret(instruction)
                self.clock_cycle = self.clock_cycle + 3
        if instruction.definition.name == 'RET_C':
            if self.flags.is_carry():
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

    def ir_opr_sp(self, instruction:Instruction):
        if instruction.definition.name == 'ADDSP_D8':
            operand = (instruction.operands[0] - 127) & 0xFF
            new_sp = ( self.stack_pointer + operand ) & 0xFFFF

            self.flags.reset()
            if ((self.stack_pointer & 0xF) + (operand & 0xF)) > 0xF:
                self.flags.set_half_carry()
            if ((self.stack_pointer & 0xFF) + (operand & 0xFF)) > 0xFF:
                self.flags.set_carry()

            self.stack_pointer = new_sp


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
                self.r_b = self.r_b - 1
                self.set_flags_dec(self.r_b)
            case 'DEC_C':
                self.r_c = self.r_c - 1
                self.set_flags_dec(self.r_c)
            case 'DEC_D':
                self.r_d = self.r_d - 1
                self.set_flags_dec(self.r_d)
            case 'DEC_E':
                self.r_e = self.r_e - 1
                self.set_flags_dec(self.r_e)
            case 'DEC_H':
                self.r_h = self.r_h - 1
                self.set_flags_dec(self.r_h)
            case 'DEC_L':
                self.r_l = self.r_l - 1
                self.set_flags_dec(self.r_l)
            case 'DEC_A':
                self.r_a = self.r_a - 1
                self.set_flags_dec(self.r_a)
            case 'DEC_HL':
                new_value = self.memory_bus.read_byte(self.get_r_hl()) - 1
                self.memory_bus.write_byte(self.get_r_hl(), new_value)
                self.set_flags_dec(new_value)

            case 'DEC16_HL':
                new_value = self.get_r_hl() - 1
                self.set_r_hl(new_value)
                self.set_flags_dec(new_value)

            case 'DEC16_BC':
                new_value = self.get_r_bc() - 1
                self.set_r_bc(new_value)
                self.set_flags_dec(new_value)

            case 'DEC16_DE':
                new_value = self.get_r_de() - 1
                self.set_r_de(new_value)
                self.set_flags_dec(new_value)

            case 'DEC16_SP':
                self.stack_pointer = self.stack_pointer - 1

    def ir_inc(self, instruction:Instruction):
        match instruction.definition.name:
            case 'INC_B':
                self.r_b = self.r_b + 1
                self.set_flags_inc(self.r_b)
            case 'INC_C':
                self.r_c = self.r_c + 1
                self.set_flags_inc(self.r_c)
            case 'INC_D':
                self.r_d = self.r_d + 1
                self.set_flags_inc(self.r_d)
            case 'INC_E':
                self.r_e = self.r_e + 1
                self.set_flags_inc(self.r_e)
            case 'INC_H':
                self.r_h = self.r_h + 1
                self.set_flags_inc(self.r_h)
            case 'INC_L':
                self.r_l = self.r_l + 1
                self.set_flags_inc(self.r_l)
            case 'INC_A':
                self.r_a = self.r_a + 1
                self.set_flags_inc(self.r_a)
            case 'INC_HL':
                new_value = self.memory_bus.read_byte(self.get_r_hl()) + 1
                self.memory_bus.write_byte(self.get_r_hl(), new_value)
                self.set_flags_inc(new_value)

            case 'INC16_HL':
                new_value = self.get_r_hl() + 1
                self.set_r_hl(new_value)
                self.set_flags_inc(new_value)

            case 'INC16_BC':
                new_value = self.get_r_bc() + 1
                self.set_r_bc(new_value)
                self.set_flags_inc(new_value)

            case 'INC16_DE':
                new_value = self.get_r_de() + 1
                self.set_r_de(new_value)
                self.set_flags_inc(new_value)

            case 'INC16_SP':
                self.stack_pointer = self.stack_pointer + 1

    def ir_interrupt(self, instruction:Instruction):
        match instruction.definition.name:
            case 'DI':
                self.interrupts_enabled = False
            case 'EI':
                self.interrupts_enabled = True
            case 'HALT':
                self.is_halt = True



    def set_flags_inc(self, operand):
        if operand == 0:
            self.flags.z = 1
        if (operand & 0xF) + 1 > 0xF:
            self.flags.h = 1
        self.flags.n = 0


    def set_flags_dec(self, operand):
        if (operand & 0xF) - 1 < 0:
            self.flags.h = 1

        if operand == 0:
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
        addr = instruction.operands[1] << 8 & instruction.operands[0]
        self.program_counter = addr
        self.clock_cycle = self.clock_cycle + 1

    def jump_conditional_relative(self, instruction:Instruction):
        next_addr = self.program_counter + 1
        addr = (next_addr + instruction.operands[0] - 128) & 0xFFFF
        self.program_counter = addr
        self.clock_cycle = self.clock_cycle + 1

    def call(self, instruction:Instruction):
        next_line = self.program_counter + 1
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
        op_result = self.r_a + operand + carry

        self.flags.reset()
        if op_result == 00:
            self.flags.set_zero()
        if ((self.r_a & 0x0F) + (operand & 0x0F)) > 0x0F:
            self.flags.set_half_carry()
        if op_result > 0xFF:
            self.flags.set_carry()

        self.r_a = op_result & 0xFF

    def add_u16(self, operand):
        op_result = self.get_r_hl + operand

        self.flags.reset()
        if op_result == 00:
            self.flags.set_zero()
        if op_result > 0xFFFF:
            self.flags.set_carry()
        if ((self.r_a & 0xFFF) + (operand & 0xFFF)) > 0xFFF:
            self.flags.set_half_carry()

    def and_u8(self, operand):
        op_result = self.r_a & operand

        self.flags.reset()
        if op_result == 00:
            self.flags.set_zero()
        self.flags.set_half_carry()

        self.r_a = op_result & 0xFF

    def bit_u8(self, operand, bit):
        result = (operand >> bit) & 0x1
        
        self.flags.n = 0
        self.flags.h = 1
        if result == 0:
            self.flags.z = 1

    def get_r_hl(self):
        return ((self.r_h << 8) & self.r_l) & 0xFF
    
    def get_r_bc(self):
        return ((self.r_b << 8) & self.r_c) & 0xFF
    
    def get_r_de(self):
        return ((self.r_d << 8) & self.r_e) & 0xFF
    
    def set_r_hl(self, value):
        self.r_h = value >> 8
        self.r_l = value & 0xFF

    def set_r_bc(self, value):
        self.r_b = value >> 8
        self.r_c = value & 0xFF

    def set_r_de(self, value):
        self.r_d = value >> 8
        self.r_e = value & 0xFF