
from instructions_dict import *
from alu import *
from ppu import *
from basic_register import *
import time

class CPU_V2:
    program_counter = 0x0100
    stack_pointer = 0xfffe
    interrupts_enabled = True
    is_halt = False
    clock_cycle = 0

    registers = Registers()
    alu = ALU()

    def __init__(self, memory_bus:MemoryBus, ppu:PPU):
        self.memory_bus = memory_bus
        self.ppu = ppu

        self._base_inst_handler = {
            'NOP': lambda x : 0,
            'ADD': self.add_u8,
            'ADDC': self.add_u8,
            'JP': self.direct_jump,
            'JPR': self.relative_jump,
            'AND': self.and_u8,
            'CALL': self.call,
            'RET': self.ret,
            'ADDHL': self.add_u16,
            'ADDSP': self.add_signed_sp,
            'CCF': self.complement_carry,
            'CPL': self.complement_acc,
            'CP': self.compare,
            'DEC': self.decrement_u8,
            'INC': self.increment_u8,
            'DEC16': self.decrement_u16,
            'INC16': self.increment_u16,
            'DI': self.disable_interrupt,
            'EI': self.enable_interrupt,
            'HALT': self.halt,
            'LD': self.basic_load,
            'LDP': self.pointer_load,
            'LD16': self.load_16u,
            'LDS': self.load_stack,
            'LDH': self.load_high,
            'OR': self.or_u8,
            'POP': self.pop,
            'PUSH': self.push,
            'SUB': self.sub_u8,
            'SUBC': self.sub_u8,
            'XOR': self.xor_u8,
            'RST': self.rst,
            'RL': self.rotate_left,
            'RLC': self.rotate_left_carry,
            'RR': self.rotate_right,
            'RRC': self.rotate_right_carry,
            'SRL': self.shift_right_logical,
            'SWAP': self.swap,
            'DAA': self.decimal_adjust
        }

    def execute_step(self, step_count=1):
        count = 0
        while count < step_count:
            instruction = self.get_instruction()
            self.instruction_router(instruction)
            ##print(instruction.definition.name, hex(instruction.operands[1]), hex(instruction.operands[0]))
            count += 1
            if count % 1000000 == 0:
                self.ppu.basic_render()
        print('FINISH')
        time.sleep(3600)

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

        if instruction_definition == None:
            print(hex(instruction))

        operands = [0x00] * 2
        if instruction_definition.operands_number > 0:
            for i in range(instruction_definition.operands_number):
                operands[i] = self.memory_bus.read_byte(self.program_counter + program_step)
                program_step = program_step + 1

        instruction = Instruction(instruction_definition, operands)
        self.program_counter = self.program_counter + program_step
        self.clock_cycle = self.clock_cycle + instruction.definition.cycles

        return instruction
    
    def instruction_router(self, instruction:Instruction):
        decoded_base = instruction.definition.name.split('_')[0]
        base_handler = self._base_inst_handler.get(decoded_base)
        base_handler(instruction)

    def add_u8(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        base_inst = decoded_inst[0]
        operand_def = decoded_inst[1]

        use_carry = True if base_inst == 'ADDC' else False
        carry = 0x1 if use_carry & self.registers.carry else 0x0
        operand = 0x00
        match operand_def:
            case 'HL':
                operand = self.memory_bus.read_byte(self.registers.get_hl())
            case 'D8':
                operand = instruction.operands[0]
            case _:
                operand = self.registers.get_8_from_id(operand_def)

        acumulator = self.registers.get_a()
        first_result = self.alu.add_u8(acumulator, operand)
        first_carry = self.alu.overflow
        first_half_carry = self.alu.verify_overflow(acumulator, operand, 3)

        second_result = self.alu.add_u8(first_result, carry)
        second_carry = self.alu.overflow
        second_half_carry = self.alu.verify_overflow(first_result, carry, 3)
    
        self.registers.zero = True if second_result == 0 else False
        self.registers.negative = False
        self.registers.half_carry = first_half_carry | second_half_carry
        self.registers.carry = first_carry | second_carry

        self.registers.set_a(second_result)

    def add_u16(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]

        acumulator = self.registers.get_hl()
        operand = 0x00
        match operand_def:
            case 'SP':
                operand = self.stack_pointer
            case _:
                operand = self.registers.get_16_from_id(operand_def)

        result = self.alu.add_u16(acumulator, operand)

        self.registers.negative = False
        self.registers.half_carry = self.alu.verify_overflow(acumulator, operand, 11)
        self.registers.carry = self.alu.overflow

        self.registers.set_hl(result)

    def add_signed_sp(self, instruction:Instruction):
        acumulator = self.stack_pointer
        operand = instruction.operands[0]

        result = self.alu.add_as_sig(acumulator, operand)

        self.registers.zero = 0
        self.registers.negative = 0
        self.registers.half_carry = self.alu.verify_overflow(acumulator, operand, 3)
        self.registers.carry = self.alu.verify_overflow(acumulator, operand, 7)

        self.stack_pointer = result

    def and_u8(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]

        match operand_def:
            case 'HL':
                operand = self.memory_bus.read_byte(self.registers.get_hl())
            case 'D8':
                operand = instruction.operands[0]
            case _:
                operand = self.registers.get_8_from_id(operand_def)
        
        acumulator = self.registers.get_a()
        result = self.alu.and_u8(acumulator, operand)

        self.registers.zero = True if result == 0 else False
        self.registers.negative = False
        self.registers.half_carry = True
        self.registers.carry = False

        self.registers.set_a(result)

    def or_u8(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]

        match operand_def:
            case 'HL':
                operand = self.memory_bus.read_byte(self.registers.get_hl())
            case 'D8':
                operand = instruction.operands[0]
            case _:
                operand = self.registers.get_8_from_id(operand_def)
        
        acumulator = self.registers.get_a()
        result = self.alu.or_u8(acumulator, operand)

        self.registers.zero = True if result == 0 else False
        self.registers.negative = False
        self.registers.half_carry = False
        self.registers.carry = False

        self.registers.set_a(result)

    def xor_u8(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]

        match operand_def:
            case 'HL':
                operand = self.memory_bus.read_byte(self.registers.get_hl())
            case 'D8':
                operand = instruction.operands[0]
            case _:
                operand = self.registers.get_8_from_id(operand_def)
        
        acumulator = self.registers.get_a()
        result = self.alu.xor_u8(acumulator, operand)

        self.registers.zero = True if result == 0 else False
        self.registers.negative = False
        self.registers.half_carry = False
        self.registers.carry = False

        self.registers.set_a(result)

    def sub_u8(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        base_inst = decoded_inst[0]
        operand_def = decoded_inst[1]

        use_carry = True if base_inst == 'SUBC' else False
        carry = 0x1 if use_carry & self.registers.carry else 0x0
        operand = 0x00

        match operand_def:
            case 'HL':
                operand = self.memory_bus.read_byte(self.registers.get_hl())
            case 'D8':
                operand = instruction.operands[0]
            case _:
                operand = self.registers.get_8_from_id(operand_def)

        first_result = self.alu.sub_u8(self.registers.get_a(), operand)
        first_carry = self.alu.overflow
        first_half = self.alu.verify_borrow(self.registers.get_a(), operand, 3)

        second_result = self.alu.sub_u8(first_result, carry)
        second_carry = self.alu.overflow
        second_half = self.alu.verify_borrow(first_result, carry, 3)

        self.registers.zero = True if second_result == 0 else False
        self.registers.negative = True
        self.registers.half_carry = first_half | second_half
        self.registers.carry = first_carry | second_carry
        self.registers.set_a(second_result)

    def decimal_adjust(self, instruction:Instruction):
        new_carry = False
        if self.registers.negative:
            adjust = 0x00
            if self.registers.half_carry:
                adjust = self.alu.add_u8(adjust, 0x6)
            if self.registers.carry:
                adjust = self.alu.add_u8(adjust, 0x60)
                new_carry = True
            result = self.alu.sub_u8(self.registers.get_a(), adjust)
        else:
            a = self.registers.get_a()
            adjust = 0x00
            if self.registers.half_carry or a & 0xf > 0x9:
                adjust = self.alu.add_u8(adjust, 0x6)
            if self.registers.carry or a > 0x99:
                adjust = self.alu.add_u8(adjust, 0x60)
                new_carry = True
            result = self.alu.add_u8(a, adjust)
        self.registers.set_a(result)
        self.registers.zero = True if result == 0 else False
        self.registers.half_carry = False
        self.registers.carry = new_carry


    def compare(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]

        acumulator = self.registers.get_a()
        operand = 0x00
        match operand_def:
            case 'HL':
                operand = self.memory_bus.read_byte(self.registers.get_hl())
            case 'D8':
                operand = instruction.operands[0]
            case _:
                operand = self.registers.get_8_from_id(operand_def)

        self.registers.zero = True if operand == acumulator else False
        self.registers.negative = True
        self.registers.half_carry = self.alu.verify_borrow(acumulator, operand, 3)
        self.registers.carry = operand > acumulator

    def decrement_u8(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]

        operand = 0x00
        match operand_def:
            case 'HL':
                operand = self.memory_bus.read_byte(self.registers.get_hl())
            case _:
                operand = self.registers.get_8_from_id(operand_def)

        result = self.alu.sub_u8(operand, 1)
        self.registers.zero = True if result == 0 else False
        self.registers.negative = True
        self.registers.half_carry = self.alu.verify_borrow(operand, 1, 3)

        match operand_def:
            case 'HL':
                self.memory_bus.write_byte(self.registers.get_hl(), result)
            case _:
                self.registers.set_8_from_id(operand_def, result)

    def increment_u8(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]

        operand = 0x00
        match operand_def:
            case 'HL':
                operand = self.memory_bus.read_byte(self.registers.get_hl())
            case _:
                operand = self.registers.get_8_from_id(operand_def)

        result = self.alu.add_u8(operand, 1)
        self.registers.zero = True if result == 0 else False
        self.registers.negative = False
        self.registers.half_carry = self.alu.verify_overflow(operand, 1, 3)

        match operand_def:
            case 'HL':
                self.memory_bus.write_byte(self.registers.get_hl(), result)
            case _:
                self.registers.set_8_from_id(operand_def, result)
    
    def decrement_u16(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]

        operand = 0x0000
        match operand_def:
            case 'SP':
                operand = self.stack_pointer
            case _:
                operand = self.registers.get_16_from_id(operand_def)
        result = self.alu.sub_u16(operand, 1)
        match operand_def:
            case 'SP':
                self.stack_pointer = result
            case _:
                self.registers.set_16_from_id(operand_def, result)

    def increment_u16(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]

        operand = 0x0000
        match operand_def:
            case 'SP':
                operand = self.stack_pointer
            case _:
                operand = self.registers.get_16_from_id(operand_def)
        result = self.alu.add_u16(operand, 1)
        match operand_def:
            case 'SP':
                self.stack_pointer = result
            case _:
                self.registers.set_16_from_id(operand_def, result)


    def direct_jump(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]
        
        jump_addr = 0x10000
        match operand_def:
            case 'HL':
                jump_addr = self.registers.get_hl()
            case 'D16':
                jump_addr = self.build_u16_from_operands(instruction)
            case 'NZ':
                if not self.registers.zero:
                    jump_addr = self.build_u16_from_operands(instruction)
                    self.clock_cycle += 1
            case 'NC':
                if not self.registers.carry:
                    jump_addr = self.build_u16_from_operands(instruction)
                    self.clock_cycle += 1
            case 'Z':
                if self.registers.zero:
                    jump_addr = self.build_u16_from_operands(instruction)
                    self.clock_cycle += 1
            case 'C':
                if self.registers.carry:
                    jump_addr = self.build_u16_from_operands(instruction)
                    self.clock_cycle += 1

        if jump_addr <= 0xFFFF:
            self.program_counter = jump_addr

    def relative_jump(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]
        
        jump_addr = 0x10000
        actual_addr = self.program_counter
        offset = instruction.operands[0]
        next_addr = self.alu.add_as_sig(actual_addr, offset)
        
        match operand_def:
            case 'D16':
                jump_addr = next_addr
            case 'NZ':
                if not self.registers.zero:
                    jump_addr = next_addr
                    self.clock_cycle += 1
            case 'NC':
                if not self.registers.carry:
                    jump_addr = next_addr
                    self.clock_cycle += 1
            case 'Z':
                if self.registers.zero:
                    jump_addr = next_addr
                    self.clock_cycle += 1
            case 'C':
                if self.registers.carry:
                    jump_addr = next_addr
                    self.clock_cycle += 1

        if jump_addr <= 0xFFFF:
            self.program_counter = jump_addr

    def call(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]

        actual_addr = self.program_counter
        candidate_addr = self.build_u16_from_operands(instruction)
        jump_addr = 0x10000
        match operand_def:
            case 'D16':
                self.push_to_stack(actual_addr)
                jump_addr = candidate_addr
            case 'NZ':
                if not self.registers.zero:
                    self.push_to_stack(actual_addr)
                    jump_addr = candidate_addr
                    self.clock_cycle += 3
            case 'NC':
                if not self.registers.carry:
                    self.push_to_stack(actual_addr)
                    jump_addr = candidate_addr
                    self.clock_cycle += 3
            case 'Z':
                if self.registers.zero:
                    self.push_to_stack(actual_addr)
                    jump_addr = candidate_addr
                    self.clock_cycle += 3
            case 'C':
                if self.registers.carry:
                    self.push_to_stack(actual_addr)
                    jump_addr = candidate_addr
                    self.clock_cycle += 3

        if jump_addr <= 0xFFFF:
            self.program_counter = jump_addr

    def ret(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]

        jump_addr = 0x10000
        match operand_def:
            case 'D16':
                jump_addr = self.pop_from_stack()
            case 'NZ':
                if not self.registers.zero:
                    jump_addr = self.pop_from_stack()
                    self.clock_cycle += 3
            case 'NC':
                if not self.registers.carry:
                    jump_addr = self.pop_from_stack()
                    self.clock_cycle += 3
            case 'Z':
                if self.registers.zero:
                    jump_addr = self.pop_from_stack()
                    self.clock_cycle += 3
            case 'C':
                if self.registers.carry:
                    jump_addr = self.pop_from_stack()
                    self.clock_cycle += 3

        if jump_addr <= 0xFFFF:
            self.program_counter = jump_addr

    def rst(self, instruction:Instruction):
        vector = [0x0 , 0x8 , 0x10 , 0x18 , 0x20 , 0x28 , 0x30 , 0x38]
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]
        instruction.operands[0] = vector[int(operand_def)]
        self.call(instruction)

    def complement_carry(self, instruction:Instruction):
        self.registers.negative = False
        self.registers.half_carry = False
        self.registers.carry = not self.registers.carry

    def complement_acc(self, instruction:Instruction):
        self.registers.negative = True
        self.registers.half_carry = True
        
        acumulator = self.registers.get_a()
        result = self.alu.not_u8(acumulator)
        self.registers.set_a(result)

    def rotate_left(self, instruction:Instruction):
        self.shift_rotation_operations(instruction, self.alu.rotate_left, True)

    def rotate_left_carry(self, instruction:Instruction):
        self.shift_rotation_operations(instruction, self.alu.rotate_left_carry)

    def rotate_right(self, instruction:Instruction):
        self.shift_rotation_operations(instruction, self.alu.rotate_right, True)

    def rotate_right_carry(self, instruction:Instruction):
        self.shift_rotation_operations(instruction, self.alu.rotate_right_carry)

    def shift_right_logical(self, instruction:Instruction):
        self.shift_rotation_operations(instruction, self.alu.shift_right_logical)

    def shift_rotation_operations(self, instruction:Instruction, alu_opr, use_carry=False):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]

        carry = self.registers.carry * 1
        new_carry = False
        result = 0x00
        match operand_def:
            case 'HL':
                operand = self.memory_bus.read_byte(self.registers.get_hl())
                if use_carry:
                    result = alu_opr(operand, carry)
                else:
                    result = alu_opr(operand)
                new_carry = self.alu.overflow
                self.memory_bus.write_byte(self.registers.get_hl(), result)
            case _:
                operand = self.registers.get_8_from_id(operand_def)
                if use_carry:
                    result = alu_opr(operand, carry)
                else:
                    result = alu_opr(operand)
                new_carry = self.alu.overflow
                self.registers.set_8_from_id(operand_def, result)

        self.registers.zero = True if result == 0 else False
        self.registers.negative = False
        self.registers.half_carry = False
        self.registers.carry = new_carry

    def swap(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]

        result = 0x00
        match operand_def:
            case 'HL':
                operand = self.memory_bus.read_byte(self.registers.get_hl())
                result = self.alu.swap_u8(operand)
                self.memory_bus.write_byte(self.registers.get_hl(), result)
            case _:
                operand = self.registers.get_8_from_id(operand_def)
                result = self.alu.swap_u8(operand)
                self.registers.set_8_from_id(operand_def, result)
        
        self.registers.zero = True if result == 0 else False
        self.registers.negative = False
        self.registers.half_carry = False
        self.registers.carry = False

    def disable_interrupt(self, instruction:Instruction):
        self.interrupts_enabled = False

    def enable_interrupt(self, instruction:Instruction):
        self.interrupts_enabled = True
    
    def halt(self, instruction:Instruction):
        self.is_halt = True

    def basic_load(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        from_register = decoded_inst[2]
        to_register = decoded_inst[1]

        value = 0x00
        match from_register:
            case 'HL':
                value = self.memory_bus.read_byte(self.registers.get_hl())
            case 'D8':
                value = instruction.operands[0]
            case _:
                value = self.registers.get_8_from_id(from_register)

        match to_register:
            case 'HL':
                self.memory_bus.write_byte(self.registers.get_hl(), value)
            case _:
                self.registers.set_8_from_id(to_register, value)

    def pointer_load(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        from_register = decoded_inst[2]
        to_register = decoded_inst[1]

        value = 0x0
        match from_register:
            case 'A':
                value = self.registers.get_a()
            case 'D16':
                addr = self.build_u16_from_operands(instruction)
                value = self.memory_bus.read_byte(addr)
            case 'HLI':
                addr = self.registers.get_hl()
                value = self.memory_bus.read_byte(addr)
                self.registers.set_hl(addr + 1) ## this can be buggy
            case 'HLD':
                addr = self.registers.get_hl()
                value = self.memory_bus.read_byte(addr)
                self.registers.set_hl(addr - 1) ## this can be buggy
            case _:
                value = self.memory_bus.read_byte(self.registers.get_16_from_id(from_register))

        match to_register:
            case 'A':
                self.registers.set_a(value)
            case 'D16':
                addr = self.build_u16_from_operands(instruction)
                self.memory_bus.write_byte(addr, value)
            case 'HLI':
                addr = self.registers.get_hl()
                self.memory_bus.write_byte(addr, value)
                self.registers.set_hl(addr + 1) ## this can be buggy
            case 'HLD':
                addr = self.registers.get_hl()
                self.memory_bus.write_byte(addr, value)
                self.registers.set_hl(addr - 1) ## this can be buggy
            case _:
                self.memory_bus.write_byte(self.registers.get_16_from_id(to_register), value)

    def load_16u(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        to_register = decoded_inst[1]

        value = self.build_u16_from_operands(instruction)
        match to_register:
            case 'SP':
                self.stack_pointer = value
            case _:
                self.registers.set_16_from_id(to_register, value)

    def load_stack(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        to_register = decoded_inst[1]

        value = 0x0
        match to_register:
            case 'D16':
                addr = self.build_u16_from_operands(instruction)
                value = self.stack_pointer
                self.memory_bus.write_byte(addr, value & 0xFF)
                self.memory_bus.write_byte(addr + 1, value >> 8)
            case 'SP':
                self.stack_pointer = self.registers.get_hl()
            case 'HL':
                a = self.stack_pointer
                b = instruction.operands[0]
                result = self.alu.add_as_sig(a, b)
                self.registers.set_hl(result)
                self.registers.zero = False
                self.registers.negative = False
                self.registers.half_carry = self.alu.verify_overflow(a, b, 3)
                self.registers.carry = self.alu.verify_overflow(a, b, 7)

    def load_high(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        from_register = decoded_inst[2]
        to_register = decoded_inst[1]

        base_addr = 0xFF00
        offset = 0x00
        value = 0x00
        match from_register:
            case 'A':
                value = self.registers.get_a()
            case 'C':
                offset = self.registers.get_c()
                addr = offset + base_addr
                value = self.memory_bus.read_byte(addr)
            case 'D8':
                offset = instruction.operands[0]
                addr = offset + base_addr
                value = self.memory_bus.read_byte(addr)

        match to_register:
            case 'A':
                self.registers.set_a(value)
            case 'C':
                offset = self.registers.get_c()
                addr = offset + base_addr
                self.memory_bus.write_byte(addr, value)
            case 'D8':
                offset = instruction.operands[0]
                addr = offset + base_addr
                self.memory_bus.write_byte(addr, value)

    def pop(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]
        value = self.pop_from_stack()
        self.registers.set_16_from_id(operand_def, value)

    def push(self, instruction:Instruction):
        decoded_inst = instruction.definition.name.split('_')
        operand_def = decoded_inst[1]
        value = self.registers.get_16_from_id(operand_def)
        self.push_to_stack(value)


    def push_to_stack(self, addr):
        least_s = addr & 0xFF
        most_s = addr >> 8 

        self.stack_pointer -= 1
        self.memory_bus.write_byte(self.stack_pointer, most_s)
        self.stack_pointer -= 1
        self.memory_bus.write_byte(self.stack_pointer, least_s)

    def pop_from_stack(self):
        least_s = self.memory_bus.read_byte(self.stack_pointer)
        self.stack_pointer += 1
        most_s = self.memory_bus.read_byte(self.stack_pointer)
        self.stack_pointer += 1

        return (most_s << 8) | least_s


    def build_u16_from_operands(self, instruction:Instruction):
        return instruction.operands[1] << 8 | instruction.operands[0]
