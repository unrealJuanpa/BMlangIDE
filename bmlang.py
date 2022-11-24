import re
import os
import sys
from colorama import Fore, Back, Style


os.system('cls')

csintaxErr = 0
tmpvarc = 0
twc = ""
asm = ".386\n.model flat,stdcall\noption casemap:none\n"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

twc = ""

def match(regex, sent):
    return bool(re.fullmatch(regex, sent))

def split_logop_and_add(sent):
    global twc
    global tmpvarc
    global asm
    # a<3 && a<>0 || a<>1 || a==1
    # a<3 #&&# a<>0 #||# a<>1 #||# a==1
    # [a<3, &&, a<>0, ||, a<>1, ||, a==1]

    sent = sent.replace("&&", '#&&#').replace('||', '#||#').split("#")

    

    ops = []

    inicial = tmpvarc
    # a<3 && a<>0 && a==5 || b<>7

    for i in range(1, len(sent), 2):
        ops.append(sent[i])

    for i in range(0, len(sent), 2):
        twc += f'\t#t{tmpvarc}={sent[i].strip()};\n'
        tmpvarc += 1

    final = tmpvarc

    if len(sent) == 3:
        twc += f'\t#t{tmpvarc} = t{inicial} {sent[1]} t{inicial + 1};\n'
        tmpvarc += 1
    elif len(sent) > 3:
        twc += f'\t#t{tmpvarc} = t{inicial} {sent[1]} t{inicial + 1};\n'
        tmpvarc += 1

        ops.pop(0)

        for i in range(inicial+2, final, 1):
            vip = ops.pop(0)
            #input(vip)
            twc += f'\t#t{tmpvarc} = t{tmpvarc-1} {vip} t{i};\n'
            tmpvarc += 1




