 

class InstructionDefinition:
    def __init__(self, name, operands_number, cycles):
        self.name = name
        self.operands_number = operands_number
        self.cycles = cycles

class Instruction:
    def __init__(self, definition:InstructionDefinition, operands):
        self.definition = definition
        self.operands = operands

INSTRUCTION_DICT = {
    0x00: InstructionDefinition('NOP', 0, 1),

    0x80: InstructionDefinition('ADD_B', 0, 1),
    0x81: InstructionDefinition('ADD_C', 0, 1),
    0x82: InstructionDefinition('ADD_D', 0, 1),
    0x83: InstructionDefinition('ADD_E', 0, 1),
    0x84: InstructionDefinition('ADD_H', 0, 1),
    0x85: InstructionDefinition('ADD_L', 0, 1),
    0x86: InstructionDefinition('ADD_HL', 0, 2),
    0x87: InstructionDefinition('ADD_A', 0, 1),
    0xc6: InstructionDefinition('ADD_D8', 1, 2),

    0x88: InstructionDefinition('ADDC_B', 0, 1),
    0x89: InstructionDefinition('ADDC_C', 0, 1),
    0x8a: InstructionDefinition('ADDC_D', 0, 1),
    0x8b: InstructionDefinition('ADDC_E', 0, 1),
    0x8c: InstructionDefinition('ADDC_H', 0, 1),
    0x8d: InstructionDefinition('ADDC_L', 0, 1),
    0x8e: InstructionDefinition('ADDC_HL', 0, 2),
    0x8f: InstructionDefinition('ADDC_A', 0, 1),
    0xce: InstructionDefinition('ADDC_D8', 1, 2),

    0xe9: InstructionDefinition('JP_HL', 0, 1),
    0xc3: InstructionDefinition('JP_D16', 2, 4),
    0xc2: InstructionDefinition('JP_NZ', 2, 3),
    0xd2: InstructionDefinition('JP_NC', 2, 3),
    0xca: InstructionDefinition('JP_Z', 2, 3),
    0xda: InstructionDefinition('JP_C', 2, 3),

    0x18: InstructionDefinition('JPR_D16', 1, 2),
    0x20: InstructionDefinition('JPR_NZ', 1, 2),
    0x30: InstructionDefinition('JPR_NC', 1, 2),
    0x28: InstructionDefinition('JPR_Z', 1, 2),
    0x38: InstructionDefinition('JPR_C', 1, 2),

    0xa0: InstructionDefinition('AND_B', 0, 1),
    0xa1: InstructionDefinition('AND_C', 0, 1),
    0xa2: InstructionDefinition('AND_D', 0, 1),
    0xa3: InstructionDefinition('AND_E', 0, 1),
    0xa4: InstructionDefinition('AND_H', 0, 1),
    0xa5: InstructionDefinition('AND_L', 0, 1),
    0xa6: InstructionDefinition('AND_HL', 0, 1),
    0xa7: InstructionDefinition('AND_A', 0, 1),
    0xe6: InstructionDefinition('AND_D8', 1, 2),

    0xcd: InstructionDefinition('CALL_D16', 2, 6),
    0xc4: InstructionDefinition('CALL_NZ', 2, 3),
    0xd4: InstructionDefinition('CALL_NC', 2, 3),
    0xcc: InstructionDefinition('CALL_Z', 2, 3),
    0xdc: InstructionDefinition('CALL_C', 2, 3),

    0xc9: InstructionDefinition('RET_D16', 0, 4),
    0xc0: InstructionDefinition('RET_NZ', 0, 2),
    0xd0: InstructionDefinition('RET_NC', 0, 2),
    0xc8: InstructionDefinition('RET_Z', 0, 2),
    0xd8: InstructionDefinition('RET_C', 0, 2),

    0x09: InstructionDefinition('ADDHL_BC', 0, 2),
    0x19: InstructionDefinition('ADDHL_DE', 0, 2),
    0x29: InstructionDefinition('ADDHL_HL', 0, 2),
    0x39: InstructionDefinition('ADDHL_SP', 0, 2),

    0xe8: InstructionDefinition('ADDSP_D8', 1, 2),

    0x3f: InstructionDefinition('CCF', 0, 1),
    0x2f: InstructionDefinition('CPL', 0, 1),

    0xb8: InstructionDefinition('CP_B', 0, 1),
    0xb9: InstructionDefinition('CP_C', 0, 1),
    0xba: InstructionDefinition('CP_D', 0, 1),
    0xbb: InstructionDefinition('CP_E', 0, 1),
    0xbc: InstructionDefinition('CP_H', 0, 1),
    0xbd: InstructionDefinition('CP_L', 0, 1),
    0xbe: InstructionDefinition('CP_HL', 0, 2),
    0xbf: InstructionDefinition('CP_A', 0, 1),
    0xfe: InstructionDefinition('CP_D8', 1, 2),

    0x05: InstructionDefinition('DEC_B', 0, 1),
    0x0d: InstructionDefinition('DEC_C', 0, 1),
    0x15: InstructionDefinition('DEC_D', 0, 1),
    0x1d: InstructionDefinition('DEC_E', 0, 1),
    0x25: InstructionDefinition('DEC_H', 0, 1),
    0x2d: InstructionDefinition('DEC_L', 0, 1),
    0x3d: InstructionDefinition('DEC_A', 0, 1),
    0x35: InstructionDefinition('DEC_HL', 0, 3),

    0x2b: InstructionDefinition('DEC16_HL', 0, 2),
    0x0b: InstructionDefinition('DEC16_BC', 0, 2),
    0x1b: InstructionDefinition('DEC16_DE', 0, 2),
    0x3b: InstructionDefinition('DEC16_SP', 0, 2),

    0x04: InstructionDefinition('INC_B', 0, 1),
    0x0c: InstructionDefinition('INC_C', 0, 1),
    0x14: InstructionDefinition('INC_D', 0, 1),
    0x1c: InstructionDefinition('INC_E', 0, 1),
    0x24: InstructionDefinition('INC_H', 0, 1),
    0x2c: InstructionDefinition('INC_L', 0 ,1),
    0x3c: InstructionDefinition('INC_A', 0, 1),
    0x34: InstructionDefinition('INC_HL', 0, 2),

    0x03: InstructionDefinition('INC16_BC', 0, 2),
    0x13: InstructionDefinition('INC16_DE', 0, 2),
    0x23: InstructionDefinition('INC16_HL', 0, 2),
    0x33: InstructionDefinition('INC16_SP', 0, 2),

    0xf3: InstructionDefinition('DI', 0, 1),
    0xfb: InstructionDefinition('EI', 0, 1),
    0x76: InstructionDefinition('HALT', 0, 1),


    ## Infinite load instructions
    0x40: InstructionDefinition('LD_B_B', 0, 1),
    0x41: InstructionDefinition('LD_B_C', 0, 1),
    0x42: InstructionDefinition('LD_B_D', 0, 1),
    0x43: InstructionDefinition('LD_B_E', 0, 1),
    0x44: InstructionDefinition('LD_B_H', 0, 1),
    0x45: InstructionDefinition('LD_B_L', 0, 1),
    0x47: InstructionDefinition('LD_B_A', 0, 1),

    0x48: InstructionDefinition('LD_C_B', 0, 1),
    0x49: InstructionDefinition('LD_C_C', 0, 1),
    0x4a: InstructionDefinition('LD_C_D', 0, 1),
    0x4b: InstructionDefinition('LD_C_E', 0, 1),
    0x4c: InstructionDefinition('LD_C_H', 0, 1),
    0x4d: InstructionDefinition('LD_C_L', 0, 1),
    0x4f: InstructionDefinition('LD_C_A', 0, 1),

    0x50: InstructionDefinition('LD_D_B', 0, 1),
    0x51: InstructionDefinition('LD_D_C', 0, 1),
    0x52: InstructionDefinition('LD_D_D', 0, 1),
    0x53: InstructionDefinition('LD_D_E', 0, 1),
    0x54: InstructionDefinition('LD_D_H', 0, 1),
    0x55: InstructionDefinition('LD_D_L', 0, 1),
    0x57: InstructionDefinition('LD_D_A', 0, 1),

    0x58: InstructionDefinition('LD_E_B', 0, 1),
    0x59: InstructionDefinition('LD_E_C', 0, 1),
    0x5a: InstructionDefinition('LD_E_D', 0, 1),
    0x5b: InstructionDefinition('LD_E_E', 0, 1),
    0x5c: InstructionDefinition('LD_E_H', 0, 1),
    0x5d: InstructionDefinition('LD_E_L', 0, 1),
    0x5f: InstructionDefinition('LD_E_A', 0, 1),

    0x60: InstructionDefinition('LD_H_B', 0, 1),
    0x61: InstructionDefinition('LD_H_C', 0, 1),
    0x62: InstructionDefinition('LD_H_D', 0, 1),
    0x63: InstructionDefinition('LD_H_E', 0, 1),
    0x64: InstructionDefinition('LD_H_H', 0, 1),
    0x65: InstructionDefinition('LD_H_L', 0, 1),
    0x67: InstructionDefinition('LD_H_A', 0, 1),

    0x68: InstructionDefinition('LD_L_B', 0, 1),
    0x69: InstructionDefinition('LD_L_C', 0, 1),
    0x6a: InstructionDefinition('LD_L_D', 0, 1),
    0x6b: InstructionDefinition('LD_L_E', 0, 1),
    0x6c: InstructionDefinition('LD_L_H', 0, 1),
    0x6d: InstructionDefinition('LD_L_L', 0, 1),
    0x6f: InstructionDefinition('LD_L_A', 0, 1),

    0x78: InstructionDefinition('LD_A_B', 0, 1),
    0x79: InstructionDefinition('LD_A_C', 0, 1),
    0x7a: InstructionDefinition('LD_A_D', 0, 1),
    0x7b: InstructionDefinition('LD_A_E', 0, 1),
    0x7c: InstructionDefinition('LD_A_H', 0, 1),
    0x7d: InstructionDefinition('LD_A_L', 0, 1),
    0x7f: InstructionDefinition('LD_A_A', 0, 1),

    0x70: InstructionDefinition('LD_HL_B', 0, 2),
    0x71: InstructionDefinition('LD_HL_C', 0, 2),
    0x72: InstructionDefinition('LD_HL_D', 0, 2),
    0x73: InstructionDefinition('LD_HL_E', 0, 2),
    0x74: InstructionDefinition('LD_HL_H', 0, 2),
    0x75: InstructionDefinition('LD_HL_L', 0, 2),
    0x77: InstructionDefinition('LD_HL_A', 0, 2),

    0x46: InstructionDefinition('LD_B_HL', 0, 2),
    0x4e: InstructionDefinition('LD_C_HL', 0, 2),
    0x56: InstructionDefinition('LD_D_HL', 0, 2),
    0x5e: InstructionDefinition('LD_E_HL', 0, 2),
    0x66: InstructionDefinition('LD_H_HL', 0, 2),
    0x6e: InstructionDefinition('LD_L_HL', 0, 2),
    0x7e: InstructionDefinition('LD_A_HL', 0, 2),

    0x06: InstructionDefinition('LD_B_D8', 1, 2),
    0x0e: InstructionDefinition('LD_C_D8', 1, 2),
    0x16: InstructionDefinition('LD_D_D8', 1, 2),
    0x1e: InstructionDefinition('LD_E_D8', 1, 2),
    0x26: InstructionDefinition('LD_H_D8', 1, 2),
    0x2e: InstructionDefinition('LD_L_D8', 1, 2),
    0x3e: InstructionDefinition('LD_A_D8', 1, 2),
    0x36: InstructionDefinition('LD_HL_D8', 1, 3),

    0x01: InstructionDefinition('LD_BC_D16', 2, 3),
    0x11: InstructionDefinition('LD_DE_D16', 2, 3),
    0x21: InstructionDefinition('LD_HL_D16', 2, 3),

    0x31: InstructionDefinition('LD_SP_D16', 2, 3),
    0x08: InstructionDefinition('LD_D16_SP', 2, 5),
    0xf9: InstructionDefinition('LD_SP_HL', 0, 1),
    0xf8: InstructionDefinition('LD_HL_SPe', 1, 3),

    0x02: InstructionDefinition('LD_BC_A', 0, 2),
    0x12: InstructionDefinition('LD_DE_A', 0, 2),
    0xea: InstructionDefinition('LD_D16_A', 2, 4),
    0xe0: InstructionDefinition('LDH_D8_A', 1, 3),
    0xe2: InstructionDefinition('LDH_C_A', 0, 2),
    0x22: InstructionDefinition('LD_HLI_A', 0, 2),
    0x32: InstructionDefinition('LD_HLD_A', 0, 2),

    0x0a: InstructionDefinition('LD_A_BC', 0, 2),
    0x1a: InstructionDefinition('LD_A_DE', 0, 2),
    0xfa: InstructionDefinition('LD_A_D16', 2, 4),
    0xf0: InstructionDefinition('LD_A_D8', 1, 3),
    0xf2: InstructionDefinition('LD_A_C', 0, 2),
    0x2a: InstructionDefinition('LD_A_HLI', 0, 2),
    0x3a: InstructionDefinition('LD_A_HLD', 0, 2)


}

