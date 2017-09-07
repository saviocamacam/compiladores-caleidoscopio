---
title: Tutorial de desenvolvimento de um compilador para Caleidoscópio
subtitle: Desenvolvimento de um compilador utilizando as ferramentas PLY e LLVMPy
author: Rodrigo Hübner
---

# Compilador para a linguagem de programação Caleidoscópio - Definição e Varredura

### Introdução

Este tutorial tem como objetivo o de desenvolver um compilador para uma linguagem 
de programação chamada Caleidoscópio [1].

O compilador será escrito na linguagem de programação Python com auxílio da 
ferramenta Python Lex Yacc (PLY) [2] e será gerado uma representação intermediária 
em LLVM [3] utilizando LLVMPy [4].

Um tutorial parecido com este pode ser visto em [5], porém neste tutorial será trabalhado
todas as práticas para o ensino de compiladores bem como o uso de ferramentas que 
auxiliam nas fases de análise do compilador.

### Definição 

Caleidoscópio é uma linguagem procedural que permite definir funções, condições, 
operações aritméticas, etc. Ao longo deste tutorial será desenvolvido todas as fases 
de análise (léxica, sintática e semântica) utilizando como suporte a ferramenta
PLY, bem como a geração do código intermediário LLVM e por fim a adição de algumas 
otimizações e com compilação *Just in Time* (JIT) [6].

Um simples programa é apresentado a seguir (números de Fibonacci) para demonstrar 
a simplicidade da linguagem.

```python
função fib(x)
   se x < 3 então
      1
   senão
      fib(x-1) + fib(x-2)
```

É possível também utilizar funções da biblioteca padrão do LLVM, utilizando a palavra 
reservada `externa` prescindido da função específica. Por exemplo:

```
externa sin(arg)
externa cos(arg)
externa atan2(arg1, arg2)

atan2(sin(0.4), cos(42))
```

Vamos então iniciar a implementação com a primeira fase de análise do compilador: 
análise léxica.

### Análise Léxica

A análise léxica tem como principal objetivo reconhecer os itens de uma linguagem 
e caracterizá-los como tokens específicos. Também tem o objetivo de detectar possíveis 
palavras ou caracteres não reconhecidos pela linguagem. A Tabela 1 apresenta todos 
os itens relacionados aos seus tokens da linguagem Caleidoscópio.


O código que implementa a análise léxica do código pode ser visto em `lexer.py`.

### Análise Sintática

A análise sintática tem como principal objetivo verificar se a composição dos tokens 
apresentados em uma entrada da linguagem estão corretos. Este passo do compilador 
também possui a tarefa de produzir uma árvore sintática abstrata (ASA) para uma 
gramática da linguagem de programação. Em uma ASA fica mais fácil aplicar algumas 
otimizações futuras, além de armazenar em seus nós, informações importantes como 
o balanceamento de parênteses implícito, conjuntos `IF-THEN-ELSE`, etc. A gramática 
de Caleidoscópio é apresentado no formato BNF como segue:

```
top ::= definition 
      | extern
      | expr
definition : "função" prototype expr
prototype : ID "(" arg_names ")"
arg_names : 
          | arg_names "," ID
          | ID
expr : binary_expr
     | call_expr
     | if_expr
     | par_expr
     | id_expr
     | num_expr
binary_expr : expr "=" expr
            | expr "~" expr
            | expr ">=" expr
            | expr ">" expr
            | expr "<=" expr
            | expr "<" expr
            | expr "+" expr
            | expr "-" expr
            | expr "*" expr
            | expr "/" expr
call_expr : ID "(" call_args ")"
call_args : 
          | call_args "," expr
          | expr
if_expr : "se" expr "então" expr "senão" expr
par_expr : "(" expr ")"
id_expr : ID
num_expr : NUM
extern : "externa" prototype
```

A precendência de operadores obedece a seguinte sequência:

1. "*" e "/"
2. "+" e "-"
3. "=", "~", ">=", ">", "<=" e "<"

O código que implementa a análise sintática do código pode ser visto em `parser.py`.

### Análise Semântica

TODO

### Geração de Código LLVM IR

TODO

### Otimizações

TODO

### Conclusões

TODO

### Referências

[1] http://llvm.org/docs/tutorial/LangImpl1.html
[2] http://www.dabeaz.com/ply
[3] http://llvm.org
[4] http://www.llvmpy.org/
[5] http://en.wikipedia.org/wiki/Just-in-time_compilation