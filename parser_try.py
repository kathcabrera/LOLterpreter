import re
from dataclasses import dataclass
from typing import Any, List, Tuple

#tokens
@dataclass
class Token:
    type: str
    lexeme: str
    line: int
    col: int

class ScanError(Exception): ...
class ParseError(Exception): ...

#longest multi word first
MULTI = [
    ("SUM_OF",        r"SUM\s+OF"),
    ("DIFF_OF",       r"DIFF\s+OF"),
    ("PRODUKT_OF",    r"PRODUKT\s+OF"),
    ("QUOSHUNT_OF",   r"QUOSHUNT\s+OF"),
    ("MOD_OF",        r"MOD\s+OF"),
    ("BIGGR_OF",      r"BIGGR\s+OF"),
    ("SMALLR_OF",     r"SMALLR\s+OF"),
    ("BOTH_SAEM",     r"BOTH\s+SAEM"),
    ("BOTH_OF",       r"BOTH\s+OF"),
    ("EITHER_OF",     r"EITHER\s+OF"),
    ("WON_OF",        r"WON\s+OF"),
    ("ALL_OF",        r"ALL\s+OF"),
    ("ANY_OF",        r"ANY\s+OF"),
]

# Single-word tokens
SIMPLE = {
    #program header/footer
    "HAI": "HAI",
    "KTHXBYE": "KTHXBYE",
    "WAZZUP": "WAZZUP",
    "BUHBYE": "BUHBYE",

    #var decl syntax
    "I": "I",
    "HAS": "HAS",
    "A": "A",
    "ITZ": "ITZ",

    #printing + glue + operators
    "VISIBLE": "VISIBLE",
    "AN": "AN",
    "OF": "OF",
    "NOT": "NOT",
    "SMOOSH": "SMOOSH",
    "MKAY": "MKAY",
    "MAEK": "MAEK",

    #types and troof literals
    "NUMBR": "TYPE",
    "NUMBAR": "TYPE",
    "YARN": "TYPE",
    "TROOF": "TYPE",
    "WIN": "TROOF_LIT",
    "FAIL": "TROOF_LIT",

    
}

RE_ID    = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
RE_INT   = re.compile(r"-?(?:0|[1-9][0-9]*)")
RE_FLOAT = re.compile(r"-?(?:\d+\.\d*|\d*\.\d+)(?:[eE][+-]?\d+)?")
RE_STR   = re.compile(r'"(?:[^"\\]|\\.)*"')

#lexer
def lex(src: str) -> List[Token]:
    
    src = src.lstrip("\ufeff")
    src = src.replace("\r\n", "\n").replace("\r", "\n")
    src = re.sub(r"[\u2028\u2029]", "\n", src)
    # Strip multiline comments
    src = re.sub(r"OBTW[\s\S]*?TLDR", "", src)

    toks: List[Token] = []
    i = 0
    n = len(src)
    line, col = 1, 1

    def add(tt, lx, l, c):
        toks.append(Token(tt, lx, l, c))

    while i < n:
        ch = src[i]

        #NEWLINE
        if ch == "\n":
            add("NEWLINE", "\\n", line, col)
            i += 1; line += 1; col = 1
            continue

        #BTW 
        if src.startswith("BTW", i):
            while i < n and src[i] != "\n":
                i += 1
                col += 1
            continue

        #skip other whitspace
        if ch.isspace():
            i += 1; col += 1
            continue

        #Multi-word keywords
        matched = False
        for tname, pat in MULTI:
            m = re.match(pat, src[i:])
            if m:
                s = m.group(0)
                add(tname, s, line, col)
                i += len(s); col += len(s)
                matched = True
                break
        if matched:
            continue

        #Single-word uppercase keywords
        mword = re.match(r"[A-Z]+", src[i:])
        if mword:
            w = mword.group(0)
            if w in SIMPLE:
                add(SIMPLE[w], w, line, col)
                i += len(w); col += len(w)
                continue

        #string
        m = RE_STR.match(src, i)
        if m:
            s = m.group(0)
            add("YARN_LIT", s, line, col)
            i = m.end(); col += len(s)
            continue

        #float
        m = RE_FLOAT.match(src, i)
        if m and ('.' in m.group(0) or 'e' in m.group(0).lower()):
            s = m.group(0)
            add("NUMBAR_LIT", s, line, col)
            i = m.end(); col += len(s)
            continue

        #integer
        m = RE_INT.match(src, i)
        if m:
            s = m.group(0)
            add("NUMBR_LIT", s, line, col)
            i = m.end(); col += len(s)
            continue

        # Identifier
        m = RE_ID.match(src, i)
        if m:
            s = m.group(0)
            add("IDENT", s, line, col)
            i = m.end(); col += len(s)
            continue

        
        context = src[max(0, i-10): i+30]
        raise ScanError(f"Unknown token at {line}:{col}: {src[i:i+10]!r} | context: {context!r}")

    toks.append(Token("EOF", "", line, col))
    return toks

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
                self.symbols.setdefault(ident, None)
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
        instruction = self.need("VISIBLE").lexeme
        
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
            return self.need("TROOF_LIT").lexeme == "WIN"

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

#helpers
def analyze(source: str):
    toks = lex(source)
    p = Parser(toks)
    ast = p.parse()

    #symbol table
    print("# Symbol table")
    print("symbol_table = {")
    for k, v in p.symbols.items():
        print(f"    {k!r}: {v!r},")
    print("}\n")

    #tuple 
    print("# Tuple")
    pp_tuple(ast); print()

    #Tree
    print("#Tree view")
    pp_tree(ast)

    return p, ast

#main
if __name__ == "__main__":
    import sys, pathlib
    if len(sys.argv) < 2:
        print("Usage: python lol_syntax_analyzer.py <program.lol>")
        sys.exit(1)
    path = pathlib.Path(sys.argv[1])
    src = path.read_text(encoding="utf-8")
    try:
        analyze(src)
    except (ScanError, ParseError) as e:
        print("Syntax error:", e)
        sys.exit(2)
