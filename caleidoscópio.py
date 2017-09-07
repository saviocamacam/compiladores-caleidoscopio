# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# caleidoscópio.py
# Interpretador para a linguagem Caleidoscópio
# Autores: Rodrigo Hübner e Jorge Luiz Franzon Rossi
#-------------------------------------------------------------------------

#from llvm.core import Module
#from llvm.ee import ExecutionEngine
# from llvm.passes import (FunctionPassManager, PASS_INSTCOMBINE, PASS_GVN,
#    PASS_REASSOCIATE, PASS_SIMPLIFYCFG)
from llvmlite import ir
from llvmlite import binding
from gen import Gen

OPTIMIZATION = False
DEBUG = True
SHOW_END_CODE = False

def create_execution_engine():
    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine()
    backing_mod = binding.parse_assembly("")
    engine = binding.create_mcjit_compiler(backing_mod, target_machine)
    return engine

def main():
    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()
    # inicializando módulo principal
    #module = Module.new('main')
    module = ir.Module('my_module')
    # inicializando a tabela de símbolos
    symbols = {}
    # inicializando o gerenciador de passos de otimização e funções
    passes = None
    # FunctionPassManager.new(module)
    # configurando o motor de execução
    ee = create_execution_engine()
    # configuração dos passos de otimização
    # registra os passos já realizados em uma estrutura para executar
    # passes.add(ee.target_data)
    # combina e remove instruções redundantes
    # passes.add(PASS_INSTCOMBINE)
    # reassocia instruções para otimizar aritmética de constantes
    # passes.add(PASS_REASSOCIATE)
    # elimina subexpressões comuns
    # passes.add(PASS_GVN)
    # remove blocos básicos sem predecessor, elimina nó PHI para blocos básicos
    # com um único predecessor e elimina blocos que contém salto incondicional
    # passes.add(PASS_SIMPLIFYCFG)
    # inicializa as otimizações
    # passes.initialize()
    while True:
        try:
            code = input('Caleidoscópio => ')
        except KeyboardInterrupt:
            print()
            break
        driver = Gen(code, module, symbols, ee, passes, OPTIMIZATION, DEBUG)
    if SHOW_END_CODE:
        print('\n\n=== Código LLVM final ===')
        print(module)

if __name__ == '__main__':
    main()