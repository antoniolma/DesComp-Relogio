import os

# Arquivos de entrada e saída
auto_inputASM = 'arq/ASM_relogio_teste.txt'
auto_outputBIN = 'arq/BIN.txt'
auto_outputMIF = 'arq/initROM.mif'

# Usar 9 bits (True) ou 8 bits (False)
noveBits = True

# Dicionário de mnemônicos para OPCODEs (hexadecimal)
mne = {
    "NOP":  "0",
    "LDA":  "1",
    "SOMA": "2",
    "SUB":  "3",
    "LDI":  "4",
    "STA":  "5",
    "JMP":  "6",
    "JEQ":  "7",
    "CEQ":  "8",
    "JSR":  "9",
    "RET":  "A",
    "ADDi": "B",
    "CGT":  "C",
    "JGT":  "D"
}

# Tabela de labels/flags
labels = {}


def get_labels(lines):
    """
    Varre o código identificando linhas que definem labels (terminam em ':'),
    e armazena em 'labels' o endereço (posição de instrução) correspondente.
    Instruções (não-labels) incrementam o contador de posição.
    """
    labels.clear()
    addr = 0
    for raw in lines:
        text = raw.split('#', 1)[0].strip()
        # label-only line
        if text.endswith(':'):
            tag = text[:-1]
            labels[tag] = addr
        # instrução válida
        elif text:
            addr += 1


def converteArroba(line):
    parts = line.split('@')
    key = parts[1]
    try:
        num = int(key)
    except ValueError:
        # se for label, buscado no dicionário
        num = labels.get(key, 0)
    hex_str = hex(num)[2:].upper().zfill(2)
    parts[1] = hex_str
    return ''.join(parts)


def converteArroba9bits(line):
    parts = line.split('@')
    key = parts[1]
    try:
        num = int(key)
    except ValueError:
        num = labels.get(key, 0)
    # define o bit extra para >255
    if num > 255:
        num -= 256
        h = hex(num)[2:].upper().zfill(2)
        parts[1] = '" & \'1\' & x"' + h
    else:
        h = hex(num)[2:].upper().zfill(2)
        parts[1] = '" & \'0\' & x"' + h
    return ''.join(parts)


def converteCifrao(line):
    parts = line.split('$')
    num = int(parts[1])
    hex_str = hex(num)[2:].upper().zfill(2)
    parts[1] = hex_str
    return ''.join(parts)


def converteCifrao9bits(line):
    parts = line.split('$')
    num = int(parts[1])
    if num > 255:
        num -= 256
        h = hex(num)[2:].upper().zfill(2)
        parts[1] = '" & \'1\' & x"' + h
    else:
        h = hex(num)[2:].upper().zfill(2)
        parts[1] = '" & \'0\' & x"' + h
    return ''.join(parts)


def defineComentario(raw):
    """
    Retorna somente o texto de comentário (após '#'), sem o símbolo.
    Se não houver '#', retorna string vazia.
    """
    if '#' in raw:
        return raw.split('#', 1)[1].strip()
    return ''


def defineInstrucao(raw):
    """
    Retorna somente a parte da instrução antes de '#', sem espaços extras.
    """
    return raw.split('#', 1)[0].strip()


def trataMnemonico(instrucao):
    """
    Converte o mnemônico inicial em seu opcode (hexa) e junta com o restante.
    Ex: 'JSR @14' -> '9@14'
    """
    parts = instrucao.replace("\t", " ").split()
    op = mne.get(parts[0], '0')
    rest = ''.join(parts[1:]) if len(parts) > 1 else ''
    return op + rest


# ======= Leitura e mapeamento de labels =======
with open(auto_inputASM, 'r') as f:
    asm_lines = f.readlines()
    get_labels(asm_lines)

# ======= Gerar BIN.txt =======
with open(auto_outputBIN, 'w') as fout:
    cont = 0
    for raw in asm_lines:
        stripped = raw.strip('\n')
        core = stripped.split('#', 1)[0].strip()
        # Ignora linhas vazias, comentários só, espaços iniciais e labels
        if not core or stripped.startswith(' ') or core.endswith(':'):
            continue
        # Captura comentário (ou define instrução se não houver)
        comment = defineComentario(stripped) or defineInstrucao(stripped)
        instr_clean = defineInstrucao(stripped)
        # Converte mnemônico para opcode
        bin_code = trataMnemonico(instr_clean)
        # Trata imediatos '@'
        if '@' in bin_code:
            bin_code = converteArroba9bits(bin_code) if noveBits else converteArroba(bin_code)
        # Trata imediatos '$'
        elif '$' in bin_code:
            bin_code = converteCifrao9bits(bin_code) if noveBits else converteCifrao(bin_code)
        # Sem imediato
        else:
            if noveBits:
                bin_code = bin_code + '" & \'0\' & x"00'
            else:
                bin_code = bin_code + '00'
        # Escreve no arquivo BIN
        line_out = f"{cont}. tmp({cont}) := x\"{bin_code}\"; -- {comment}\n"
        fout.write(line_out)
        print(line_out, end='')
        cont += 1

# ======= Gerar initROM.mif =======
# Pressupõe que exista um arquivo template initROM.mif com cabeçalho
with open(auto_outputMIF, 'r') as f_header:
    header = f_header.readlines()
with open(auto_outputBIN, 'r') as f_bin:
    bin_lines = f_bin.readlines()
with open(auto_outputMIF, 'w') as f_mif:
    # Escrever cabeçalho (exemplo: 21 linhas)
    for i, h in enumerate(header):
        if i < 21:
            f_mif.write(h)
    # Escrever dados convertidos
    for b in bin_lines:
        # Remove formatação e comentário
        clean = ''.join(ch for ch in b if ch not in 'tmp()=x";')
        clean = clean.split('--')[0].strip() + '\n'
        f_mif.write(clean)
    f_mif.write('END;')
