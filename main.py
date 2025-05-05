#!/usr/bin/env python3
"""
Assembler para arquitetura Register-Memory (17 bits/instr):
  5 bits opcode, 3 bits Rd, 1 bit MSB do imediato/endereço, 8 bits valor.
Lê 'ASM.txt' e produz:
  - 'BIN.txt' com linhas VHDL: tmp(i) := "op" & "rd" & 'b' & x"XX";
  - 'initROM.mif' com conteúdo binário puro.
"""

# Para facilitar a troca de qual arquivo deve ser lido e onde escrever (na main())
teste = False

# Mnemônico => opcode (hexadecimal, 5 bits)
mne = {
    "NOP":   "0", "LDR":   "1",  "SOMA":  "2",
    "SUB":   "3", "LDI":   "4",  "STR":   "5",
    "JMP":   "6", "JEQ":   "7",  "CEQ":   "8",
    "JSR":   "9", "RET":   "A",  "ADDi":  "B",
    "CGT":   "C", "JGT":   "D",  "SUBi":  "E",
    "CLT":   "F", "JLT":   "10", "CEQi":  "11"
}

# Registradores R0–R7 => 3 bits
reg_map = { f"R{i}": format(i, '03b') for i in range(8) }

def parse_line(line):
    """Retorna (mnemonic, operands, comment) ou None se for label/vazia/comentário."""
    raw = line.strip()
    # label?
    if raw.endswith(':'):
        return ('LABEL', raw[:-1], None)
    # ignora linhas vazias, comente puro ou iniciadas em espaço
    if not raw or raw.startswith('#') or line.startswith(' '):
        return None
    parts = raw.split('#',1)
    instr   = parts[0].strip()
    comment = parts[1].strip() if len(parts)>1 else instr
    tokens = instr.split(None,1)
    mnemonic = tokens[0]
    operands = tokens[1] if len(tokens)>1 else ""
    return mnemonic, operands, comment

def encode_operand(token, label_map):
    token = token.strip()
    # referência a label?
    if token.startswith('@') and not token[1:].isdigit():
        val = label_map[token[1:]]
    else:
        # cai na sua lógica antiga para @$ e dígitos
        if token.startswith('@') or token.startswith('$') or token.isdigit():
            val = int(token.lstrip('@$'))
        else:
            return '0','00'
    msb = '1' if val>255 else '0'
    low = val-256 if val>255 else val
    return msb, format(low,'02X')

def assemble_instruction(mnemonic: str, operands: str, label_map):
    # 1) opcode 5 bits
    code = int(mne[mnemonic], 16)
    op5 = format(code, '05b')

    # 2) Registrador destino (3 bits)
    if mnemonic == "RET":
        rd3 = reg_map["R0"]
    else:
        if ',' in operands:
            rd_tok = operands.split(',',1)[0].strip()
        else:
            rd_tok = "R0"
        rd3 = reg_map.get(rd_tok, reg_map["R0"])

    # 3) inicializa tok para o operando
    tok = None

    #    branches e JSR usam o próprio operando
    if mnemonic in ("JMP", "JEQ", "JLT", "JGT", "JSR"):
        tok = operands.strip()
    #    instruções com vírgula pegam só o segundo pedaço
    elif ',' in operands:
        tok = operands.split(',', 1)[1].strip()

    # 4) Codifica MSB + 8 bits
    if tok:
        bit_ms, hex8 = encode_operand(tok, label_map)
    else:
        bit_ms, hex8 = '0', '00'

    return op5, rd3, bit_ms, hex8


def main():
    # 1ª passagem: lê todas as linhas e constrói label_map + lista de instruções “puras”
    if teste:
        arq_leitura = "arq/ASM_teste.txt"
    else:
        arq_leitura = "arq/ASM.txt"

    raw_lines = open(arq_leitura, encoding="utf-8", errors="ignore").read().splitlines()
    label_map = {}
    instr_lines = []
    pc = 0
    for line in raw_lines:
        parsed = parse_line(line)
        if parsed is None:
            continue
        if parsed[0] == 'LABEL':
            label = parsed[1]
            label_map[label] = pc
        else:
            instr_lines.append(line)
            pc += 1

    # 2ª passagem: monta cada instrução usando label_map
    instrs = []
    for line in instr_lines:
        mnemonic, ops, comment = parse_line(line)
        op5, rd3, b, xx = assemble_instruction(mnemonic, ops, label_map)
        instrs.append((op5, rd3, b, xx, line))

    # gera BIN.txt
    if teste:
        arq_escrita = "arq/BIN_teste.txt"
    else:
        arq_escrita = "arq/BIN.txt"
    with open(arq_escrita, "w", encoding="utf-8", errors="ignore") as f:
        for i, (op5, rd3, b, xx, comment) in enumerate(instrs):
            f.write(
                f'tmp({i}) := "{op5}" & "{rd3}" & \'{b}\' & x"{xx}";\t-- {comment}\n'
            )

    # gera initROM.mif
    with open("arq/initROM.mif", "w", encoding="utf-8", errors="ignore") as f:
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
