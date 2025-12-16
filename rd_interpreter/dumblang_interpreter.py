#!/usr/bin/env python3
from __future__ import annotations

import operator
import string
import sys
import os
from dataclasses import dataclass
from enum import Enum
from pprint import pprint as pp


class TokenType(Enum):
    NONE = "NONE"
    OPERATOR = "OPERATOR"
    IDENTIFIER = "IDENTIFIER"
    STRING_LITERAL = "STRING_LITERAL"
    NUMBER_LITERAL = "NUMBER_LITERAL"
    EXPR_END = "EXPR_END"
    L_BLOCK = "L_BLOCK"
    R_BLOCK = "R_BLOCK"
    L_PAREN = "L_PAREN"
    R_PAREN = "R_PAREN"
    ARR_START = "ARR_START"
    ARR_END = "ARR_END"
    ARR_SEP = "ARR_SEP"
    ASIGN = "ASIGN"
    EOF = "EOF"


@dataclass
class Token:
    t_type: TokenType
    t_content: str | None
    line: int = 0


def tokenizer(input_program: str):
    line_no = 1
    stream = iter(input_program)
    curr_token = Token(TokenType.NONE, "", line=line_no)

    for c in stream:
        # line comments start with '#'
        if c == "#":
            for c in stream:
                if c == "\n":
                    line_no += 1
                    break
            continue

        match c:
            case (
                " " | "\t" | "\r" | "\n"
            ) if curr_token.t_type != TokenType.STRING_LITERAL:
                if curr_token.t_type != TokenType.NONE:
                    yield curr_token
                if c == "\n":
                    line_no += 1
                curr_token = Token(TokenType.NONE, "", line=line_no)
                continue

            case (
                _
            ) if c in string.ascii_letters or curr_token.t_type == TokenType.STRING_LITERAL:
                if curr_token.t_type == TokenType.NONE:
                    curr_token = Token(TokenType.IDENTIFIER, c, line=line_no)
                else:
                    if curr_token.t_type == TokenType.STRING_LITERAL and c == '"':
                        if curr_token.t_type != TokenType.NONE:
                            yield curr_token
                        curr_token = Token(TokenType.NONE, "", line=line_no)
                    else:
                        curr_token.t_content += c

            case _ if c in string.digits or (
                c == "." and curr_token.t_type == TokenType.NUMBER_LITERAL
            ):
                if curr_token.t_type == TokenType.NONE:
                    curr_token = Token(TokenType.NUMBER_LITERAL, c, line=line_no)
                else:
                    curr_token.t_content += c

            case '"':
                if curr_token.t_type == TokenType.NONE:
                    curr_token = Token(TokenType.STRING_LITERAL, "", line=line_no)
                else:
                    if c != '"':
                        curr_token.t_content += c

            case "[":
                if curr_token.t_type != TokenType.NONE:
                    yield curr_token
                yield Token(TokenType.ARR_START, "[", line=line_no)
                curr_token = Token(TokenType.NONE, "", line=line_no)

            case "]":
                if curr_token.t_type != TokenType.NONE:
                    yield curr_token
                yield Token(TokenType.ARR_END, "]", line=line_no)
                curr_token = Token(TokenType.NONE, "", line=line_no)

            case "{":
                if curr_token.t_type != TokenType.NONE:
                    yield curr_token
                yield Token(TokenType.L_BLOCK, "{", line=line_no)
                curr_token = Token(TokenType.NONE, "", line=line_no)

            case "}":
                if curr_token.t_type != TokenType.NONE:
                    yield curr_token
                yield Token(TokenType.R_BLOCK, "}", line=line_no)
                curr_token = Token(TokenType.NONE, "", line=line_no)

            case ";":
                if curr_token.t_type != TokenType.NONE:
                    yield curr_token
                yield Token(TokenType.EXPR_END, ";", line=line_no)
                curr_token = Token(TokenType.NONE, "", line=line_no)

            case ",":
                if curr_token.t_type != TokenType.NONE:
                    yield curr_token
                yield Token(TokenType.ARR_SEP, ",", line=line_no)
                curr_token = Token(TokenType.NONE, "", line=line_no)

            case "(":
                if curr_token.t_type != TokenType.NONE:
                    yield curr_token
                yield Token(TokenType.L_PAREN, "(", line=line_no)
                curr_token = Token(TokenType.NONE, "", line=line_no)

            case ")":
                if curr_token.t_type != TokenType.NONE:
                    yield curr_token
                yield Token(TokenType.R_PAREN, ")", line=line_no)
                curr_token = Token(TokenType.NONE, "", line=line_no)

            case "=":
                if curr_token.t_type == TokenType.NONE:
                    curr_token = Token(TokenType.OPERATOR, "=", line=line_no)
                else:
                    if curr_token.t_type == TokenType.OPERATOR and c == "=":
                        yield Token(TokenType.OPERATOR, "==", line=line_no)
                        curr_token = Token(TokenType.NONE, "", line=line_no)
                    else:
                        curr_token.t_content += c

            case _:
                if curr_token.t_type != TokenType.NONE:
                    yield curr_token
                yield Token(TokenType.OPERATOR, c, line=line_no)
                curr_token = Token(TokenType.NONE, "", line=line_no)

    if curr_token.t_type != TokenType.NONE:
        yield curr_token
    yield Token(TokenType.EOF, None, line=line_no)


