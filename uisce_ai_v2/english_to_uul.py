# Uisce-AI v2 — simple English → UUL translator
import re

def to_uul(english: str) -> str:
    s = english.strip().lower()
    cause, effect = _split_cause_effect(s)
    meta = []
    if re.search(r"\bconsent|permission|agreed|consented\b", s):
        meta.append("consent")
    if re.search(r"\bnecessary|need|must|required|emergency\b", s):
        meta.append("need")
    right = "prop reason"
    if meta:
        right += " " + " ".join(meta)
    return f"is {cause} → {right} ka is {effect}" if effect else f"is {cause} → {right}"

def _split_cause_effect(s: str):
    for cue in [" because ", " so ", " for ", " to "]:
        if cue in s:
            left, right = s.split(cue, 1)
            return left.strip(), right.strip()
    return s, ""
