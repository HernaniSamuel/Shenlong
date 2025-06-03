import argparse
import subprocess
import os
from lark import Lark
from parser.ast_builder import ASTBuilder
from translator.core import CoreTranslator

def main():
    parser = argparse.ArgumentParser(description="Shenlong: Compilador de .psyl para .cpp")
    parser.add_argument("source", help="Arquivo de entrada .psyl")
    parser.add_argument("--compile", action="store_true", help="Compila o arquivo .cpp gerado")
    parser.add_argument("--run", action="store_true", help="Compila e executa o binário")
    args = parser.parse_args()

    # Caminho do arquivo de entrada
    source_path = args.source
    if not source_path.endswith(".psyl"):
        print("Erro: O arquivo precisa ter a extensão .psyl")
        return

    # Lê o conteúdo do arquivo de entrada
    with open(source_path) as f:
        source_code = f.read()

    # Carrega a gramática
    with open('grammar/syntax.lark') as f:
        grammar = f.read()

    # Faz parsing
    lark_parser = Lark(grammar, start='program', parser='lalr')
    tree = lark_parser.parse(source_code)

    # Constrói AST
    ast_builder = ASTBuilder()
    ast = ast_builder.transform(tree)

    # Traduz pra C++
    translator = CoreTranslator()
    generated_code = translator.translate(ast)

    # Cria um template com o main()
    cpp_template = """// Code generated automatically by Shenlong the Tiger!
#include <iostream>

int main() {
%s
    return 0;
}
"""

    # Indenta as linhas geradas em um nível
    indented_code = "\n".join(
        ("    " + line if line.strip() else line) for line in generated_code.splitlines()
    )

    cpp_code = cpp_template % indented_code

    # Caminho de saída (mesma pasta, extensão .cpp)
    output_path = os.path.splitext(source_path)[0] + ".cpp"
    with open(output_path, "w") as f:
        f.write(cpp_code)

    # print(f"Arquivo gerado: {output_path}")

    binary_path = os.path.splitext(source_path)[0]

    if args.compile or args.run:
        # Verifica se precisa recompilar (timestamps)
        psyl_mtime = os.path.getmtime(source_path)
        cpp_mtime = os.path.getmtime(output_path) if os.path.exists(output_path) else 0
        bin_mtime = os.path.getmtime(binary_path) if os.path.exists(binary_path) else 0

        # Compila se binário não existe ou .psyl mais novo que binário
        needs_compile = not os.path.exists(binary_path) or psyl_mtime > bin_mtime

        if needs_compile:
            # print("Compilando com g++: g++ -std=c++17", output_path, "-o", binary_path)
            compile_cmd = ["g++", "-std=c++17", output_path, "-o", binary_path]
            result = subprocess.run(compile_cmd)

            if result.returncode != 0:
                print("Erro ao compilar o arquivo .cpp")
                return
            # print(f"Arquivo compilado: {binary_path}")
        else:
            # print("Binário já está atualizado.")
            pass

        if args.run:
            # Executa o binário
            # print("Executando o binário:")
            subprocess.run([binary_path])


if __name__ == "__main__":
    main()