def split_op_and_add(sent, level=1):
    global twc
    global tmpvarc
    global asm

    asm += f'\tmov eax, 0\n'

    tabs = "\t" * level


    if sent.endswith('++'):
        varnamefinal = sent.replace('++', '').strip()
        twc += f'{tabs}{varnamefinal}={varnamefinal}+1;\n'

        asm += f'\tmov eax, [{varnamefinal}]\n'
        asm += f'\tadd eax, 1\n'
        asm += f'\tmov [{varnamefinal}], eax\n'
        return 0

    sent = sent.replace('+', '#+')
    sent = sent.replace('-', '#-')
    sent = sent.replace('*', '#*')
    sent = sent.replace('/', '#/')
    sent = sent.replace('^', '#^')
    sent = sent.replace(';', '')

    varnamefinal = sent.split("=")[0].strip()
    ops = sent.split("=")[1].strip()
    ops = ops.split('#')

    ops2 = []

    for idx, i in enumerate(ops):
        if i.startswith('^'):
            for p in range(int(i.split('^')[1])-1):
                ops2.append(f'*{ops[idx-1]}')
        else:
            ops2.append(i)

    ops = ops2

    if len(ops) == 1:
        twc += f'{tabs}{varnamefinal}={ops[0]};\n'
        asm += f'\tmov [{varnamefinal}], {ops[0]}\n'
    elif len(ops) == 2:
        twc += f'{tabs}{varnamefinal}={"".join(ops[0:2])};\n'

        norm = ops[0]
        if match(rules['identif'], norm):
            asm += f'\tmov eax, [{norm}]\n'
        else:
            asm += f'\tmov eax, {norm}\n'

        if ops[1].startswith('+'):
            norm = ops[1].replace('+', '')
            if match(rules['identif'], norm):
                asm += f'\tadd eax, [{norm}]\n'
            else:
                asm += f'\tadd eax, {norm}\n'
        elif ops[1].startswith('-'):
            norm = ops[1].replace('-', '')
            if match(rules['identif'], norm):
                asm += f'\tsub eax, [{norm}]\n'
            else:
                asm += f'\tsub eax, {norm}\n'
        elif ops[1].startswith('*'):
            norm = ops[1].replace('*', '')

            if match(rules['identif'], norm):
                asm += f'\tmul eax, [{norm}]\n'
            else:
                asm += f'\tmul eax, {norm}\n'

        elif ops[1].startswith('/'):
            norm = ops[1].replace('/', '')

            if match(rules['identif'], norm):
                asm += f'\tdiv eax, [{norm}]\n'
            else:
                asm += f'\tdiv eax, {norm}\n'


        asm += f'\tmov [{varnamefinal}], eax\n'
    else:
        tmpvarc += 1
        twc += f'{tabs}#t{tmpvarc}={"".join(ops[0:2])};\n'

        for i in ops[2:]:
            tmpvarc += 1
            twc += f'{tabs}#t{tmpvarc}=t{tmpvarc-1}{i};\n'

        twc += f'{tabs}{varnamefinal}=#t{tmpvarc};\n'

        norm = ops[0]
        if match(rules['identif'], norm):
            asm += f'\tmov eax, [{norm}]\n'
        else:
            asm += f'\tmov eax, {norm}\n'

        for idxpl in range(1, len(ops)):
            if ops[idxpl].startswith('+'):
                norm = ops[idxpl].replace('+', '')
                if match(rules['identif'], norm):
                    asm += f'\tadd eax, [{norm}]\n'
                else:
                    asm += f'\tadd eax, {norm}\n'
            elif ops[idxpl].startswith('-'):
                norm = ops[idxpl].replace('-', '')
                if match(rules['identif'], norm):
                    asm += f'\tsub eax, [{norm}]\n'
                else:
                    asm += f'\tsub eax, {norm}\n'
            elif ops[idxpl].startswith('*'):
                norm = ops[idxpl].replace('*', '')

                if match(rules['identif'], norm):
                    asm += f'\tmul eax, [{norm}]\n'
                else:
                    asm += f'\tmul eax, {norm}\n'

            elif ops[idxpl].startswith('/'):
                norm = ops[idxpl].replace('/', '')

                if match(rules['identif'], norm):
                    asm += f'\tdiv eax, [{norm}]\n'
                else:
                    asm += f'\tdiv eax, {norm}\n'
                    
        asm += f'\tmov [{varnamefinal}], eax\n'




rules = {}

# tokens
rules['0masespacios'] = '( )*'
rules['1masespacios'] = '( )+'
rules['unsignentero'] = '[0-9]+'
rules['signentero'] = '(\-|())' + rules['unsignentero']
rules['letra'] = '[a-zA-Z]'
rules['identif'] = rules['letra'] + f'(({rules["unsignentero"]})|({rules["letra"]}))*'
rules['aritoperat'] = '(\+|\-|\*|/|\^)'
rules['idetifOuint'] = f'({rules["identif"]}|{rules["unsignentero"]})'
rules['concatAritOpBase'] = f'{rules["0masespacios"]}{rules["aritoperat"]}{rules["0masespacios"]}{rules["idetifOuint"]}'
rules['operacion'] = f'{rules["idetifOuint"]}({rules["concatAritOpBase"]})*{rules["0masespacios"]}'
rules['tuplaDeclaracionBase'] = f'(,){rules["0masespacios"]}{rules["identif"]}{rules["0masespacios"]}'
rules['puntoycoma'] = f'{rules["0masespacios"]}(;)'
rules['saltoespaciotab'] = '(\n|( )|\t)*'
rules['llaveInicio'] = '{'
rules['tkcinicio'] = '/\*'
rules['tkcfin'] = '\*/'
rules['stringcomentario'] = '[\10-\254]*'
rules['pi'] = '\('
rules['pf'] = '\)'
rules['logop'] = '(\<|\>|\<\=|\>\=|\=\=|\<\>)'
rules['identifoint'] = f'({rules["idetifOuint"]}|\-{rules["unsignentero"]})'
rules['signomas'] = '\+'
rules['operacion'] = f"({rules['operacion']}|{rules['idetifOuint']}{rules['0masespacios']}{rules['signomas']}{rules['signomas']})"
rules['lop'] = '((\&\&)|(\|\|))'

