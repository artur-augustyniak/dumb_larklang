#!/usr/bin/env python3
from lark import Lark, Tree, Token
from lark.visitors import Interpreter
import math


dsl_grammar = r"""
    ?program: function* main

    main: "main" "(" ")" block

    // one optional parameter
    function: IDENTIFIER "(" [IDENTIFIER] ")" block

    block: "{" statement* "}"

    ?statement: expr ";"        -> stmt_expr
              | while_loop
              | if_else

    while_loop: "while" "(" expr ")" block
    if_else: "if" "(" expr ")" block "else" block

    // ----- expressions with precedence -----

    ?expr: assignment

    // assignment has lowest precedence
    ?assignment: IDENTIFIER "=" expr   -> asign
               | logic

    // comparisons (==, <, >)
    ?logic: sum OPERATOR sum           -> bin_expr
          | sum

    // + and -
    ?sum: sum OPERATORC term           -> bin_expr_c
         | term

    // * and /
    ?term: term OPERATORB power        -> bin_expr_b
          | power

    // exponentiation (^), right-associative
    ?power: atom
          | atom OPERATORA power       -> bin_expr_a

    // unary + / -
    ?atom: OPERATORC atom              -> unary_exp
          | primary

    // "primary" things
    ?primary: NUMBER_LITERAL                 -> number
             | STRING_LITERAL                -> string
             | IDENTIFIER "(" [expr] ")"     -> function_call
             | IDENTIFIER "[" expr "]" "=" expr -> arr_assign
             | IDENTIFIER "[" expr "]"       -> arr_acc
             | IDENTIFIER                    -> identifier
             | "[" [expr ("," expr)*] ","? "]" -> arr_decl
             | "(" expr ")"                  -> expr_paren
             | "return" [expr]               -> ret

    // ----- tokens -----

    OPERATORA: "^"
    OPERATORB: "*" | "/"
    OPERATORC: "+" | "-"
    OPERATOR: "==" | "<" | ">"

    NUMBER_LITERAL: /[0-9]+/
    STRING_LITERAL: "\"" /[^\n"]*/ "\""
    IDENTIFIER: /[a-z]+/

    %ignore /[ \t\r\n]+/
    %ignore /#.*/   // line comments starting with '#'
"""


OPERATORS = {
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "<": lambda a, b: a < b,
    ">": lambda a, b: a > b,
    "==": lambda a, b: a == b,
    "^": lambda a, b: a**b,
}


def inp_str():
    print("DSL<(str)")
    return input()


def inp_num():
    print("DSL<(num)")
    return float(input())


def sqrt(x):
    return math.sqrt(x)


class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


