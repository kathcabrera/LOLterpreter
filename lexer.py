import re
from dataclasses import dataclass
from typing import List

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