class Parser:
    class AST:
        pass

    @dataclass
    class Program(AST):
        functions: list["Parser.Function"]

    @dataclass
    class Function(AST):
        name: str
        param: str | None
        body: "Parser.Block"

    @dataclass
    class Block(AST):
        expressions: list["Parser.AST"]

    @dataclass
    class Identifier(AST):
        val: str

        def eval(self, scope, interpreter: "Interpreter"):
            return self.val

    @dataclass
    class NumberLiteral(AST):
        val: float

        def eval(self, scope, interpreter: "Interpreter"):
            return self.val

    @dataclass
    class StringLiteral(AST):
        val: str

        def eval(self, scope, interpreter: "Interpreter"):
            return self.val

    @dataclass
    class Array(AST):
        val: list["Parser.AST"]

        def eval(self, scope, interpreter: "Interpreter"):
            return [elem.eval(scope, interpreter) for elem in self.val]

    @dataclass
    class Term(AST):
        lterm: "Parser.AST"

    @dataclass
    class Expression(AST):
        lterm: "Parser.AST"
        op: "Parser.OperatorBinary"
        rterm: "Parser.AST"

        def _resolve_term(self, term, scope, interpreter: "Interpreter"):
            ctx = interpreter.block_contexts[scope] if isinstance(scope, str) else scope

            if isinstance(term, Parser.Identifier):
                name = term.eval(scope, interpreter)
                return ctx[name]
            if isinstance(term, Parser.Expression):
                return term.eval(scope, interpreter)
            if isinstance(term, Parser.FunctionCall):
                return interpreter._execute_fun_call(term, scope)
            return term.eval(scope, interpreter)

        def eval(self, scope, interpreter: "Interpreter"):
            lterm_val = self._resolve_term(self.lterm, scope, interpreter)
            rterm_val = self._resolve_term(self.rterm, scope, interpreter)
            return OPERATORS[self.op.op](lterm_val, rterm_val)

    @dataclass
    class OperatorUnary(AST):
        op: str

    @dataclass
    class OperatorBinary(AST):
        op: str

    @dataclass
    class Return(AST):
        val: "Parser.AST | None"

        def eval(self, scope, interpreter: "Interpreter"):
            if self.val is None:
                return None
            if isinstance(self.val, Parser.Identifier):
                ctx = (
                    interpreter.block_contexts[scope]
                    if isinstance(scope, str)
                    else scope
                )
                return ctx[self.val.eval(scope, interpreter)]
            return self.val.eval(scope, interpreter)

    @dataclass
    class FunctionCall(AST):
        name: str
        param: "Parser.AST | None"

    @dataclass
    class ArrAcc(AST):
        name: "Parser.Identifier"
        idx: "Parser.AST"

        def eval(self, scope, interpreter: "Interpreter"):
            ctx = interpreter.block_contexts[scope] if isinstance(scope, str) else scope
            idx_val = self.idx.eval(scope, interpreter)
            if isinstance(idx_val, str):
                idx_val = ctx[idx_val]
            arr_name = self.name.eval(scope, interpreter)
            return ctx[arr_name][int(idx_val)]

    @dataclass
    class WhileLoop(AST):
        condition: "Parser.AST"
        block: "Parser.Block"

        def eval_cond(self, scope, interpreter: "Interpreter"):
            return self.condition.eval(scope, interpreter)

    @dataclass
    class IfElse(AST):
        condition: "Parser.AST"
        if_branch: "Parser.Block"
        else_branch: "Parser.Block"

        def eval_cond(self, scope, interpreter: "Interpreter"):
            return self.condition.eval(scope, interpreter)

    # operator precedence table
    PRECEDENCE = {
        "<": 5,
        ">": 5,
        "==": 5,
        "=": 1,
        "+": 1,
        "-": 1,
        "*": 10,
        "/": 10,
        "^": 30,
    }

    def __init__(self, tokenizer_iter):
        self.tokenizer = tokenizer_iter
        self.current_token: Token | None = None
        self.next_token: Token | None = None
        self._advance()

    def _advance(self):
        self.current_token, self.next_token = self.next_token, next(
            self.tokenizer, None
        )

    def _accept(self, token_type: TokenType):
        if self.next_token and self.next_token.t_type == token_type:
            self._advance()
            return self.current_token
        return False

    def _expect(self, token_type: TokenType):
        t = self._accept(token_type)
        if not t:
            raise SyntaxError(f"Expected {token_type} got {self.current_token}")
        return t

    # GRAMMAR

    def parse(self) -> "Parser.Program":
        return self._program()

    def _program(self) -> "Parser.Program":
        functions: list[Parser.Function] = []
        while self.next_token and self.next_token.t_type != TokenType.EOF:
            functions.append(self._function())
        return Parser.Program(functions=functions)

    def _function(self) -> "Parser.Function":
        function_name = self._expect(TokenType.IDENTIFIER)
        self._expect(TokenType.L_PAREN)
        f_param = self._accept(TokenType.IDENTIFIER)
        param_name = f_param.t_content if f_param else None
        self._expect(TokenType.R_PAREN)
        body = self._block()
        return Parser.Function(
            name=function_name.t_content,
            param=param_name,
            body=body,
        )

    def _block(self) -> "Parser.Block":
        self._expect(TokenType.L_BLOCK)
        expressions: list[Parser.AST] = []

        while self.next_token and self.next_token.t_type != TokenType.R_BLOCK:
            if (
                self.next_token.t_type == TokenType.IDENTIFIER
                and self.next_token.t_content in ("while", "if")
            ):
                kw = self._accept(TokenType.IDENTIFIER)
                if kw.t_content == "while":
                    expressions.append(self._while())
                elif kw.t_content == "if":
                    expressions.append(self._if())
            else:
                expressions.append(self._expression())
                self._expect(TokenType.EXPR_END)

        self._expect(TokenType.R_BLOCK)
        return Parser.Block(expressions=expressions)

    def _if(self) -> "Parser.IfElse":
        self._expect(TokenType.L_PAREN)
        condition = self._expression()
        self._expect(TokenType.R_PAREN)
        if_block = self._block()

        else_kw = self._expect(TokenType.IDENTIFIER)
        if else_kw.t_content != "else":
            raise SyntaxError(f"Expected 'else' got {else_kw.t_content!r}")

        else_block = self._block()
        return Parser.IfElse(
            condition=condition, if_branch=if_block, else_branch=else_block
        )

    def _while(self) -> "Parser.WhileLoop":
        self._expect(TokenType.L_PAREN)
        condition = self._expression()
        self._expect(TokenType.R_PAREN)
        while_block = self._block()
        return Parser.WhileLoop(condition=condition, block=while_block)

    def _expression(self, prec: int = 1) -> "Parser.AST | None":
        if not self.next_token or self.next_token.t_type in (
            TokenType.R_PAREN,
            TokenType.R_BLOCK,
            TokenType.ARR_END,
            TokenType.EXPR_END,
        ):
            return None

        lfactor = self._factor()

        while (
            self.next_token
            and self.next_token.t_type == TokenType.OPERATOR
            and Parser.PRECEDENCE.get(self.next_token.t_content, 0) >= prec
        ):
            op_tok = self._accept(TokenType.OPERATOR)
            next_prec = Parser.PRECEDENCE[op_tok.t_content]
            rterm = self._expression(next_prec)
            lfactor = Parser.Expression(
                lterm=lfactor,
                op=Parser.OperatorBinary(op=op_tok.t_content),
                rterm=rterm,
            )
        return lfactor

    def _factor(self) -> "Parser.AST":
        if self.next_token and self.next_token.t_type == TokenType.ARR_START:
            self._expect(TokenType.ARR_START)
            elements: list[Parser.AST] = []

            while self.next_token and self.next_token.t_type != TokenType.ARR_END:
                elements.append(self._factor())
                if self.next_token and self.next_token.t_type == TokenType.ARR_SEP:
                    self._expect(TokenType.ARR_SEP)
                else:
                    break

            self._expect(TokenType.ARR_END)
            return Parser.Array(val=elements)

        if self.next_token and self.next_token.t_type == TokenType.IDENTIFIER:
            tok = self._expect(TokenType.IDENTIFIER)

            if self.next_token and self.next_token.t_type == TokenType.L_PAREN:
                self._expect(TokenType.L_PAREN)
                param = self._expression()
                self._expect(TokenType.R_PAREN)
                return Parser.FunctionCall(
                    name=tok.t_content,
                    param=param if param else None,
                )

            if self.next_token and self.next_token.t_type == TokenType.ARR_START:
                self._expect(TokenType.ARR_START)
                idx = self._expression()
                self._expect(TokenType.ARR_END)
                return Parser.ArrAcc(name=Parser.Identifier(val=tok.t_content), idx=idx)

            if tok.t_content == "return":
                opt_val = self._expression()
                return Parser.Return(val=opt_val)

            return Parser.Identifier(val=tok.t_content)

        if self.next_token and self.next_token.t_type == TokenType.NUMBER_LITERAL:
            tok = self._expect(TokenType.NUMBER_LITERAL)
            return Parser.NumberLiteral(val=float(tok.t_content))

        if self.next_token and self.next_token.t_type == TokenType.STRING_LITERAL:
            tok = self._expect(TokenType.STRING_LITERAL)
            return Parser.StringLiteral(val=tok.t_content)

        if self.next_token and self.next_token.t_type == TokenType.L_PAREN:
            self._expect(TokenType.L_PAREN)
            if self.next_token and self.next_token.t_type == TokenType.OPERATOR:
                unary_op = self._expect(TokenType.OPERATOR)
                sign = -1.0 if unary_op.t_content == "-" else 1.0
                result = Parser.Expression(
                    lterm=Parser.NumberLiteral(sign),
                    op=Parser.OperatorBinary(op="*"),
                    rterm=self._expression(),
                )
                self._expect(TokenType.R_PAREN)
                return result
            else:
                val = self._expression()
                self._expect(TokenType.R_PAREN)
                return val

        raise SyntaxError(f"Unexpected token {self.next_token}")


