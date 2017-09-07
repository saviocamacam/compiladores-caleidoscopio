# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# lexer.py
# Analisador sintático e geração de uma árvore sintática abstrata para a
#   linguagem Caleidoscópio
# Autores: Rodrigo Hübner e Jorge Luiz Franzon Rossi
#-------------------------------------------------------------------------

from ply import yacc
from lexer import Lexer

class Tree:

    def __init__(self, type_node, child=[], value=''):
        self.type = type_node
        self.child = child
        self.value = value

    def __str__(self):
        return self.type

class Parser:

    def __init__(self, code):
        lex = Lexer()
        self.tokens = lex.tokens
        self.precedence = (
            ('left', 'ELSE'),
            ('left', 'EQ', 'NE', 'GE', 'GT', 'LE', 'LT'),
            ('left', 'ADD', 'SUB'),
            ('left', 'MUL', 'DIV'),
        )
        parser = yacc.yacc(debug=False, module=self, optimize=False)
        self.ast = parser.parse(code)

    def p_top(self, p):
        '''
        top : definition
            | extern
            | expr
        '''
        p[0] = Tree('top', [p[1]])

    def p_definition(self, p):
        'definition : DEF prototype expr'
        p[0] = Tree('definition', [p[2], p[3]])

    def p_prototype(self, p):
        'prototype : ID LPAR arg_names RPAR'
        p[0] = Tree('prototype', [p[3]], p[1])

    def p_arg_names_1(self, p):
        'arg_names : '

    def p_arg_names_2(self, p):
        'arg_names : ID COMMA arg_names'
        p[0] = Tree('arg_names', [p[3]], p[1])

    def p_arg_names_3(self, p):
        'arg_names : ID'
        p[0] = Tree('arg_names', [], p[1])

    def p_expr(self, p):
        '''
        expr : binary_expr
             | call_expr
             | if_expr
             | par_expr
             | id_expr
             | num_expr
        '''
        p[0] = Tree('expr', [p[1]])

    def p_binary_expr(self, p):
        '''
        binary_expr : expr EQ expr
                    | expr NE expr
                    | expr GE expr
                    | expr GT expr
                    | expr LE expr
                    | expr LT expr
                    | expr ADD expr
                    | expr SUB expr
                    | expr MUL expr
                    | expr DIV expr
        '''
        p[0] = Tree('binary_expr', [p[1], p[3]], p[2])

    def p_call_expr(self, p):
        'call_expr : ID LPAR call_args RPAR'
        p[0] = Tree('call_expr', [p[3]], p[1])

    def p_call_args_1(self, p):
        'call_args : '

    def p_call_args_2(self, p):
        'call_args : expr COMMA call_args'
        p[0] = Tree('call_args', [p[1], p[3]])

    def p_call_args_3(self, p):
        'call_args : expr'
        p[0] = Tree('call_args', [p[1]])

    def p_if_expr(self, p):
        'if_expr : IF expr THEN expr ELSE expr'
        p[0] = Tree('if_expr', [p[2], p[4], p[6]])

    def p_par_expr(self, p):
        'par_expr : LPAR expr RPAR'
        p[0] = Tree('par_expr', [p[2]])

    def p_id_expr(self, p):
        'id_expr : ID'
        p[0] = Tree('id_expr', [], p[1])

    def p_num_expr(self, p):
        'num_expr : NUM'
        p[0] = Tree('num_expr', [], p[1])

    def p_extern(self, p):
        'extern : EXTERN prototype'
        p[0] = Tree('extern', [p[2]])

    def p_error(self, p):
        if p:
            print("Erro sintático: '%s', linha %d" % (p.value, p.lineno))
            exit(1)
        else:
            yacc.restart()
            print('Erro sintático: definições incompletas!')
            exit(1)

if __name__ == '__main__':
    from sys import argv, exit
    f = open(argv[1])
    Parser(f.read())
