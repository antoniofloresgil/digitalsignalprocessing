"""Find which earlier code cells each code cell of a chapter depends on.

Reads the Python cells of a .qmd file and, for every cell k, finds the indices (in
document order) of the earlier cells that must run before it so that every name
it uses is defined.

The analysis is static and works at the level of names: a cell depends on the
nearest earlier cell that binds each name it uses and does not bind itself
beforehand, and dependencies are followed transitively. Builtins are ignored.

Used by tools/filters/live-cells.lua (`--json file.qmd`) to make each cell of the
HTML edition runnable on its own in the browser. To inspect a chapter:

    python tools/live_deps.py --report chapters/05-dft-and-fft.qmd
"""
import ast
import builtins
import json
import re
import sys

BUILTINS = set(dir(builtins)) | {"__name__", "__file__"}


def bound_inside(node):
    """Every name that code under `node` binds, however deeply nested (over-approximation)."""
    names = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            names.add(n.id)
        elif isinstance(n, ast.arg):
            names.add(n.arg)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(n.name)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                names.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, ast.ExceptHandler) and n.name:
            names.add(n.name)
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            names.update(n.names)
    return names


class Flow(ast.NodeVisitor):
    """Walks a cell in execution order, collecting external uses and module-level bindings."""

    def __init__(self, late_defined):
        self.defined = set()          # module-level names bound so far
        self.external = set()         # names used before being bound in this cell
        self.scopes = []              # stack of local-name sets (function, lambda, comprehension)
        self.late_defined = late_defined

    # -- names
    def load(self, name):
        if name in BUILTINS or any(name in s for s in self.scopes):
            return
        if self.scopes and name in self.late_defined:      # function bodies run later
            return
        if name not in self.defined:
            self.external.add(name)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.load(node.id)
        elif not self.scopes:
            self.defined.add(node.id)

    # -- statements whose evaluation order differs from the field order
    def visit_Assign(self, node):
        self.visit(node.value)
        for t in node.targets:
            self.visit(t)

    def visit_AnnAssign(self, node):
        if node.value:
            self.visit(node.value)
        self.visit(node.target)

    def visit_AugAssign(self, node):
        self.visit(node.value)
        if isinstance(node.target, ast.Name):
            self.load(node.target.id)
        self.visit(node.target)

    def visit_NamedExpr(self, node):
        self.visit(node.value)
        self.visit(node.target)

    def visit_For(self, node):
        self.visit(node.iter)
        self.visit(node.target)
        for s in node.body + node.orelse:
            self.visit(s)

    visit_AsyncFor = visit_For

    def visit_Import(self, node):
        if not self.scopes:
            for a in node.names:
                self.defined.add((a.asname or a.name).split(".")[0])

    visit_ImportFrom = visit_Import

    # -- scopes
    def scoped(self, node, parts):
        local = bound_inside(node)
        self.scopes.append(local)
        for p in parts:
            self.visit(p)
        self.scopes.pop()

    def visit_FunctionDef(self, node):
        for d in node.decorator_list + node.args.defaults + [d for d in node.args.kw_defaults if d]:
            self.visit(d)
        self.scoped(node, node.body)
        if not self.scopes:
            self.defined.add(node.name)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        for d in node.decorator_list + node.bases:
            self.visit(d)
        self.scoped(node, node.body)
        if not self.scopes:
            self.defined.add(node.name)

    def visit_Lambda(self, node):
        for d in node.args.defaults:
            self.visit(d)
        self.scoped(node, [node.body])

    def comprehension(self, node):
        first = node.generators[0].iter                    # evaluated in the enclosing scope
        self.visit(first)
        local = bound_inside(node)
        self.scopes.append(local)
        for i, g in enumerate(node.generators):
            if i:
                self.visit(g.iter)
            for c in g.ifs:
                self.visit(c)
        parts = [node.key, node.value] if isinstance(node, ast.DictComp) else [node.elt]
        for p in parts:
            self.visit(p)
        self.scopes.pop()

    visit_ListComp = visit_SetComp = visit_DictComp = visit_GeneratorExp = comprehension


def analyze(code):
    """Return (names the cell binds at module level, names it needs from earlier cells)."""
    tree = ast.parse(code)
    late = set()
    for stmt in tree.body:                                  # module-level bindings, anywhere in the cell
        for n in ast.walk(stmt):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                late.add(n.id)
            elif isinstance(n, (ast.FunctionDef, ast.ClassDef)):
                late.add(n.name)
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                late.update((a.asname or a.name).split(".")[0] for a in n.names)
    flow = Flow(late)
    for stmt in tree.body:
        flow.visit(stmt)
    return flow.defined, flow.external


def dependencies(cells):
    infos = [analyze(c) for c in cells]
    result = []
    for k in range(len(cells)):
        seen, stack = set(), [k]
        while stack:
            i = stack.pop()
            for name in infos[i][1]:
                j = next((j for j in range(i - 1, -1, -1) if name in infos[j][0]), None)
                if j is not None and j not in seen:
                    seen.add(j)
                    stack.append(j)
        result.append(sorted(seen))
    return result


def cells_of(qmd):
    text = open(qmd, encoding="utf-8").read()
    return ["\n".join(l for l in m.group(1).splitlines() if not l.startswith("#|"))
            for m in re.finditer(r"```\{python\}\n(.*?)```", text, re.S)]


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--report":
        for path in sys.argv[2:]:
            cells = cells_of(path)
            print(path)
            for k, d in enumerate(dependencies(cells)):
                print(f"  cell {k:2d} needs {d}")
    elif len(sys.argv) == 3 and sys.argv[1] == "--json":
        cells = cells_of(sys.argv[2])
        json.dump([{"code": c, "deps": d} for c, d in zip(cells, dependencies(cells))], sys.stdout)
    else:
        sys.exit(__doc__)
