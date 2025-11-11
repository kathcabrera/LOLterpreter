import sys
import re
from dataclasses import dataclass

#one instance per lexeme
@dataclass
class Token:
    kind: str #KEYWORD, IDENT, NUMBR, NUMBAR, YARN, TROOF, TYPE
    lexeme: str #exact text
    line: int #line number of token first char
    col: int #col number of token first char

#Regex building blocks

# Literals
YARN_RE   = r'"(?:[^"\\]|\\.)*"'                       
NUMBAR_RE = r'-?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?' #floats
NUMBR_RE  = r'-?\d+' #integers
TROOF_RE  = r'\b(?:WIN|FAIL)\b' #boolean
TYPE_RE   = r'\b(?:NOOB|NUMBR|NUMBAR|YARN|TROOF)\b' #type

#Keywords
KEYWORDS = [
    r'FOUND\s+YR', r'I\s+IZ', r'I\s+HAS\s+A', r'IS\s+NOW\s+A',
    r'SUM\s+OF', r'DIFF\s+OF', r'PRODUKT\s+OF', r'QUOSHUNT\s+OF', r'MOD\s+OF',
    r'BIGGR\s+OF', r'SMALLR\s+OF', r'BOTH\s+OF', r'EITHER\s+OF', r'WON\s+OF',
    r'ANY\s+OF', r'ALL\s+OF', r'BOTH\s+SAEM',
    r'O\s+RLY\?', r'YA\s+RLY', r'NO\s+WAI', r'WTF\?',r'AN',
    r'GIMMEH', r'VISIBLE', r'SMOOSH', r'MAEK', r'DIFFRINT', r'NOT',
    r'BTW', r'OBTW', r'TLDR', r'HAI', r'KTHXBYE', r'WAZZUP', r'BUHBYE',
    r'ITZ', r'R', r'OIC', r'MEBBE', r'A', r'MKAY'
]
#Long words are checked first
KEYWORDS.sort(key=lambda s: len(s), reverse=True)

KEYWORD_ALT = r'(?<!\w)(?:' + r'|'.join(KEYWORDS) + r')(?!\w)'

#for comments and whitespace
LINE_COMMENT_RE  = r'BTW[^\n]*' #after BTW to end of line
BLOCK_COMMENT_RE = r'OBTW(?:.|\n)*?TLDR'#non-greedy across lines
SKIP_WS_RE       = r'[ \t\r]+'#skip space and tabs

# Identifier 
#determines the role
IDENT_RE = r'[A-Za-z_][A-Za-z0-9_]*'

#Master token
TOKEN_SPEC = [
    ('BLOCK_COMMENT', BLOCK_COMMENT_RE),
    ('LINE_COMMENT',  LINE_COMMENT_RE),
    ('NEWLINE',        r'\n'),
    ('SKIP',           SKIP_WS_RE),

    #Literals
    ('YARN',           YARN_RE),
    ('NUMBAR',         NUMBAR_RE),
    ('NUMBR',          NUMBR_RE),
    ('TROOF',          TROOF_RE),
    ('TYPE',           TYPE_RE),

    #Keywords
    ('KEYWORD',        KEYWORD_ALT),

    #Identifier
    ('IDENT',          IDENT_RE),

    #Others
    ('MISMATCH',       r'.'),
]
#Compile a single master regex with named groups
MASTER_RE = re.compile('|'.join(f'(?P<{name}>{pat})' for name, pat in TOKEN_SPEC),
                       re.MULTILINE)

