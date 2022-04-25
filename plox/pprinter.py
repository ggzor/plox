from .ast import *
from .tokens import *


class LispPrinter(ExprVisitor[str], StmtVisitor[str]):
    def __init__(self):
        self.indent = 0

    def print_program(self, program: Program):
        return "\n".join([stmt.accept(self) for stmt in program])

    def print_indent(self, s):
        return " " * self.indent + s

    def visit_block(self, block: Block):
        """
        Returns a lisp like string representation of the block.

        (block)

        (block
            (var x int)
            (var y int)
            (print x)
            (print y))
        """
        s = "(block"
        if len(block.statements) > 0:
            self.indent += 4
            s += "\n" + "\n".join(
                [self.print_indent(stmt.accept(self)) for stmt in block.statements]
            )
            self.indent -= 4
        s += ")"
        return s

    def visit_assign(self, expr: Assign) -> str:
        """
        Returns a lisp like string representation of the assignment.
        (assign x (add x 1))
        """
        return f"(assign {expr.name.lexeme} {expr.value.accept(self)})"

    def visit_binary(self, expr: Binary) -> str:
        """
        Returns a lisp like string representation of the binary expression.
        (+ x 1)
        """
        return f"({expr.operator.lexeme} {expr.left.accept(self)} {expr.right.accept(self)})"

    def visit_grouping(self, expr: Grouping) -> str:
        """
        Returns a lisp like string representation of the grouping expression.
        (grouping (+ x 1))
        """
        return f"(grouping {expr.expression.accept(self)})"

    def visit_literal(self, expr: Literal) -> str:
        """
        Returns a the string representation of the literal.
        1
        "Hello"
        """
        if expr.value is None:
            return "nil"
        elif expr.value is True:
            return "true"
        elif expr.value is False:
            return "false"
        elif isinstance(expr.value, str):
            return f'"{expr.value}"'
        else:
            return str(expr.value)

    def visit_unary(self, expr: Unary) -> str:
        """
        Returns a lisp like string representation of the unary expression.
        (- x 1)
        """
        return f"({expr.operator} {expr.right.accept(self)})"

    def visit_variable(self, expr: Variable) -> str:
        """
        Returns a lisp like string representation of the variable.
        x
        """
        return expr.name.lexeme

    def visit_print(self, expr: Print) -> str:
        """
        Returns a lisp like string representation of the print statement.
        (print x)
        """
        return f"(print {expr.expression.accept(self)})"

    def visit_call(self, expr: Call) -> str:
        """
        Returns a lisp like string representation of the call expression. Each
        argument is printed as a separate line.

        (call f)
        (call f
            (+ 1)
            2)
        """
        s = f"(call {expr.callee.accept(self)}"
        if len(expr.arguments) > 0:
            self.indent += 4
            s += "\n" + "\n".join(
                [self.print_indent(arg.accept(self)) for arg in expr.arguments]
            )
            self.indent -= 4
        s += ")"
        return s

    def visit_expression(self, stmt: Expression) -> str:
        """
        Returns a lisp like string representation of the expression statement.
        (+ x 1)
        """
        return stmt.expression.accept(self)

    def visit_function(self, stmt: Function) -> str:
        """
        Returns a lisp like string representation of the function statement.
        (func f (x y)
              (add x 1))
        """
        s = f'(func {stmt.name.lexeme} ({" ".join([arg.lexeme for arg in stmt.params])})'
        self.indent += 4
        s += "\n" + "\n".join([self.print_indent(s.accept(self)) for s in stmt.body])
        self.indent -= 4
        s += ")"
        return s

    def visit_if(self, stmt: If) -> str:
        """
        Returns a lisp like string representation of the if statement.
        (if (x)
            (print x))
        """
        s = f"(if {stmt.condition.accept(self)}"
        self.indent += 4
        s += "\n" + self.print_indent(stmt.then_branch.accept(self))
        self.indent -= 4
        if stmt.else_branch:
            s += "\n" + self.print_indent(stmt.else_branch.accept(self))
        s += ")"
        return s

    def visit_while(self, stmt: While) -> str:
        """
        Returns a lisp like string representation of the while statement.
        (while (x)
            (print x))
        """
        s = f"(while {stmt.condition.accept(self)}"
        self.indent += 4
        s += "\n" + self.print_indent(stmt.body.accept(self))
        self.indent -= 4
        s += ")"
        return s

    def visit_return(self, stmt: Return) -> str:
        """
        Returns a lisp like string representation of the return statement.
        (return x)
        """
        if stmt.value:
            return f"(return {stmt.value.accept(self)})"
        else:
            return "(return)"

    def visit_logical(self, expr: Logical) -> str:
        """
        Returns a lisp like string representation of the logical expression.
        (or x y)
        """
        left = expr.left.accept(self)
        right = expr.right.accept(self)
        return f"({expr.operator.lexeme} {left} {right})"

    def visit_var(self, stmt: Var) -> str:
        """
        Returns a lisp like string representation of the var statement.
        (var x int)
        """
        if stmt.initializer:
            return f"(var {stmt.name.lexeme} {stmt.initializer.accept(self)})"
        else:
            return f"(var {stmt.name.lexeme})"

    def visit_class(self, stmt: Class) -> str:
        """
        Returns a lisp like string representation of the class statement.
        (class Test
            (func someFunc ()
                (print "Ok")))
        """
        s = f"(class {stmt.name.lexeme}"

        if stmt.superclass:
            s += f" (< {stmt.superclass.name.lexeme})"

        if len(stmt.methods) > 0:
            self.indent += 4
            s += "\n" + "\n".join(
                [self.print_indent(s.accept(self)) for s in stmt.methods]
            )
            self.indent -= 4
        s += ")"
        return s

    def visit_get(self, expr: Get) -> str:
        """
        Returns a lisp like string representation of the get expression.
        (get x y)
        """
        return f"(get {expr.object.accept(self)} {expr.name.lexeme})"

    def visit_set(self, expr: Set) -> str:
        """
        Returns a lisp like string representation of the set expression.
        (set x y value)
        """
        object = expr.object.accept(self)
        value = expr.value.accept(self)
        return f"(set {object} {expr.name.lexeme} {value})"

    def visit_this(self, _: This) -> str:
        return f"this"

    def visit_super(self, expr: Super) -> str:
        return f"({expr.keyword.lexeme} {expr.method.lexeme})"
