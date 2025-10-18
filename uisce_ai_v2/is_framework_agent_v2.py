# Uisce-AI v2 — CLI agent that thinks in UUL
from uul_parser import parse
from english_to_uul import to_uul
from uul_to_english import to_english
from uul_grammar import render
from proportional_logic import check_epp

BANNER = """Uisce-AI v2 (UUL-native)
Type 'uul: <text>' to enter raw UUL; otherwise type English.
Type 'quit' to exit.
"""

def main():
    print(BANNER)
    while True:
        try:
            raw = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not raw:
            continue
        if raw.lower() in {"quit", "exit"}:
            break
        uul = raw[4:].strip() if raw.startswith("uul:") else to_uul(raw)
        ast = parse(uul)
        verdict = check_epp(ast)
        print(f"\n[UUL] {uul}")
        print("[AST]")
        print(render(ast))
        print(f"[EPP] {verdict.ok} — {verdict.reason}")
        print("[EN ]", to_english(ast))
        print()

if __name__ == "__main__":
    main()