# reglas
rules['declaracion'] = f'(DEC){rules["1masespacios"]}{rules["identif"]}{rules["0masespacios"]}({rules["tuplaDeclaracionBase"]})*{rules["puntoycoma"]}'
rules['input'] = f'(INPUT){rules["1masespacios"]}{rules["identif"]}{rules["puntoycoma"]}'
rules['asignacion'] = f'{rules["identif"]}{rules["0masespacios"]}={rules["0masespacios"]}{rules["operacion"]}{rules["puntoycoma"]}'
rules['asignacion'] = f'({rules["asignacion"]}|{rules["identif"]}{rules["0masespacios"]}{rules["signomas"]}{rules["signomas"]}{rules["puntoycoma"]})'
rules['asignacionfor'] = f'({rules["identif"]}{rules["0masespacios"]}={rules["0masespacios"]}{rules["operacion"]}|{rules["identif"]}{rules["0masespacios"]}{rules["signomas"]}{rules["signomas"]})'

rules['output'] = f'(OUTPUT){rules["1masespacios"]}{rules["idetifOuint"]}{rules["puntoycoma"]}'
rules['initprogram'] = f'(MAIN){rules["0masespacios"]}'
rules['comentario'] = f'{rules["tkcinicio"]}{rules["stringcomentario"]}{rules["tkcfin"]}'
rules['llaveFin'] = '}'
rules['comparacion'] = f'{rules["0masespacios"]}{rules["identifoint"]}{rules["0masespacios"]}{rules["logop"]}{rules["0masespacios"]}{rules["identifoint"]}{rules["0masespacios"]}{rules["puntoycoma"]}{rules["0masespacios"]}'
rules['comparacionwhile'] = f'{rules["0masespacios"]}{rules["identifoint"]}{rules["0masespacios"]}{rules["logop"]}{rules["0masespacios"]}{rules["identifoint"]}{rules["0masespacios"]}({rules["lop"]}{rules["0masespacios"]}{rules["identifoint"]}{rules["0masespacios"]}{rules["logop"]}{rules["0masespacios"]}{rules["identifoint"]}{rules["0masespacios"]})*'
rules['for'] = f'(FOR){rules["0masespacios"]}{rules["pi"]}{rules["0masespacios"]}{rules["asignacion"]}{rules["0masespacios"]}{rules["comparacion"]}{rules["asignacionfor"]}{rules["0masespacios"]}{rules["pf"]}{rules["0masespacios"]}'
rules['while'] = f'(WHILE){rules["0masespacios"]}{rules["pi"]}{rules["comparacionwhile"]}{rules["pf"]}{rules["0masespacios"]}'
rules['if'] = f'(IF){rules["0masespacios"]}{rules["pi"]}{rules["comparacionwhile"]}{rules["pf"]}{rules["0masespacios"]}'
rules['else'] = f'(ELSE){rules["0masespacios"]}'

#rules['cualquiera'] = f'(({rules["saltoespaciotab"]})|({rules["declaracion"]})|({rules["input"]})|({rules["asignacion"]})|({rules["output"]}))*'

with open(sys.argv[1], 'r') as file:
    code = file.readlines()

code = ''.join(code)
code = re.sub("(/\*).*(\*/)", "", code)
code = re.sub("(\{)", "\n{\n", code)
code = re.sub("(\})", "\n}\n", code)
code = code.split('\n')
code = [c.strip() for c in code if len(c.strip()) > 0]
code.append("")

idx3 = 0

while idx3 < len(code) - 1:

    if match(rules['for'], code[idx3]) or match(rules['while'], code[idx3]) or match(rules['if'], code[idx3]) or match(rules['else'], code[idx3]):
        if not '{' == code[idx3+1]:
            code.insert(idx3+1, '{')
            code.insert(idx3+3, '}')

    idx3 += 1