PREFIX_INSTRUCTION_DICT = {

    
    0x40: InstructionDefinition('BIT_B_0', 0, 2),
    0x42: InstructionDefinition('BIT_D_0', 0, 2),
    0x41: InstructionDefinition('BIT_C_0', 0, 2),
    0x43: InstructionDefinition('BIT_E_0', 0, 2),
    0x44: InstructionDefinition('BIT_H_0', 0, 2),
    0x45: InstructionDefinition('BIT_L_0', 0, 2),
    0x46: InstructionDefinition('BIT_HL_0', 0, 2),
    0x47: InstructionDefinition('BIT_A_0', 0, 2),

    0x48: InstructionDefinition('BIT_B_1', 0, 2),
    0x49: InstructionDefinition('BIT_C_1', 0, 2),
    0x4a: InstructionDefinition('BIT_D_1', 0, 2),
    0x4b: InstructionDefinition('BIT_E_1', 0, 2),
    0x4c: InstructionDefinition('BIT_H_1', 0, 2),
    0x4d: InstructionDefinition('BIT_L_1', 0, 2),
    0x4e: InstructionDefinition('BIT_HL_1', 0, 2),
    0x4f: InstructionDefinition('BIT_A_1', 0, 2),

    0x50: InstructionDefinition('BIT_B_2', 0, 2),
    0x51: InstructionDefinition('BIT_C_2', 0, 2),
    0x52: InstructionDefinition('BIT_D_2', 0, 2),
    0x53: InstructionDefinition('BIT_E_2', 0, 2),
    0x54: InstructionDefinition('BIT_H_2', 0, 2),
    0x55: InstructionDefinition('BIT_L_2', 0, 2),
    0x56: InstructionDefinition('BIT_HL_2', 0, 2),
    0x57: InstructionDefinition('BIT_A_2', 0, 2),

    0x58: InstructionDefinition('BIT_B_3', 0, 2),
    0x59: InstructionDefinition('BIT_C_3', 0, 2),
    0x5a: InstructionDefinition('BIT_D_3', 0, 2),
    0x5b: InstructionDefinition('BIT_E_3', 0, 2),
    0x5c: InstructionDefinition('BIT_H_3', 0, 2),
    0x5d: InstructionDefinition('BIT_L_3', 0, 2),
    0x5e: InstructionDefinition('BIT_HL_3', 0, 2),
    0x5f: InstructionDefinition('BIT_A_3', 0, 2),

    0x60: InstructionDefinition('BIT_B_4', 0, 2),
    0x61: InstructionDefinition('BIT_C_4', 0, 2),
    0x62: InstructionDefinition('BIT_D_4', 0, 2),
    0x63: InstructionDefinition('BIT_E_4', 0, 2),
    0x64: InstructionDefinition('BIT_H_4', 0, 2),
    0x65: InstructionDefinition('BIT_L_4', 0, 2),
    0x66: InstructionDefinition('BIT_HL_4', 0, 2),
    0x67: InstructionDefinition('BIT_A_4', 0, 2),

    0x68: InstructionDefinition('BIT_B_5', 0, 2),
    0x69: InstructionDefinition('BIT_C_5', 0, 2),
    0x6a: InstructionDefinition('BIT_D_5', 0, 2),
    0x6b: InstructionDefinition('BIT_E_5', 0, 2),
    0x6c: InstructionDefinition('BIT_H_5', 0, 2),
    0x6d: InstructionDefinition('BIT_L_5', 0, 2),
    0x6e: InstructionDefinition('BIT_HL_5', 0, 2),
    0x6f: InstructionDefinition('BIT_A_5', 0, 2),

    0x70: InstructionDefinition('BIT_B_6', 0, 2),
    0x71: InstructionDefinition('BIT_C_6', 0, 2),
    0x72: InstructionDefinition('BIT_D_6', 0, 2),
    0x73: InstructionDefinition('BIT_E_6', 0, 2),
    0x74: InstructionDefinition('BIT_H_6', 0, 2),
    0x75: InstructionDefinition('BIT_L_6', 0, 2),
    0x76: InstructionDefinition('BIT_HL_6', 0, 2),
    0x77: InstructionDefinition('BIT_A_6', 0, 2),

    0x78: InstructionDefinition('BIT_B_7', 0, 2),
    0x79: InstructionDefinition('BIT_C_7', 0, 2),
    0x7a: InstructionDefinition('BIT_D_7', 0, 2),
    0x7b: InstructionDefinition('BIT_E_7', 0, 2),
    0x7c: InstructionDefinition('BIT_H_7', 0, 2),
    0x7d: InstructionDefinition('BIT_L_7', 0, 2),
    0x7e: InstructionDefinition('BIT_HL_7', 0, 2),
    0x7f: InstructionDefinition('BIT_A_7', 0, 2),

}


