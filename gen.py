# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# gen.py
# Gerador de código LLVM IR para a linguagem Caleidoscópio
# Autores: Rodrigo Hübner e Jorge Luiz Franzon Rossi
# TODO:
#   - Resolver funções que não foram declaradas
#-------------------------------------------------------------------------


# PROBLEMAS 
# - Redefinição de funções

from llvmlite import ir, binding
from parser import Parser
from sys import exit
from ctypes import CFUNCTYPE, c_int32, c_double

class Gen:

    def __init__(self, code, module, symbols, ee, passes, optz, debug):
        parse = Parser(code)
        self.module = module
        self.ee = ee
        self.passes = passes
        self.optimization = optz
        self.builder = None
        self.func = None
        self.symbols = symbols
        self.debug = debug
        self.gen_top(parse.ast)

    def compile_ir(self):
        mod = binding.parse_assembly(str(self.module))
        mod.verify()
        self.ee.add_module(mod)
        self.ee.finalize_object()
        return mod

    def gen_top(self, node):
        node = node.child[0]
        if node.type == 'definition':
            self.gen_definition(node)
            if self.optimization:
                self.passes.run(self.func)
            if self.debug:
                print(self.func)
        elif node.type == 'extern':
            self.gen_prototype(node.child[0], node.child[0].value)
        elif node.type == 'expr':
            self.gen_prototype(node, name='function_'+str(len(self.module.functions)))
            self.gen_block()
            result = self.gen_expr(node)
            try:
                self.builder.ret(result)
                mod = self.compile_ir()
                func_ptr = self.ee.get_function_address(self.func._name)
                cfunc = CFUNCTYPE(c_double)(func_ptr)
                retval = cfunc()
                print('Retorno: ', retval)
                #retval = self.ee.run_function(self.func, [])
                # print(retval.as_real(Type.double()))
            except AttributeError:
                print('Erro: {0}'.format(result))

    def gen_definition(self, node):
        print('ptype ', node.value)
        self.gen_prototype(node.child[0], node.child[0].value)
        self.gen_block()
        result = self.gen_expr(node.child[1])
        self.builder.ret(result)

    def gen_prototype(self, node, name=''):
        # tratamento de funções redefinidas
        print("Função:", name)
        if name and name in self.symbols.keys():
            self.symbols.pop(name)
            # self.module.get_function_named(name).delete()
            self.module.globals.pop(name)
            self.module._sequence.remove(name)
        node = node.child[0]
        args = self.gen_arg_names(node)
        num_args = len(args)
        ty_func = ir.FunctionType(
            ir.DoubleType(), [ir.DoubleType()] * num_args)
        #self.func = self.module.add_function(func_type, name)
        self.func = ir.Function(self.module, ty_func, name=name)
        self.symbols[self.func.name] = {}
        for i, arg in enumerate(args):
            self.func.args[i].name = arg
            self.symbols[self.func.name][arg] = self.func.args[i]
        for i in self.module.functions:
            print(i)

    def gen_block(self):
        block = self.func.append_basic_block('entry')
        self.builder = ir.IRBuilder(block)

    def gen_arg_names(self, node):
        args = []
        while node and node.type == 'arg_names':
            args.append(node.value)
            if node.child:
                node = node.child[0]
            else:
                break
        return args

    def gen_expr(self, node):
        node = node.child[0]
        if node.type == 'binary_expr':
            return self.gen_binary_expr(node)
        elif node.type == 'call_expr':
            return self.gen_call_expr(node)
        elif node.type == 'if_expr':
            return self.gen_if_expr(node)
        elif node.type == 'par_expr':
            return self.gen_expr(node.child[0])
        elif node.type == 'id_expr':
            return self.symbols[self.func.name][node.value]
        elif node.type == 'num_expr':
            return ir.Constant(ir.DoubleType(), node.value)

    def gen_binary_expr(self, node):
        left = self.gen_expr(node.child[0])
        right = self.gen_expr(node.child[1])
        op = node.value
        # operações aritméticas
        if op == '+':
            return self.builder.fadd(left, right, 'addtmp')
        elif op == '-':
            return self.builder.fsub(left, right, 'subtmp')
        elif op == '*':
            return self.builder.fmul(left, right, 'multmp')
        elif op == '/':
            return self.builder.fdiv(left, right, 'divtmp')
        # operações lógicas
        if op == '=':
            return self.builder.fcmp_unordered('==', left, right, 'cmptmp')
        elif op == '~':
            return self.builder.fcmp_unordered('!=', left, right, 'cmptmp')
        elif op == '>':
            return self.builder.fcmp_unordered('>', left, right, 'cmptmp')
        elif op == '>=':
            return self.builder.fcmp_unordered('>=', left, right, 'cmptmp')
        elif op == '<':
            return self.builder.fcmp_unordered('<', left, right, 'cmptmp')
        elif op == '<=':
            return self.builder.fcmp_unordered('<=', left, right, 'cmptmp')
        # if op in ('+', '-', '*', '/'):
        #     return op_a[op]
        # elif op in ('=', '!', '>', '>=', '<', '<='):
        #     return self.builder.uitofp(op_l[op], ir.DoubleType(), 'booltmp')
        # else:
        #     raise RuntimeError('Operação binária não reconhecida.')

    def gen_call_args(self, node):
        args = []
        while node:
            args.append(self.gen_expr(node.child[0]))
            if len(node.child) > 1:
                node = node.child[1]
            else:
                break
        return args

    def gen_call_expr(self, node):
        args = self.gen_call_args(node.child[0])
        if node.value not in self.symbols.keys():
            err = "'%s' não está definida" % (node.value)
            self.func = None
            return err
        num_func_call = len(self.symbols[node.value])
        num_func = len(args)
        if num_func == num_func_call:
            func = self.module.get_global(node.value)
            return self.builder.call(func, args, 'calltmp')
        else:
            err = "'%s' espera %d argumento(s), %d passado(s)" % (node.value,
                                                                  num_func_call, num_func)
            self.func = None
            return err

    def gen_if_expr(self, node):
        # formula a condição
        cond = self.gen_expr(node.child[0])
        # Estava dando erro
        #bool_cond = self.builder.fcmp_unordered('==', cond,
        #                              ir.Constant(ir.DoubleType(), 0), 'ifcond')
        # adiciona os blocos básicos
        then_block = self.func.append_basic_block('then')
        else_block = self.func.append_basic_block('else')
        merge_block = self.func.append_basic_block('ifcont')
        #self.builder.cbranch(bool_cond, then_block, else_block)
        self.builder.cbranch(cond, then_block, else_block)
        # emite o valor 'then'
        self.builder.position_at_end(then_block)
        then_value = self.gen_expr(node.child[1])
        self.builder.branch(merge_block)
        then_block = self.builder.basic_block
        # emite o valor 'else'
        self.builder.position_at_end(else_block)
        else_value = self.gen_expr(node.child[2])
        self.builder.branch(merge_block)
        else_block = self.builder.basic_block
        # finalizando o código e acionando os nós PHI
        self.builder.position_at_end(merge_block)
        phi = self.builder.phi(ir.DoubleType(), 'iftmp')
        phi.add_incoming(then_value, then_block)
        phi.add_incoming(else_value, else_block)
        return phi