def add_asmyo(sent, cmd, invert=False):
    global asm

    sent = sent.replace("WHILE", "").replace("(", "").replace(")", "").strip()
    final_asmcmps = []
    for i in sent.replace("&&", '#&&').replace('||', '#||').split("#"):
        final_asmcmps.append(i)

    if '==' in final_asmcmps[0]:
        vj = final_asmcmps[0].replace("==", '#').split('#')
        asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
        if invert:
            asm += f'\tJNE l{cmd}\n'
        else:
            asm += f'\tJE l{cmd}\n'
    elif '<>' in final_asmcmps[0]:
        vj = final_asmcmps[0].replace("<>", '#').split('#')
        asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
        if invert:
            asm += f'\tJE l{cmd}\n'
        else:
            asm += f'\tJNE l{cmd}\n'
    elif '<=' in final_asmcmps[0]:
        vj = final_asmcmps[0].replace("<=", '#').split('#')
        asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
        if invert:
            asm += f'\tJG l{cmd}\n'
        else:
            asm += f'\tJLE l{cmd}\n'
    elif '>=' in final_asmcmps[0]:
        vj = final_asmcmps[0].replace(">=", '#').split('#')
        asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
        if invert:
            asm += f'\tJL l{cmd}\n'
        else:
            asm += f'\tJGE l{cmd}\n'
    elif '<' in final_asmcmps[0]:
        vj = final_asmcmps[0].replace("<", '#').split('#')
        asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
        if invert:
            asm += f'\tJGE l{cmd}\n'
        else:
            asm += f'\tJL l{cmd}\n'
    elif '>' in final_asmcmps[0]:
        vj = final_asmcmps[0].replace(">", '#').split('#')
        asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
        if invert:
            asm += f'\tJLE {vj[0]}, {vj[1]}\n'
        else:
            asm += f'\tJG {vj[0]}, {vj[1]}\n'


code.pop(-1)

mainflag = 0
errorlist = []
comm = []

