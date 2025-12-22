# Dumb LarkLang

Dumb LarkLang is a small, educational DSL implemented in Python using the
Lark parsing library. It's intended as a learning project that shows how to
design a compact language grammar, implement an interpreter, and optionally
transpile DSL programs to Python.

**Highlights**
- Minimal Lark-based interpreter and AST visitor (`dumblang.py`).
- A handwritten recursive-descent variant in `rd_interpreter/`.
- A simple transpiler to Python (`transpile.py`).
- Embedding example and CLI runner.

**Requirements**
- Python 3.12+
- Dependencies from `pyproject.toml` (uses `lark`).

**Install**
- With pip (recommended for quick runs):

```bash
python -m pip install lark
```

- Or use Poetry (project includes a `pyproject.toml`):

```bash
poetry install
```

**Quick Usage**

- Run a DSL program with the interpreter:

```bash
python execute.py examples/intro_basics.dsl
```

- Transpile a DSL program to Python source (prints to stdout):

```bash
python transpile.py examples/intro_basics.dsl > out.py
python out.py
```

- Run the example embedder (interactive example using `embed.py`):

```bash
python embed.py
```

**API / Embedding**
- Use `parse_and_execute(text, env_arg=0, dsl_builtins={})` from `dumblang.py`
	to parse and run a DSL program from a string. `env_arg` passes an "env"
	parameter into `main()` and `dsl_builtins` allows registering extra builtins.

Built-in functions provided by the runtime:
- `print(x)` — prints prefixed with `DSL>`
- `inpstr()` — prompt and read a string from stdin
- `inpnum()` — prompt and read a number from stdin
- `sqrt(x)` — square root helper

**Project layout**
- `dumblang.py` — primary Lark grammar, `DslInterpreter`, and `parse_and_execute`.
- `execute.py` — tiny CLI runner that reads a `.dsl` file and executes it.
- `transpile.py` — converts parsed DSL AST into Python source.
- `embed.py` — demonstration of embedding the interpreter with custom builtins.
- `rd_interpreter/dumblang_interpreter.py` — older handwritten lexer/parser + interpreter.
- `examples/` — example DSL programs (interactive examples, sorting, math, etc.).

**Examples**
- `intro_basics.dsl` — language basics: variables, expressions, statements.
- `interactive_sum.dsl` — interactive sum reading loop (uses `inpnum`).
- `array_operations.dsl` — arrays and indexing examples.
- `sorting_bubble.dsl` — bubble sort in the DSL.
- `babylonian_method.dsl` — numeric algorithm example (square root).

**Notes & Caveats**
- The project is educational and focuses on clarity over performance. The
	`rd_interpreter` directory contains an alternate hand-rolled parser and
	interpreter implementation for comparison.
- The transpiler emits straightforward Python; generated code is intended for
	inspection and learning rather than production use.

**License**
- MIT

If you want, I can run the transpiler on an example and attach the generated
Python, or add a small `Makefile` / script to run common tasks.
