# Uisce-AI v2 — UUL → English verbalizer
from uul_grammar import AST, NodeType

def to_english(ast: AST) -> str:
    maps = [n for n in (ast.children or []) if n.type == NodeType.MAP]
    if not maps:
        return "I cannot find a proportional mapping (→) to justify an action."
    left, right = maps[0].children or [None, None]
    action_words = _collect_terms(left)
    reasons = _collect_terms(right, include={"prop", "reason"})
    flags = _collect_terms(right, include={"consent", "need"})
    parts = []
    if action_words:
        parts.append(f"Action: {' '.join(action_words)}")
    if reasons:
        parts.append(f"Justification: {' '.join(reasons)}")
    if flags:
        parts.append(f"Ethics: {' '.join(flags)}")
    return " | ".join(parts) if parts else "Parsed but found no content."

def _collect_terms(n: AST, include: set = None):
    words = []
    for ch in n.children or []:
        if ch.type == NodeType.SEQ:
            words += _collect_terms(ch, include)
        else:
            if include is None:
                if ch.value: words.append(ch.value)
            elif ch.value in include:
                words.append(ch.value)
    return words