OPERATORS = {
    "*": operator.mul,
    "/": operator.floordiv,
    "-": operator.sub,
    "+": operator.add,
    "^": operator.pow,
    "<": operator.lt,
    ">": operator.gt,
    "==": operator.eq,
}


def inp_str() -> str:
    print("DSL<(str)")
    return input()


def inp_num() -> float:
    print("DSL<(num)")
    return float(input())


class PythonTranspiler:
    INDENT = "    "

    def __init__(self, prog: Parser.Program):
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

        # functions
        for fn in self.prog.functions:
            self._transpile_function(fn)
            self._emit("")

        # main entry if present
        if any(f.name == "main" for f in self.prog.functions):
            self._emit('if __name__ == "__main__":')
            self._emit("main()", 1)

        return "\n".join(self.lines)

    def _transpile_function(self, fn: Parser.Function):
        param_list = fn.param or ""
        self._emit(f"def {fn.name}({param_list}):", 0)

        if not fn.body.expressions:
            self._emit("pass", 1)
        else:
            self._transpile_block(fn.body, 1)

    def _transpile_block(self, block: Parser.Block, indent: int):
        for stmt in block.expressions:
            self._transpile_stmt(stmt, indent)

    def _transpile_stmt(self, node: Parser.AST, indent: int):
        if isinstance(node, Parser.Expression):
            if node.op.op == "=":
                line = self._emit_assignment(node)
                self._emit(line, indent)
            else:
                self._emit(self._emit_expr(node), indent)
            return

        if isinstance(node, Parser.FunctionCall):
            self._emit(self._emit_call(node), indent)
            return

        if isinstance(node, Parser.WhileLoop):
            cond = self._emit_expr(node.condition)
            self._emit(f"while {cond}:", indent)
            self._transpile_block(node.block, indent + 1)
            return

        if isinstance(node, Parser.IfElse):
            cond = self._emit_expr(node.condition)
            self._emit(f"if {cond}:", indent)
            self._transpile_block(node.if_branch, indent + 1)
            self._emit("else:", indent)
            self._transpile_block(node.else_branch, indent + 1)
            return

        if isinstance(node, Parser.Return):
            if node.val is None:
                self._emit("return", indent)
            else:
                self._emit(f"return {self._emit_expr(node.val)}", indent)
            return

        raise TypeError(f"Unexpected stmt node in transpiler: {node!r}")

    def _emit_expr(self, node: Parser.AST) -> str:
        # literals
        if isinstance(node, Parser.NumberLiteral):
            return repr(node.val)

        if isinstance(node, Parser.StringLiteral):
            return repr(node.val)

        if isinstance(node, Parser.Identifier):
            return node.val

        if isinstance(node, Parser.Array):
            elems = ", ".join(self._emit_expr(e) for e in node.val)
            return f"[{elems}]"

        if isinstance(node, Parser.ArrAcc):
            name = node.name.val
            idx = self._emit_expr(node.idx)
            try:
                idx = int(float(idx))
            except:
                pass
            return f"{name}[int({idx})]"

        if isinstance(node, Parser.FunctionCall):
            return self._emit_call(node)

        if isinstance(node, Parser.Expression):
            op = node.op.op
            if op == "/":
                op = "//"
            left = self._emit_expr(node.lterm)
            right = self._emit_expr(node.rterm)
            return f"({left} {op} {right})"
        raise TypeError(f"Unexpected expr node in transpiler: {node!r}")

    def _emit_assignment(self, expr: Parser.Expression) -> str:
        assert expr.op.op == "="

        if isinstance(expr.lterm, Parser.ArrAcc):
            idx_expr = self._emit_expr(expr.lterm.idx)
            try:
                idx_expr = float(self._emit_expr(expr.lterm.idx))
            except:
                pass
            lhs = f"{expr.lterm.name.val}[int({idx_expr})]"
        else:
            lhs = self._emit_expr(expr.lterm)

        rhs = self._emit_expr(expr.rterm)
        return f"{lhs} = {rhs}"

    def _emit_call(self, call: Parser.FunctionCall) -> str:
        name = call.name
        arg = "" if call.param is None else self._emit_expr(call.param)
        return f"{name}({arg})"


