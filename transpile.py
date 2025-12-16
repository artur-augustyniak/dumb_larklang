#!/usr/bin/env python3
import sys
from pprint import pprint as pp
from dumblang import dsl_grammar
import lark


class PythonTranspiler:
    INDENT = "    "

    def __init__(self, prog: lark.tree.Tree):
        self.prog = prog
        self.lines: list[str] = []

    def _emit(self, line: str = "", indent: int = 0):
        self.lines.append(self.INDENT * indent + line)

    def transpile(self) -> str:
        self._emit("def inpstr():")
        self._emit("    return input()", 0)
        self._emit("")
        self._emit("def inpnum():")
        self._emit("    return float(input())", 0)
        self._emit("")

        for child in self.prog.children:
            if isinstance(child, lark.Tree) and child.data == "function":
                self._transpile_function(child)
                self._emit("")

            if isinstance(child, lark.Tree) and child.data == "main":
                self._emit("def main():")
                self._transpile_main(child)
                self._emit("")
                self._emit('if __name__ == "__main__":')
                self._emit("main()", 1)

        return "\n".join(self.lines)

    def _transpile_main(self, fn: lark.Tree):
        self._transpile_block(fn.children[0], 1)

    def _transpile_function(self, fn: lark.Tree):
        param_list = fn.children[1] or ""
        self._emit(f"def {fn.children[0].value}({param_list}):", 0)
        if not fn.children[2].children:
            self._emit("pass", 1)
        else:
            self._transpile_block(fn.children[2], 1)

    def _transpile_block(self, block: lark.Tree, indent: int):
        for stmt in block.children:
            self._transpile_stmt(stmt, indent)
        else:
            self._emit("pass", indent)

    def _transpile_stmt(self, node: lark.Tree, indent: int):
        if isinstance(node, lark.Tree) and node.data == "stmt_expr":
            if node.children[0].data == "asign":
                line = self._emit_assignment(node.children[0])
                self._emit(line, indent)
            elif node.children[0].data == "arr_assign":
                line = self._emit_arr_assignment(node.children[0])
                self._emit(line, indent)
            else:
                self._emit(self._emit_expr(node.children[0]), indent)
            return

        if isinstance(node, lark.Tree) and node.data == "while_loop":
            cond = self._emit_expr(node.children[0])
            self._emit(f"while {cond}:", indent)
            self._transpile_block(node.children[1], indent + 1)
            return

        if isinstance(node, lark.Tree) and node.data == "if_else":
            cond = self._emit_expr(node.children[0])
            self._emit(f"if {cond}:", indent)
            self._transpile_block(node.children[1], indent + 1)
            self._emit("else:", indent)
            self._transpile_block(node.children[2], indent + 1)
            return

        raise TypeError(f"Unexpected stmt node in transpiler: {node!r}")

    def _emit_expr(self, node: lark.Tree) -> str:

        if isinstance(node, lark.Tree) and node.data == "number":
            return node.children[0].value

        if isinstance(node, lark.Tree) and node.data == "string":
            return node.children[0].value

        if isinstance(node, lark.Tree) and node.data == "identifier":
            return self._emit_expr(node.children[0])

        if isinstance(node, lark.lexer.Token):
            return node.value

        if isinstance(node, lark.Tree) and node.data == "arr_acc":
            name = node.children[0].value
            idx = self._emit_expr(node.children[1])
            try:
                idx = int(float(idx))
            except:
                pass
            return f"{name}[int({idx})]"

        if isinstance(node, lark.Tree) and node.data == "ret":
            if node.children[0] is None:
                return "return"
            else:
                return f"return {self._emit_expr(node.children[0])}"
            return

        if isinstance(node, lark.Tree) and (
            node.data == "bin_expr"
            or node.data == "bin_expr_c"
            or node.data == "bin_expr_b"
        ):
            op = node.children[1].value
            if op == "/":
                op = "//"
            left = self._emit_expr(node.children[0])
            right = self._emit_expr(node.children[2])
            return f"{left} {op} {right}"

        if isinstance(node, lark.Tree) and node.data == "arr_decl":
            elems = ", ".join(self._emit_expr(e) for e in node.children)
            return f"[{elems}]"

        if isinstance(node, lark.Tree) and node.data == "function_call":
            return self._emit_call(node)

        if isinstance(node, lark.Tree) and node.data == "expr_paren":
            expr = self._emit_expr(node.children[0])
            return f"({expr})"

        if isinstance(node, lark.Tree) and node.data == "unary_exp":
            op = node.children[0].value
            exp = self._emit_expr(node.children[1])
            return f"{op}{exp}"

        raise TypeError(f"Unexpected expr node in transpiler: {node!r}")

    def _emit_assignment(self, expr: lark.Tree) -> str:
        lterm = expr.children[0]
        rterm = expr.children[1]
        lhs = self._emit_expr(lterm)
        rhs = self._emit_expr(rterm)
        return f"{lhs} = {rhs}"

    def _emit_arr_assignment(self, expr: lark.Tree) -> str:
        arr_name = expr.children[0].value
        arr_expr = expr.children[1]
        arr_idx = self._emit_expr(arr_expr)
        rterm = expr.children[2]
        try:
            arr_idx = float(arr_idx)
        except:
            pass
        lhs = f"{arr_name}[int({arr_idx})]"

        rhs = self._emit_expr(rterm)
        return f"{lhs} = {rhs}"

    def _emit_call(self, call: lark.Tree) -> str:
        name = call.children[0].value
        arg = "" if call.children[1] is None else self._emit_expr(call.children[1])
        return f"{name}({arg})"


if __name__ == "__main__":
    src = open(sys.argv[1]).read()
    parser = lark.Lark(dsl_grammar, start="program", parser="lalr")
    tree = parser.parse(src)
    # print(type(tree))
    # print(tree.pretty())
    transpiler = PythonTranspiler(tree)
    py_src = transpiler.transpile()
    print(py_src)