#iterates through the text left to right
def lex(text: str):
    line = 1
    col_start_of_line = 0
    
    #iterates over every match of MATCH_RE
    for m in MASTER_RE.finditer(text):
        kind = m.lastgroup #checks named group
        lexeme = m.group() #checks the exact text that matched

        if kind == 'NEWLINE':
            line += 1
            col_start_of_line = m.end()
            continue
        #Whitespace and comments are ignored 
        if kind in ('SKIP', 'LINE_COMMENT', 'BLOCK_COMMENT'):
            continue
        #if no match then error on token
        if kind == 'MISMATCH':
            # You can raise here; for milestone we’ll just report it
            c = m.start() - col_start_of_line + 1
            yield Token('ERROR', lexeme, line, c)
            continue

        col = m.start() - col_start_of_line + 1

        #Normalize KEYWORD lexeme
        if kind == 'KEYWORD':
            lexeme = re.sub(r'\s+', ' ', lexeme)
        
        if kind == 'YARN':
            inner = lexeme[1:-1]
            yield Token('STRING_QUOTE', '"', line, col)
            # Unescape display? The spec example shows raw inner; keep raw inner text
            yield Token('YARN_INNER', inner, line, col + 1)
            yield Token('STRING_QUOTE', '"', line, col + len(lexeme) - 1)
            continue

        yield Token(kind, lexeme, line, col)

#Category mapping for keywords to required labels
CODE_DELIMS = {'HAI', 'KTHXBYE'}
VARLIST_DELIMS = {'WAZZUP', 'BUHBYE'}
VAR_DECL = {'I HAS A'}
ASSIGN_FOLLOWING_IHAS = {'ITZ'}
OUTPUT_KEYWORDS = {'VISIBLE'}
MULTI_PARAM_SEP = {'AN'}
ARITH_OPS = {'SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF'}
COMP_OPS  = {'BIGGR OF', 'SMALLR OF', 'BOTH SAEM', 'DIFFRINT', 'EITHER OF', 'BOTH OF', 'WON OF', 'ALL OF', 'ANY OF'}

def print_labelled(tokens):
     for t in tokens:
        if t.kind == 'KEYWORD':
            k = t.lexeme
            if k in CODE_DELIMS:
                print(f"Code Delimiter {k} ")
            elif k in VARLIST_DELIMS:
                print(f"Variable List Delimiter {k} ")
            elif k in VAR_DECL:
                print(f"Variable Declaration {k} ")
            elif k in ASSIGN_FOLLOWING_IHAS:
                print(f"Variable Assignment (following I HAS A) {k} ")
            elif k in OUTPUT_KEYWORDS:
                print(f"Output Keyword {k} ")
            elif k in MULTI_PARAM_SEP:
                print(f"Multiple Parameter Separator {k} ")
            elif k in ARITH_OPS:
                print(f"Arithmetic Operator {k} ")
            elif k in COMP_OPS:
                print(f"Comparison Operator {k} ")
            else:
                
                print(f"Keyword {k} ")

        elif t.kind == 'IDENT':
            print(f"Variable Identifier {t.lexeme} ")

        elif t.kind == 'NUMBR':
            print(f"Integer Literal {t.lexeme} {t.lexeme}")

        elif t.kind == 'NUMBAR':
            print(f"Float Literal {t.lexeme} {t.lexeme}")

        elif t.kind == 'TROOF':
            if t.lexeme == 'WIN':
                print(f"Boolean Value (True) WIN WIN")
            else:
                print(f"Boolean Value (False) FAIL FAIL")

        elif t.kind == 'TYPE':
            print(f"Type Literal {t.lexeme} {t.lexeme}")

        elif t.kind == 'STRING_QUOTE':
            print('String Delimiter " ')

        elif t.kind == 'YARN_INNER':
            print(f"String Literal {t.lexeme} {t.lexeme}")

        elif t.kind == 'ERROR':
            print(f"LEXICAL ERROR {t.lexeme}")

def main():
    #reads the file input
    if len(sys.argv) != 2:
        print("Usage: python lol_lexer.py <source.lol>")
        sys.exit(1)

    #Read the file as UTF-8 text
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        code = f.read()

    tokens = list(lex(code))
    print_labelled(tokens)

if __name__ == '__main__':
    main()
