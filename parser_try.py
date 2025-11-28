import re
from lexer import Token, lex
from dataclasses import dataclass
from typing import Any, List, Tuple

class ScanError(Exception): ...
class ParseError(Exception): ...


#ast helpers
def node(tag: str, *children: Any) -> Tuple[str, Any]:
    return (tag, *children)

def pp_tuple(ast):
    import pprint; pprint.pprint(ast, width=100)

def pp_tree(ast, indent=""):
    tag = ast[0]
    print(indent + tag)
    for child in ast[1:]:
        if isinstance(child, tuple):
            pp_tree(child, indent + "│   ")
        else:
            print(indent + "│   " + repr(child))

#parser and evaluator
class Parser:
    def __init__(self, toks: List[Token]):
        self.toks = toks
        self.i = 0
        self.symbols = {}   #symbol table

    #basic stream ops
    def peek(self, k=0): return self.toks[self.i + k]
    def at(self, *types): return self.peek().type in types
    def match(self, *types):
        if self.at(*types):
            t = self.peek(); self.i += 1; return t
        return None
    def need(self, *types):
        t = self.match(*types)
        if not t:
            got = self.peek()
            raise ParseError(f"Expected {'/'.join(types)} at {got.line}:{got.col}, got {got.type} {got.lexeme!r}")
        return t
    def skip_nl(self):
        while self.match("NEWLINE"): pass

    # entry
    def parse(self):
        self.skip_nl()
        self.need("HAI")
        self.need("NEWLINE")
        self.skip_nl()

        wazzup_decls = None
        if self.match("WAZZUP"):
            self.skip_nl()
            wazzup_decls = self.wazzup_block()             

        inline_decls = self.variable_declaration_list_opt() 
        stmts        = self.statement_list_opt()            

        self.skip_nl()
        self.need("KTHXBYE")
        self.skip_nl()
        self.need("EOF")

        # merge decl lists
        decls = None
        if wazzup_decls and inline_decls:
            decls = node("VARIABLE_DECLARATION_LIST", *wazzup_decls[1:], *inline_decls[1:])
        else:
            decls = wazzup_decls or inline_decls or node("VARIABLE_DECLARATION_LIST")

        return node("PROGRAM",
                    decls,
                    stmts if stmts else node("STATEMENT_LIST"))


    #WAZZUP
    def wazzup_block(self):
        items = []
        while self.peek().type == "I":
            self.need("I"); self.need("HAS"); self.need("A")
            ident = self.need("IDENT").lexeme
            if self.match("ITZ"):
                val = self.eval_expr()
                self.symbols[ident] = val
                items.append(node("VARIABLE", ("Identifier", ident), ("Value", val)))
            else:
                self.symbols.setdefault(ident, "NOOB")
                items.append(node("VARIABLE", ("Identifier", ident)))
            self.skip_nl()
        self.need("BUHBYE")
        self.skip_nl()
        return node("VARIABLE_DECLARATION_LIST", *items)


    # Optional variable declarations
    def variable_declaration_list_opt(self):
        while self.peek().type == "I":
            self.need("I"); self.need("HAS"); self.need("A")
            ident = self.need("IDENT").lexeme
            if self.match("ITZ"):
                val = self.eval_expr()
                self.symbols[ident] = val
            else:
                self.symbols.setdefault(ident, None)
            self.skip_nl()

    # Statement list
    def statement_list_opt(self):
        items = []
        while self.peek().type in ("VISIBLE", "IDENT"):
            if self.at("VISIBLE"):
                items.append(self.print_stmt())
            else:
                # assignment
                if self.peek(1).type != "R":
                    break
                self.assign_stmt()
            self.skip_nl()
        return node("STATEMENT_LIST", *items)

    def print_stmt(self):
        self.need("VISIBLE").lexeme
        
        val = self.eval_expr()
        while self.match("AN"):  
            self.eval_expr()
        return node("PRINT", val)
                # items.append(node("VARIABLE", ("Identifier", ident), ("Value", val)))

    def assign_stmt(self):
        name = self.need("IDENT").lexeme
        self.need("R")
        val = self.eval_expr()
        self.symbols[name] = val
        return node("ASSIGN", ("Identifier", name), ("Value", val))

    #expressions
    def eval_expr(self):
        # literals
        if self.at("NUMBR_LIT"):
            return int(self.need("NUMBR_LIT").lexeme)
        if self.at("NUMBAR_LIT"):
            return float(self.need("NUMBAR_LIT").lexeme)
        if self.at("YARN_LIT"):
            s = self.need("YARN_LIT").lexeme
            return bytes(s[1:-1], "utf-8").decode("unicode_escape")
        if self.at("TROOF_LIT"):
            return self.need("TROOF_LIT").lexeme

        # identifier reference
        if self.at("IDENT"):
            name = self.need("IDENT").lexeme
            return self.symbols.get(name, None)

        # arithmetic binary
        if self.at("SUM_OF","DIFF_OF","PRODUKT_OF","QUOSHUNT_OF","MOD_OF","BIGGR_OF","SMALLR_OF"):
            op = self.peek().type; self.i += 1
            a = self.eval_expr(); self.need("AN"); b = self.eval_expr()
            return self._arith(op, a, b)

        # boolean binary
        if self.at("BOTH_OF","EITHER_OF","WON_OF"):
            op = self.peek().type; self.i += 1
            a = self.eval_expr(); self.need("AN"); b = self.eval_expr()
            return self._bool(op, a, b)
        if self.at("NOT"):
            self.i += 1; return not self.eval_expr()
        if self.at("ALL_OF","ANY_OF"):
            op = self.peek().type; self.i += 1
            vals = [self.eval_expr()]; self.need("AN"); vals.append(self.eval_expr())
            while self.match("AN"): vals.append(self.eval_expr())
            self.need("MKAY")
            return all(vals) if op == "ALL_OF" else any(vals)

        # comparison
        if self.at("BOTH_SAEM"):
            self.i += 1; a = self.eval_expr(); self.need("AN"); b = self.eval_expr(); return a == b
        if self.peek().lexeme == "DIFFRINT":   # tokenized as IDENT
            self.i += 1; a = self.eval_expr(); self.need("AN"); b = self.eval_expr(); return a != b

        # concatenation
        if self.at("SMOOSH"):
            self.i += 1
            parts = [str(self.eval_expr())]
            while self.match("AN"): parts.append(str(self.eval_expr()))
            self.need("MKAY"); return "".join(parts)

        # cast
        if self.at("MAEK"):
            self.i += 1; v = self.eval_expr(); self.need("A"); t = self.need("TYPE").lexeme
            return self._cast(v, t)

        got = self.peek()
        raise ParseError(f"Unsupported expression at {got.line}:{got.col}: {got.lexeme!r}")

    def _arith(self, op, a, b):
        if op == "SUM_OF":      return (a or 0) + (b or 0)
        if op == "DIFF_OF":     return (a or 0) - (b or 0)
        if op == "PRODUKT_OF":  return (a or 0) * (b or 0)
        if op == "QUOSHUNT_OF": return (a or 0) / (b or 1)
        if op == "MOD_OF":      return (a or 0) % (b or 1)
        if op == "BIGGR_OF":    return a if a >= b else b
        if op == "SMALLR_OF":   return a if a <= b else b

    def _bool(self, op, a, b):
        if op == "BOTH_OF":   return bool(a) and bool(b)
        if op == "EITHER_OF": return bool(a) or bool(b)
        if op == "WON_OF":    return bool(a) ^ bool(b)

    def _cast(self, v, t):
        if t == "NUMBR": return int(v)
        if t == "NUMBAR": return float(v)
        if t == "YARN":  return "" if v is None else str(v)
        if t == "TROOF": return bool(v)
        return v