class Interpreter:
    def __init__(self, tree: Parser.Program) -> None:
        self.tree = tree
        self.functions: dict[str, Parser.Function] = {}
        self.builtins = {
            "print": lambda p: print(f"DSL> {p}"),
            "inpstr": lambda _: inp_str(),
            "inpnum": lambda _: inp_num(),
        }
        self.block_contexts: dict[str, dict[str, object]] = {}

    def _ensure_scope(self, scope_name: str) -> dict:
        return self.block_contexts.setdefault(scope_name, {})

    def _execute_fun_call(self, fun: Parser.FunctionCall, from_scope: str):
        if fun.name in self.builtins:
            return self.builtins[fun.name](self._eval_expr(fun.param, from_scope))

        self._ensure_scope(fun.name)
        fn_def = self.functions[fun.name]

        if fn_def.param and fun.param is not None:
            if isinstance(fun.param, Parser.Identifier):
                caller_ctx = self.block_contexts.get(from_scope, {})
                arg_name = fun.param.eval(from_scope, self)
                arg_val = caller_ctx[arg_name]
            elif isinstance(fun.param, Parser.NumberLiteral):
                arg_val = fun.param.val
            else:
                arg_val = self._execute_fun_call(fun.param, self)
            self.block_contexts[fun.name][fn_def.param] = arg_val

        return self._execute_fun_body(fn_def)

    def _eval_expr(self, exp: Parser.AST | None, scope: str):
        if exp is None:
            return None

        if isinstance(exp, Parser.Identifier):
            ctx = self._ensure_scope(scope)
            return ctx.get(exp.eval(scope, self))

        if isinstance(exp, Parser.Expression):
            if exp.op.op == "=":
                ctx = self._ensure_scope(scope)

                if isinstance(exp.lterm, Parser.ArrAcc):
                    arr_name = exp.lterm.name.eval(scope, self)
                    arr_idx = exp.lterm.idx.eval(scope, self)
                    if isinstance(arr_idx, str):
                        arr_idx = ctx[arr_idx]

                    if isinstance(exp.rterm, Parser.Identifier):
                        rt = ctx[exp.rterm.eval(scope, self)]
                    else:
                        rt = exp.rterm.eval(scope, self)

                    ctx[arr_name][int(arr_idx)] = rt
                    return True

                if isinstance(exp.rterm, Parser.FunctionCall):
                    rterm = self._execute_fun_call(exp.rterm, scope)
                else:
                    rterm = exp.rterm.eval(scope, self)

                var_name = exp.lterm.eval(scope, self)
                ctx[var_name] = rterm
                return True

            return exp.eval(scope, self) if exp is not None else None

        return exp.eval(scope, self)

    def _execute_fun_body(self, fun: Parser.Function):
        self._ensure_scope(fun.name)

        for e in fun.body.expressions:
            t = type(e)
            match t:
                case Parser.Expression:
                    self._eval_expr(e, fun.name)

                case Parser.FunctionCall:
                    self._execute_fun_call(e, fun.name)

                case Parser.WhileLoop:
                    while e.eval_cond(fun.name, self):
                        loop_fun = Parser.Function(
                            name=fun.name, param=None, body=e.block
                        )
                        ret = self._execute_fun_body(loop_fun)
                        if ret is not None:
                            return ret

                case Parser.IfElse:
                    cond = e.eval_cond(fun.name, self)
                    branch = e.if_branch if cond else e.else_branch
                    branch_fun = Parser.Function(name=fun.name, param=None, body=branch)
                    ret = self._execute_fun_body(branch_fun)
                    if ret is not None:
                        return ret

                case Parser.Return:
                    if e.val is None:
                        return None
                    if isinstance(e.val, Parser.Expression):
                        return self._eval_expr(e.val, fun.name)
                    return e.eval(fun.name, self)

                case _:
                    raise Exception(f"Unknown AST node in body: {e!r}")

        return None

    def interpret(self):
        # register functions
        for f in self.tree.functions:
            self.functions[f.name] = f

        if "main" not in self.functions:
            raise RuntimeError("No 'main' function defined")

        result = self._execute_fun_body(self.functions["main"])

        print("^" * 80)
        pp(self.block_contexts)
        return result


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(f"Usage: {argv[0]} <source.dsl> [--emit-py]")
        return 1

    filename = argv[1]
    mode = "run"
    if len(argv) >= 3 and argv[2] == "--emit-py":
        mode = "emit-py"

    with open(filename) as f:
        txt = f.read()

    # print(txt)
    # for t in tokenizer(txt):
    #     print(t)
    # print("PARSER")

    parser = Parser(tokenizer(txt))

    try:
        prog = parser.parse()

        if mode == "emit-py":
            transpiler = PythonTranspiler(prog)
            py_src = transpiler.transpile()
            print(py_src)
            return 0

        interp = Interpreter(prog)
        interp.interpret()
        return 0

    except SyntaxError as e:
        print(f"Syntax error: {getattr(e, 'msg', str(e))}")
        print(f"File: {filename}")
        return 1


if __name__ == "__main__":
    rc = main(sys.argv)
    if rc:
        os._exit(rc)
