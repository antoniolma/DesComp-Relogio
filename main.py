#!/usr/bin/env python3
"""
Assembler para arquitetura Register-Memory (17 bits/instr):
  5 bits opcode, 3 bits Rd, 1 bit MSB do imediato/endereço, 8 bits valor.
Lê 'ASM.txt' e produz:
  - 'BIN.txt' com linhas VHDL: tmp(i) := "op" & "rd" & 'b' & x"XX";
  - 'initROM.mif' com conteúdo binário puro.
"""

# Mnemônico → opcode (hexadecimal, 5 bits)
mne = {
    "NOP":   "0",
    "LDR":   "1",
    "SOMA":  "2",
    "SUB":   "3",
    "LDI":   "4",
    "STR":   "5",
    "JMP":   "6",
    "JEQ":   "7",
    "CEQ":   "8",
    "JSR":   "9",
    "RET":   "A",
    "ADDi":  "B",
    "CGT":   "C",
    "JGT":   "D",
    "SUBi":  "E",
    "CLT":   "F",
    "JLT":   "10",
    "CEQi":  "11"
}

# Registradores R0–R7 → 3 bits
reg_map = { f"R{i}": format(i, '03b') for i in range(8) }

def parse_line(line):
    """Retorna (mnemonic, operands, comment) ou None se inválida."""
    # ignora linhas vazias, comentários puros ou iniciadas por espaço
    if line.startswith(' ') or not line.strip() or line.lstrip().startswith('#'):
        return None

    # separa comentário
    parts = line.strip().split('#', 1)
    instr   = parts[0].strip()
    comment = parts[1].strip() if len(parts) > 1 else instr

    # usa split(None,1) para separar MNEMONIC do resto
    tokens = instr.split(None, 1)
    mnemonic = tokens[0]
    operands = tokens[1] if len(tokens) > 1 else ""

    return mnemonic, operands, comment


def to_bin(val, bits):
    return format(val, f'0{bits}b')

def encode_operand(token: str):
    """
    Recebe:
      - '@123'  → address
      - '$45'   → imediato
      - '7'     → número puro (tratado como address/imediato)
    Retorna (msb, hex8):
      - msb  = '1' se valor>255, senão '0'
      - hex8 = valor_low em 2 dígitos hex (00–FF)
    """
    # limpa eventual espaço
    token = token.strip()

    if token.startswith('@'):
        val = int(token[1:])
    elif token.startswith('$'):
        val = int(token[1:])
    elif token.isdigit():
        val = int(token)
    else:
        # sem operando
        return '0', '00'

    msb = '1' if val > 255 else '0'
    low = val - 256 if val > 255 else val
    # **02X** garante '0A','0B',...'FF'
    return msb, format(low, '02X')

def assemble_instruction(mnemonic: str, operands: str):
    # 1) opcode 5 bits
    code = int(mne[mnemonic], 16)
    op5 = format(code, '05b')

    # 2) Registrador destino (3 bits)
    if mnemonic == "RET":
        rd3 = reg_map["R7"]
    else:
        # extrai Rd antes da vírgula, ou usa R0 por padrão
        if ',' in operands:
            rd_tok = operands.split(',',1)[0].strip()
        else:
            rd_tok = "R0"
        rd3 = reg_map.get(rd_tok, reg_map["R0"])

    # 3) Identifica o operando para MSB+8 bits
    tok = None
    if mnemonic in ("JMP", "JEQ", "JLT", "JGT", "JSR"):
        tok = operands.strip()
    elif ',' in operands:
        tok = operands.split(',', 1)[1].strip()

    # 4) Codifica MSB + 8 bits
    if tok:
        msb, hex8 = encode_operand(tok)
    else:
        msb, hex8 = '0', '00'

    return op5, rd3, msb, hex8

def main():
    instrs = []
    with open("arq/ASM_relogio_teste.txt") as f:
        for line in f:
            parsed = parse_line(line)
            if not parsed:
                continue
            m, ops, c = parsed
            op5, rd3, b, xx = assemble_instruction(m, ops)
            instrs.append((op5, rd3, b, xx, c))

    # gera BIN.txt
    with open("arq/BIN.txt", "w") as f:
        for i, (op5, rd3, b, xx, comment) in enumerate(instrs):
            f.write(
                f'tmp({i}) := "{op5}" & "{rd3}" & \'{b}\' & x"{xx}";\t-- {comment}\n'
            )

    # gera initROM.mif
    with open("arq/initROM.mif", "w") as f:
        f.write("WIDTH=17;\n")
        f.write(f"DEPTH={len(instrs)};\n")
        f.write("ADDRESS_RADIX=DEC;\n")
        f.write("DATA_RADIX=BIN;\n")
        f.write("CONTENT BEGIN\n")
        for i, (op5, rd3, b, xx, _) in enumerate(instrs):
            f.write(f"  {i} : {op5}{rd3}{b}{format(int(xx,16), '08b')};\n")
        f.write("END;\n")

if __name__ == "__main__":
    main()
