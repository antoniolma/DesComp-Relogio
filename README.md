# DESCOMP - Projeto 1: Relógio

## Desenvolvedores:
- Antonio Lucas Michelon de Almeida
- Pedro Nery Affonso dos Santos

## O Projeto:
<p align="justify">
O projeto consiste no desenvolvimento e implementação de um processador para um relógio, utilizando uma arquitetura baseada em registradores-memória, como visto em aula. Além disso, deverá ser desenvolvido um programa em Python de um Assembler, que transforma o código Assembly em linguagem de máquina do processador desenvolvido durante a disciplina. Esse projeto foi produzido com base no estudo guiado das aulas seis, sete, oito e nove.
</p>

<p align="justify">
Os alunos deverão projetar tanto o VHDL (Hardware) quanto o código Assembly (Software), que devem ser integrados na memória ROM do processador. Por fim, deverá ser realizada a implementação do projeto em uma placa FPGA, para a visualização e validação do projeto físico.
</p>

## Manual de instruções
<p align="justify">
Ao ligar o relógio, ele deverá entrar no seu ciclo básico de contagem, ou seja irá incrementar segundos, depois minutos e por fim as horas até bater o valor limite de 24 horas, onde voltará a mostrar em seus displays todos os valores zerados.

Como adicionais, foram implementados:
<ul>
    <li>
        <p><b>Switches</b> para mudança de <b>velocidade de contagem</b>, sendo:</p>
        <ul>
            <li>
                <p><b><i>SW9</i></b>: velocidade <b>rápida</b>.</p>
            </li>
            <li>
                <p><b><i>SW8</i></b>: velocidade <b>média</b>.</p>
            </li>
            <li>
                <p><b><i>Nenhum</i></b>: velocidade <b>padrão</b>.</p>
            </li>   
        </ul>
    </li>
    <li>
        <p><b>Botões</b> (<b><i>KEY3</i></b> e <b><i>KEY2</i></b>) para ajuste manual do horário:</p>
        <ul>
            <li>
                <p><b><i>KEY3</i></b>: incrementa 1 na contagem de <b><i>horas</i></b>.</p>
            </li>
            <li>
                <p><b><i>KEY2</i></b>: incrementa 1 na contagem de <b><i>minutos</i></b>.</p>
            </li>
        </ul>
    </li>
</ul>
</p>

## Novas instruções implementadas:
<p align="justify">
<ul>
    <li>
        <p align="justify"><b>CLT</b> <i>(Compare Less Than)</i>: Instrução que <b>compara</b> o valor de uma posição da memória com o valor presente no <b>registrador escolhido</b>. Caso o valor extraído da RAM seja maior que o do registrador, uma <b><i>flagLess</i></b> é habilitada.</p>
    </li>
    <li>
        <p align="justify"><b>JLT</b> <i>(Jump if Less Than)</i>: Instrução que <b>pula</b> para a linha de endereço da memória ROM, caso a instrução de comparação CLT tenha ativado a <b><i>flagLess</i></b>. Caso contrário, o PC segue para a linha seguinte.</p>
    </li>
    <li>
        <p align="justify"><b>ADDi</b> <i>(Soma com o imediato)</i>: Instrução que <b>soma</b> o valor do registrador endereçado com o valor imediato passado.</p>
    </li>
    <li>
        <p align="justify"><b>SUBi</b> <i>(Subtrair com o imediato)</i>: Instrução que <b>subtrai</b> o valor do registrador endereçado com o valor imediato passado.</p>
    </li>
    <li>
        <p align="justify"><b>CEQi</b> <i>(Compara com o imediato)</i>: Instrução que <b>compara</b> o valor do registrador endereçado com o valor imediato passado. Caso o valor do registrador seja igual ao imediato, uma <b>flagEqual</b> é habilitada.</p>
    </li>
</ul>
</p>

## Diagrama de blocos do circuito
![Imagem Diagrama de Blocos](img/RTL_Viewer.png)