class DslInterpreter(Interpreter):
    def __init__(self, env_arg=0, dsl_builtins={}):
        super().__init__()
        self.env_arg = env_arg
        self.current_function = None
        self.functions = {}
        self.block_contexts = {}
        self.functions["print"] = ("builtin", lambda arg: print(f"DSL> {arg}"))
        self.functions["inpstr"] = ("builtin", lambda _arg: inp_str())
        self.functions["inpnum"] = ("builtin", lambda _arg: inp_num())
        self.functions["sqrt"] = ("builtin", lambda _arg: sqrt(_arg))
        self.functions.update(dsl_builtins)

    def _ctx(self):
        return self.block_contexts.setdefault(self.current_function, {})

    def _get_var(self, name: str):
        ctx = self._ctx()
        if name not in ctx:
            raise NameError(
                f"Undefined variable '{name}' in function {self.current_function}"
            )
        return ctx[name]

    def _set_var(self, name: str, value):
        ctx = self._ctx()
        ctx[name] = value
        return value

    def program(self, tree: Tree):
        # register user-defined functions
        main_func = None
        for child in tree.children:
            if isinstance(child, Tree) and child.data == "function":
                if child.children[0].value == "main":
                    main_func = child
                self.visit(child)
        # run main
        for child in tree.children:
            if isinstance(child, Tree) and child.data == "main":
                return self.visit(child)
        raise RuntimeError("No main() function defined")

    def function(self, tree: Tree):
        name_tok = tree.children[0]
        name = name_tok.value

        param_name = None
        if tree.children[1] is not None:
            param_tok = tree.children[1]
            param_name = param_tok.value
            block = tree.children[2]
        else:
            block = tree.children[2]
        self.functions[name] = (
            "user",
            {"tree": tree, "param": param_name, "block": block},
        )
        self.block_contexts.setdefault(
            name, {"params": [param_name] if param_name else []}
        )

    def main(self, tree: Tree):
        old_func = self.current_function
        self.current_function = "main"
        self.block_contexts.setdefault("main", {"params": ["env"], "env": self.env_arg})
        try:
            block = tree.children[0]
            return self.visit(block)
        except ReturnException as e:
            return e.value
        finally:
            self.current_function = old_func

    def block(self, tree: Tree):
        for stmt in tree.children:
            self.visit(stmt)

    def stmt_expr(self, tree: Tree):
        (expr,) = tree.children
        self.visit(expr)

    def number(self, tree: Tree):
        (tok,) = tree.children
        return float(tok.value)

    def string(self, tree: Tree):
        (tok,) = tree.children
        s = tok.value
        return s[1:-1]

    def identifier(self, tree: Tree):
        (tok,) = tree.children
        return self._get_var(tok.value)

    def arr_decl(self, tree: Tree):
        return [self.visit(child) for child in tree.children]

    def arr_acc(self, tree: Tree):
        name_tok, idx_tree = tree.children
        name = name_tok.value
        idx = int(self.visit(idx_tree))
        arr = self._get_var(name)
        return arr[idx]

    def arr_assign(self, tree: Tree):
        name_tok, idx_tree, val_tree = tree.children
        name = name_tok.value
        idx = int(self.visit(idx_tree))
        val = self.visit(val_tree)
        arr = self._get_var(name)
        arr[idx] = val
        return val

    def asign(self, tree: Tree):
        name_tok, expr_tree = tree.children
        name = name_tok.value
        val = self.visit(expr_tree)
        return self._set_var(name, val)

    def unary_exp(self, tree: Tree):
        op_tok, term_tree = tree.children
        term = self.visit(term_tree)
        if op_tok.value == "+":
            return +term
        else:
            return -term

    def bin_expr_a(self, tree: Tree):
        left, op_tok, right = tree.children
        l = self.visit(left)
        r = self.visit(right)
        return OPERATORS[op_tok.value](l, r)

    def bin_expr_b(self, tree: Tree):
        left, op_tok, right = tree.children
        l = self.visit(left)
        r = self.visit(right)
        return OPERATORS[op_tok.value](l, r)

    def bin_expr_c(self, tree: Tree):
        left, op_tok, right = tree.children
        l = self.visit(left)
        r = self.visit(right)
        return OPERATORS[op_tok.value](l, r)

    def bin_expr(self, tree: Tree):
        left, op_tok, right = tree.children
        l = self.visit(left)
        r = self.visit(right)
        return OPERATORS[op_tok.value](l, r)

    def expr_paren(self, tree: Tree):
        (expr_tree,) = tree.children
        return self.visit(expr_tree)

    def while_loop(self, tree: Tree):
        cond_tree, block_tree = tree.children
        while self.visit(cond_tree):
            try:
                self.visit(block_tree)
            except ReturnException as e:
                raise e

    def if_else(self, tree: Tree):
        cond_tree, if_block, else_block = tree.children
        if self.visit(cond_tree):
            self.visit(if_block)
        else:
            self.visit(else_block)

    def ret(self, tree: Tree):
        if not tree.children:
            raise ReturnException(None)
        (expr_tree,) = tree.children
        val = self.visit(expr_tree)
        raise ReturnException(val)

    def function_call(self, tree: Tree):
        if len(tree.children) == 1:
            name_tok = tree.children[0]
            arg_expr = None
        else:
            name_tok, arg_expr = tree.children

        name = name_tok.value

        if name not in self.functions:
            raise NameError(f"Unknown function '{name}'")

        kind, info = self.functions[name]

        if kind == "builtin":
            arg_value = self.visit(arg_expr) if arg_expr else None
            return info(arg_value)

        func_tree = info["tree"]
        param_name = info["param"]
        block = info["block"]

        arg_value = self.visit(arg_expr) if arg_expr else None

        old_func = self.current_function
        self.current_function = name

        ctx = self.block_contexts.setdefault(
            name, {"params": [param_name] if param_name else []}
        )
        if param_name is not None:
            ctx[param_name] = arg_value

        try:
            self.visit(block)
        except ReturnException as e:
            self.current_function = old_func
            return e.value
        finally:
            self.current_function = old_func


def parse_and_execute(text: str, env_arg: str | float | int = 0, dsl_builtins={}):
    parser = Lark(dsl_grammar, start="program", parser="lalr")
    tree = parser.parse(text)
    intr = DslInterpreter(env_arg, dsl_builtins)
    return intr.visit(tree)