cmd = 1
idx = 0
asflag = True
while idx < len(code):
    sent = code[idx]
    sent = sent.strip()

    if True:
        if match(rules['initprogram'], sent): # cubierto 3w, asm
            twc += 'main:'
        elif match(rules['declaracion'], sent) and idx == 2: # cubierto 3w, asm
            vars = sent.replace(";", '').split(" ")[1].split(',')
            asm += '.data\n'
            for v in vars:
                asm += f'{v} DB 0\n'

        elif match(rules['input'], sent): # cubierto 3w, asm
            if asflag:
                asflag = False
                asm += 'start:\n'

            v = sent.split(' ')[1].strip().replace(';', '')
            twc += '\tcall input;\n'
            twc += f'\tpop {v};\n'

            asm += '\tmov ah,01h\n'
            asm += '\tint 21h\n'
            asm += f'\tmov [{v}], al\n'

        elif match(rules['asignacion'], sent): # cubierto 3w, asm
            if asflag:
                asflag = False
                asm += 'start:\n'

            split_op_and_add(sent.replace(';', ''))
        elif match(rules['output'], sent): # cubierto 3w, asm
            if asflag:
                asflag = False
                asm += 'start:\n'

            v = sent.split(' ')[1].strip().replace(';', '')
            twc += f'\tpush {v};\n'
            twc += '\tcall output;\n'

            if match(rules['identif'], v):
                asm += f'\tmov dl, [{v}]\n'
            else:
                asm += f'\tmov dl, {v}\n'

            asm += f'\tmov ah, 02h\n'
            asm += f'\tint 21h\n'

        elif match(rules['llaveFin'], sent): # cubierto 3w, asm
            mainflag -= 1
        elif match(rules['llaveInicio'], sent): # cubierto 3w, asm
            mainflag += 1

        elif match(rules['while'], sent):
            if asflag:
                asflag = False
                asm += 'start:\n'

            split_logop_and_add(sent.replace("WHILE", "").replace("(", "").replace(")", "").strip())
            add_asmyo(sent, cmd+1, True)
            twc += f'\tifZ t{tmpvarc-1} goto l{cmd+1};\n'
            twc += f'#l{cmd}:'
            asm += f'l{cmd}:\n'

            clk = 0
            for idx4 in range(idx+1, len(code)):
                if code[idx4] == '{':
                    clk += 1
                elif code[idx4] == '}':
                    clk -= 1
                else:
                    if match(rules['input'], code[idx4]):
                        v = code[idx4].split(' ')[1].strip().replace(';', '')
                        twc += '\tcall input;\n'
                        twc += f'\tpop {v};\n'

                        asm += '\tmov ah,01h\n'
                        asm += '\tint 21h\n'
                        asm += f'\tmov [{v}], al\n'
                    elif match(rules['asignacion'], code[idx4]):
                        split_op_and_add(code[idx4].replace(';', ''))
                    elif match(rules['output'], code[idx4]):
                        v = code[idx4].split(' ')[1].strip().replace(';', '')
                        twc += f'\tpush {v};\n'
                        twc += '\tcall output;\n'

                        if match(rules['identif'], v):
                            asm += f'\tmov dl, [{v}]\n'
                        else:
                            asm += f'\tmov dl, {v}\n'

                        asm += f'\tmov ah, 02h\n'
                        asm += f'\tint 21h\n'

                if clk == 0:
                    break

            
            split_logop_and_add(sent.replace("WHILE", "").replace("(", "").replace(")", "").strip())
            twc += f'\tif t{tmpvarc-1} goto l{cmd};\n'
            twc += f'l{cmd+1}:'
            
            add_asmyo(sent, cmd)
            asm += f'l{cmd+1}:\n'
            

            cmd += 1
            idx = idx4

        elif match(rules['for'], sent):
            if asflag:
                asflag = False
                asm += 'start:\n'

            sent = sent.replace("FOR", "").replace("(", "").replace(")", "").strip().split(';')
            sent = [x.strip().replace(';', '') for x in sent]
            
            split_op_and_add(sent[0])
            split_logop_and_add(sent[1])
            add_asmyo(sent[1], cmd+1, True)
            twc += f'\tifZ t{tmpvarc-1} goto l{cmd+1};\n'
            twc += f'#l{cmd}:'
            asm += f'l{cmd}:\n'


            clk = 0
            for idx4 in range(idx+1, len(code)):
                if code[idx4] == '{':
                    clk += 1
                elif code[idx4] == '}':
                    clk -= 1
                else:
                    if match(rules['input'], code[idx4]):
                        v = code[idx4].split(' ')[1].strip().replace(';', '')
                        twc += '\tcall input;\n'
                        twc += f'\tpop {v};\n'

                        asm += '\tmov ah,01h\n'
                        asm += '\tint 21h\n'
                        asm += f'\tmov [{v}], al\n'

                    elif match(rules['asignacion'], code[idx4]):
                        split_op_and_add(code[idx4].replace(';', ''))
                    elif match(rules['output'], code[idx4]):
                        v = code[idx4].split(' ')[1].strip().replace(';', '')
                        twc += f'\tpush {v};\n'
                        twc += '\tcall output;\n'

                        if match(rules['identif'], v):
                            asm += f'\tmov dl, [{v}]\n'
                        else:
                            asm += f'\tmov dl, {v}\n'

                        asm += f'\tmov ah, 02h\n'
                        asm += f'\tint 21h\n'

                if clk == 0:
                    break

            
            split_op_and_add(sent[2])
            split_logop_and_add(sent[1])
            twc += f'\tif t{tmpvarc-1} goto l{cmd};\n'
            twc += f'#l{cmd+1}:'


            '''
            sent = sent[1]
            final_asmcmps = []
            for i in sent.replace("&&", '#&&').replace('||', '#||').split("#"):
                final_asmcmps.append(i)

            if '==' in final_asmcmps[0]:
                vj = final_asmcmps[0].replace("==", '#').split('#')
                asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                asm += f'\tJE l{cmd}\n'
            elif '<>' in final_asmcmps[0]:
                vj = final_asmcmps[0].replace("<>", '#').split('#')
                asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                asm += f'\tJNE l{cmd}\n'
            elif '<=' in final_asmcmps[0]:
                vj = final_asmcmps[0].replace("<=", '#').split('#')
                asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                asm += f'\tJLE l{cmd}\n'
            elif '>=' in final_asmcmps[0]:
                vj = final_asmcmps[0].replace(">=", '#').split('#')
                asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                asm += f'\tJGE l{cmd}\n'
            elif '<' in final_asmcmps[0]:
                vj = final_asmcmps[0].replace("<", '#').split('#')
                asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                asm += f'\tJL l{cmd}\n'
            elif '>' in final_asmcmps[0]:
                vj = final_asmcmps[0].replace(">", '#').split('#')
                asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                asm += f'\tJG {vj[0]}, {vj[1]}\n'
            '''

            add_asmyo(sent[1], cmd)
            
            asm += f'l{cmd+1}:\n'

            cmd += 1
            idx = idx4

        elif match(rules['if'], sent):
            if asflag:
                asflag = False
                asm += 'start:\n'

            split_logop_and_add(sent.replace("IF", '').replace("(", "").replace(")", "").strip())
            twc += f'\tifZ t{tmpvarc-1} goto l{cmd};\n'

            sent = sent.replace("IF", '').replace("(", "").replace(")", "").strip()
            final_asmcmps = []
            for i in sent.replace("&&", '#&&').replace('||', '#||').split("#"):
                final_asmcmps.append(i)

            if '==' in final_asmcmps[0]:
                vj = final_asmcmps[0].replace("==", '#').split('#')
                asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                asm += f'\tJE l{cmd}\n'
            elif '<>' in final_asmcmps[0]:
                vj = final_asmcmps[0].replace("<>", '#').split('#')
                asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                asm += f'\tJNE l{cmd}\n'
            elif '<=' in final_asmcmps[0]:
                vj = final_asmcmps[0].replace("<=", '#').split('#')
                asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                asm += f'\tJLE l{cmd}\n'
            elif '>=' in final_asmcmps[0]:
                vj = final_asmcmps[0].replace(">=", '#').split('#')
                asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                asm += f'\tJGE l{cmd}\n'
            elif '<' in final_asmcmps[0]:
                vj = final_asmcmps[0].replace("<", '#').split('#')
                asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                asm += f'\tJL l{cmd}\n'
            elif '>' in final_asmcmps[0]:
                vj = final_asmcmps[0].replace(">", '#').split('#')
                asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                asm += f'\tJG {vj[0]}, {vj[1]}\n'

            
            tmpcomp = tmpvarc-1

            clk = 0
            for idx4 in range(idx+1, len(code)):
                if code[idx4] == '{':
                    clk += 1
                elif code[idx4] == '}':
                    clk -= 1
                else:
                    if match(rules['input'], code[idx4]):
                        v = code[idx4].split(' ')[1].strip().replace(';', '')
                        twc += '\tcall input;\n'
                        twc += f'\tpop {v};\n'
                    elif match(rules['asignacion'], code[idx4]):
                        split_op_and_add(code[idx4].replace(';', ''))
                    elif match(rules['output'], code[idx4]):
                        v = code[idx4].split(' ')[1].strip().replace(';', '')
                        twc += f'\tpush {v};\n'
                        twc += '\tcall output;\n'

                if clk == 0:
                    break

            twc += f'#l{cmd}:'
            cmd += 1
            idx = idx4 + 1

            if match(rules['else'], code[idx]):
                twc += f'\tif t{tmpcomp} goto l{cmd};\n'


                sent = sent.replace("IF", '').replace("(", "").replace(")", "").strip()
                final_asmcmps = []
                for i in sent.replace("&&", '#&&').replace('||', '#||').split("#"):
                    final_asmcmps.append(i)

                if '==' in final_asmcmps[0]:
                    vj = final_asmcmps[0].replace("==", '#').split('#')
                    asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                    asm += f'\tJE l{cmd}\n'
                elif '<>' in final_asmcmps[0]:
                    vj = final_asmcmps[0].replace("<>", '#').split('#')
                    asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                    asm += f'\tJNE l{cmd}\n'
                elif '<=' in final_asmcmps[0]:
                    vj = final_asmcmps[0].replace("<=", '#').split('#')
                    asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                    asm += f'\tJLE l{cmd}\n'
                elif '>=' in final_asmcmps[0]:
                    vj = final_asmcmps[0].replace(">=", '#').split('#')
                    asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                    asm += f'\tJGE l{cmd}\n'
                elif '<' in final_asmcmps[0]:
                    vj = final_asmcmps[0].replace("<", '#').split('#')
                    asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                    asm += f'\tJL l{cmd}\n'
                elif '>' in final_asmcmps[0]:
                    vj = final_asmcmps[0].replace(">", '#').split('#')
                    asm += f'\tcmp {vj[0].strip()}, {vj[1].strip()}\n'
                    asm += f'\tJG {vj[0]}, {vj[1]}\n'



                clk = 0
                for idx4 in range(idx+1, len(code)):
                    if code[idx4] == '{':
                        clk += 1
                    elif code[idx4] == '}':
                        clk -= 1
                    else:
                        if match(rules['input'], code[idx4]):
                            v = code[idx4].split(' ')[1].strip().replace(';', '')
                            twc += '\tcall input;\n'
                            twc += f'\tpop {v};\n'
                        elif match(rules['asignacion'], code[idx4]):
                            split_op_and_add(code[idx4].replace(';', ''))
                        elif match(rules['output'], code[idx4]):
                            v = code[idx4].split(' ')[1].strip().replace(';', '')
                            twc += f'\tpush {v};\n'
                            twc += '\tcall output;\n'

                    if clk == 0:
                        break

                twc += f'#l{cmd}:'
                cmd += 1

            idx = idx4
        else:
            errorlist.append((idx+1, sent))

    idx += 1


