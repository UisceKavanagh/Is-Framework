# Uisce-AI v2 — UUL tokenizer & parser
from typing import List
from uul_grammar import Token, AST, NodeType, UUL_LEXEMES

SEPARATORS = {" ", "\t", "\n"}
SPECIAL = {"→"}

def tokenize(uul: str) -> List[Token]:
    uul = uul.strip()
    out: List[Token] = []
    buf = ""
    def flush():
        nonlocal buf
        if buf:
            out.append(Token("WORD", buf))
            buf = ""
    for ch in uul:
        if ch in SEPARATORS:
            flush()
        elif ch in SPECIAL:
            flush()
            out.append(Token("SYM", ch))
        else:
            buf += ch
    flush()
    return out

def to_ast(tokens: List[Token]) -> AST:
    clauses: List[List[Token]] = [[]]
    for t in tokens:
        if t.value == "ka":
            clauses.append([])
        else:
            clauses[-1].append(t)

    def lex_node(tok: Token) -> AST:
        kind = UUL_LEXEMES.get(tok.value)
        if kind is None:
            return AST(NodeType.ASSERT, value=tok.value)
        return AST(kind, value=tok.value)

    seq_children: List[AST] = []
    for clause in clauses:
        if not clause:
            continue
        if any(t.value == "→" for t in clause):
            left, right, side = [], [], "L"
            for t in clause:
                if t.value == "→":
                    side = "R"
                    continue
                (right if side == "R" else left).append(t)
            seq_children.append(AST(NodeType.MAP, children=[
                AST(NodeType.SEQ, children=[lex_node(t) for t in left]),
                AST(NodeType.SEQ, children=[lex_node(t) for t in right]),
            ]))
        else:
            seq_children.extend(lex_node(t) for t in clause)
    return AST(NodeType.SEQ, children=seq_children)

def parse(uul: str) -> AST:
    return to_ast(tokenize(uul))