## DAA
## LD r8,r8
## LD r8,n8
## LD r16,n16
## LD [HL],r8
## LD [HL],n8
## LD r8,[HL]
## LD [r16],A
## LD [n16],A
## LDH [n16],A
## LDH [C],A
## LD A,[r16]
## LD A,[n16]
## LDH A,[n16]
## LDH A,[C]
## LD [HLI],A
## LD [HLD],A
## LD A,[HLD]
## LD A,[HLI]
## LD SP,n16
## LD [n16],SP
## LD HL,SP+e8
## LD SP,HL
## NOP
## OR A,r8
## OR A,[HL]
## OR A,n8
## POP AF
## POP r16
## PUSH AF
## PUSH r16
## RES u3,r8
## RES u3,[HL]
## RET
## RET cc
## RETI
## RL r8
## RL [HL]
## RLA
## RLC r8
## RLC [HL]
## RLCA
## RR r8
## RR [HL]
## RRA
## RRC r8
## RRC [HL]
## RRCA
## RST vec
## SBC A,r8
## SBC A,[HL]
## SBC A,n8
## SCF
## SET u3,r8
## SET u3,[HL]
## SLA r8
## SLA [HL]
## SRA r8
## SRA [HL]
## SRL r8
## SRL [HL]
## STOP
## SUB A,r8
## SUB A,[HL]
## SUB A,n8
## SWAP r8
## SWAP [HL]
## XOR A,r8
## XOR A,[HL]
## XOR A,n8
