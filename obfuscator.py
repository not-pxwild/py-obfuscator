import ast
import base64
import random
import string
from pathlib import Path

def random_name(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

def obfuscate_code_layer(code, layer=1):
    # Encode in Base64
    encoded = base64.b64encode(code.encode()).decode()
    # Wrap in exec decode layer
    return f"exec(base64.b64decode('{encoded}'))"

def rename_locals(tree):
    class Renamer(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            node.name = random_name()
            self.generic_visit(node)
            return node
        def visit_Name(self, node):
            if isinstance(node.ctx, (ast.Store, ast.Load)):
                node.id = random_name()
            return node
    return Renamer().visit(tree)

def string_obfuscator(tree):
    class StrObf(ast.NodeTransformer):
        def visit_Constant(self, node):
            if isinstance(node.value, str) and node.value:
                encoded = base64.b64encode(node.value.encode()).decode()
                return ast.Call(func=ast.Name(id="__s", ctx=ast.Load()),
                                args=[ast.Constant(value=encoded)],
                                keywords=[])
            return node
    return StrObf().visit(tree)

HELPER = """
import base64
def __s(x): return base64.b64decode(x.encode()).decode()
"""

def extreme_obfuscate(source, layers=3):
    # Parse AST
    tree = ast.parse(source)
    tree = rename_locals(tree)
    tree = string_obfuscator(tree)
    import astor
    code = HELPER + "\n" + astor.to_source(tree)
    for _ in range(layers):
        code = obfuscate_code_layer(code)
    return code

def obfuscate_file(input_file, output_file, layers=3):
    src = Path(input_file).read_text()
    obf = extreme_obfuscate(src, layers)
    Path(output_file).write_text(obf)
    print(f"[+] Written extreme obfuscated code to {output_file}")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Extreme multi-layer Python obfuscator")
    ap.add_argument("input", help="Input Python file")
    ap.add_argument("output", help="Output obfuscated file")
    ap.add_argument("-l", "--layers", type=int, default=3, help="Number of Base64 layers")
    args = ap.parse_args()
    obfuscate_file(args.input, args.output, args.layers)