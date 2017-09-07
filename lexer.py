# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# lexer.py
# Analisador léxico para a linguagem Caleidoscópio
# Autores: Rodrigo Hübner e Jorge Luiz Franzon Rossi
#-------------------------------------------------------------------------

import ply.lex as lex

class Lexer:

    def __init__(self):
        self.lexer = lex.lex(debug=False, module=self, optimize=False)

    keywords = {
        u'função': 'DEF',
        u'externa': 'EXTERN',
        u'se': 'IF',
        u'então': 'THEN',
        u'senão': 'ELSE',
    }

    tokens = ['EQ', 'NE', 'GE', 'GT', 'LE', 'LT', 'ADD', 'SUB', 'MUL', 'DIV',
              'ID', 'NUM', 'LPAR', 'RPAR', 'COMMA'] + list(keywords.values())

    t_EQ = r'='
    t_NE = r'~'
    t_GE = r'>='
    t_GT = r'>'
    t_LE = r'<='
    t_LT = r'<'
    t_ADD = r'\+'
    t_SUB = r'\-'
    t_MUL = r'\*'
    t_DIV = r'/'
    t_LPAR = r'\('
    t_RPAR = r'\)'
    t_COMMA = r','
    t_NUM = r'[0-9]+(\.[0-9]+)?'

    def t_ID(self, t):
        r'[a-zA-Zá-ñÁ-Ñ][a-zA-Zá-ñÁ-Ñ0-9]*'
        t.type = self.keywords.get(t.value, 'ID')
        return t

    def t_COMMENT(self, t):
        r'\#.*'

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    t_ignore = ' \t'

    def t_error(self, t):
        print("Item ilegal: '%s', linha %d, coluna %d" % (t.value[0],
                                                          t.lineno, t.lexpos))
        t.lexer.skip(1)

    def test(self, code):
        lex.input(code)
        while True:
            t = lex.token()
            if not t:
                break
            print(t)

if __name__ == '__main__':
    from sys import argv
    lexer = Lexer()
    f = open(argv[1])
    lexer.test(f.read())