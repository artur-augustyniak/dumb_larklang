# Dumb LarkLang

Dumb LarkLang is a minimal educational programming language implemented in Python
using the **Lark** parsing library. The project demonstrates how to design a small
DSL with variables, arrays, control flow, functions, and basic I/O.

## Goals

- Demonstrate grammar-driven language implementation
- Show a clean separation between parsing and execution
- Provide concise examples of language features

## Project Structure

- `dumblang.py` – language grammar and interpreter (core runtime)
- `execute.py` – CLI entry point for running `.dsl` files
- `embed.py` – example of embedding the interpreter
- `examples/` – curated language examples

## Running Examples

```bash
python execute.py examples/intro_basics.dsl
```

## Examples Overview

- `intro_basics.dsl` – syntax, variables, expressions
- `numeric_operations.dsl` – arithmetic
- `array_operations.dsl` – arrays and indexing
- `sorting_bubble.dsl` – bubble sort implementation
- `full_language_demo.dsl` – combined language features

## License

MIT
