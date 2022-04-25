import sys
from pathlib import Path

from plox.scanner import Scanner
from plox.parser import Parser
from plox.interpret import Interpreter
from plox.errors import *
from plox.resolver import Resolver

from plox.pprinter import LispPrinter


def run(source):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    result = parser.parse()

    if result is None or Globals.had_error:
        return

    print(LispPrinter().print_program(result))

    interpreter = Interpreter()
    resolver = Resolver(interpreter)
    resolver.resolve_list(result)

    if Globals.had_error:
        return

    interpreter.visit_statements(result)


def run_file(f):
    run(Path(f).read_text(encoding="utf8"))
    if Globals.had_error:
        exit(65)
    if Globals.had_runtime_error:
        exit(70)


def run_prompt():
    while True:
        print("> ", end="", flush=True)
        inp = sys.stdin.readline()
        if len(inp) == 0:
            break
        run(inp)
        Globals.had_error = False


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: plox [script]")
        exit(64)
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_prompt()