asm += 'end start\n'
asm += f'ret\n'

#print de codigo intermedio

if not mainflag == 0:
    errorlist.append(('del inicio y fin', 'Declaracion del MAIN incorrecta, verifique que exista, que se inicie y se cierre de forma correcta!'))

csintaxErr = 0
for idx, sent in errorlist:
    csintaxErr += 1
    print(f'{bcolors.FAIL}ERROR #{csintaxErr}:', end='')
    print(f'{bcolors.ENDC}\tSintaxis incorrecta en la linea {idx} del archivo {sys.argv[1]}.')
    print(f'\t\tLa linea contiene una instruccion no reconocida!')
    print(f'\t\tDetalles: {sent}')

    if ('INPUT' in sent or '=' in sent or 'OUTPUT' in sent or 'DEC' in sent) and not sent.endswith(';'):
        print(Back.LIGHTYELLOW_EX + f'\t\tSugerencia: Recuerde agregar punto y coma al final de las instrucciones {sent.split(" ")[0]}!' + Back.RESET)
    print('\n')

if len(errorlist) == 0:
    print('Sintaxis correcta!')


if len(errorlist) == 0 or len(errorlist) > 1:
    print(f'{csintaxErr} problemas encontrados.')
else:
    print(f'{csintaxErr} problema encontrado.')

print()

if csintaxErr == 0:
    fmsg = '-'*10 + ' Codigo de tres direcciones generado ' + '-'*10
    print(fmsg)
    print(twc.strip())
    print('-'*len(fmsg))

    print()

    fmsg = '-'*10 + ' Assembler generado ' + '-'*10
    print(fmsg)
    print(asm.strip())
    print('-'*len(fmsg))

input('\n\nPresione una tecla para finalizar...')