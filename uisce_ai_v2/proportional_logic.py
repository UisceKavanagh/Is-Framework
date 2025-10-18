# Uisce-AI v2 — Epistemic Proportionality (EPP) engine
from uul_grammar import AST, NodeType

class EPPResult:
    def __init__(self, ok: bool, reason: str):
        self.ok = ok
        self.reason = reason
    def __repr__(self):
        return f"EPPResult(ok={self.ok}, reason={self.reason})"

def check_epp(ast: AST) -> EPPResult:
    if ast.type != NodeType.SEQ or not ast.children:
        return EPPResult(False, "Empty or non-sequence input.")
    maps = [n for n in ast.children if n.type == NodeType.MAP]
    if not maps:
        return EPPResult(False, "No causal mapping (→) found.")
    for m in maps:
        left, right = m.children or [None, None]
        left_has_action = _has_type(left, NodeType.ASSERT)
        right_has_reason = _has_type(right, NodeType.ASSERT)
        right_has_prop = _has_type(right, NodeType.PROP)
        right_has_ethic = _has_type_value(right, NodeType.META, {"consent", "need"})
        if left_has_action and right_has_reason and right_has_prop and right_has_ethic:
            return EPPResult(True, "Structure satisfies EPP minimally.")
    return EPPResult(False, "Causal mapping missing required proportional/ethical components.")

def _walk(n: AST):
    if not n:
        return
    yield n
    for ch in n.children or []:
        yield from _walk(ch)

def _has_type(n: AST, t: NodeType) -> bool:
    return any(x.type == t for x in _walk(n))

def _has_type_value(n: AST, t: NodeType, values: set) -> bool:
    return any(x.type == t and (x.value in values if x.value else False) for x in _walk(n))
