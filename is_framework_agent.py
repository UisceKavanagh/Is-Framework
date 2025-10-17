# is_framework_agent.py
# A minimal reasoning agent implementing the "Is." framework without external APIs.

from dataclasses import dataclass
from typing import Dict

# ======== Primitives (Section 19) ========
# E(x): existence is assumed for all x in this interaction space
# U(x): understood; N(x): non-understood
# F(x): within focus (current dialogue); S(x): sentient (assumed for user); A(y): action

@dataclass
class EPPJudgment:
    reason: bool
    proportion: bool
    consent: bool
    necessity: bool

    def satisfied(self) -> bool:
        # EPP satisfied when Reason and Proportion hold AND
        #   (Consent OR Necessity) is true.
        # For ordinary Q&A we set consent=True upstream.
        return self.reason and self.proportion and (self.consent or self.necessity)

@dataclass
class AgentConfig:
    name: str = "IsFrameworkReasoner"
    show_trace: bool = True

class IsFrameworkAgent:
    def __init__(self, config: AgentConfig = AgentConfig()):
        self.cfg = config
        # simple focus store
        self.focus_memory: Dict[str, Dict] = {}

    # ======== Core Helpers ========

    def _assess_reason(self, prompt: str) -> bool:
        """
        Expanded 'Reason' check.
        Treats any interrogative (question) or declarative with conceptual words
        as reason-seeking or reason-giving.
        """
        p = prompt.lower()
        if p.endswith("?"):
            return True  # any question seeks reason
        keywords = [
            "because", "why", "reason", "justify", "due to", "premise", "proof",
            "explain", "what is", "define", "how does", "how do", "meaning"
        ]
        return any(k in p for k in keywords) or len(p.split()) > 3

    def _assess_proportion(self, prompt: str) -> bool:
        """
        Proportion: refuse sweeping claims with high uncertainty.
        If prompt asks for harmful, medical, legal, or strong assertions without evidence, return False.
        """
        p = prompt.lower()
        high_risk = any(k in p for k in [
            "diagnose", "medical", "illegal", "attack", "harm", "self-harm",
            "terror", "exploit", "hack", "breach", "leak", "defame"
        ])
        unverifiable_certainty = ("100%" in p or "guarantee" in p or "prove reality" in p)
        return not high_risk and not unverifiable_certainty

    def _assess_consent_necessity(self, prompt: str) -> EPPJudgment:
        """
        Consent/Necessity:
          - If a prompt targets doing something TO a sentient subject, require consent or necessity.
          - Otherwise (ordinary Q&A), treat consent as implicitly satisfied (no risk).
        """
        p = prompt.lower()
        targets_person = any(k in p for k in [
            "do this to", "perform on", "experiment on", "apply to"
        ])
        consent = ("consent" in p or "permission" in p)
        necessity = ("necessary" in p or "emergency" in p or "last resort" in p)
        reason = self._assess_reason(prompt)
        proportion = self._assess_proportion(prompt)

        if not targets_person:
            # No direct risk → implicit consent for discussion/answering
            return EPPJudgment(reason=reason, proportion=proportion, consent=True, necessity=False)

        # There IS a target person → require explicit consent/necessity
        return EPPJudgment(reason=reason, proportion=proportion, consent=consent, necessity=necessity)

    def _integrate(self, statement: str) -> str:
        """
        Accept(It(x)) ⇒ U(x): integrate by restating with clarity and limits; transform uncertainty into understanding.
        """
        return f"Integrated understanding: {statement.strip()}"

    def _reject(self, statement: str) -> str:
        """
        Reject(It(x)) ⇒ N(x): if EPP fails, we must refuse.
        """
        return f"Cannot proceed: EPP unmet for: {statement.strip()}"

    # ======== Public API ========

    def respond(self, prompt: str) -> str:
        """
        Main loop: applies EPP, disagreement rule, and integration behavior.
        """
        # Disagreement rule: bare negation without reasons → epistemically irrelevant
        bare_negation = prompt.strip().lower() in {"no", "wrong", "i disagree", "false"} or \
                        (prompt.strip().lower().startswith("disagree") and "because" not in prompt.lower())
        if bare_negation:
            trace = "[Disagreement] No reasons provided → Epistemically irrelevant."
            return self._format(trace, "Disagreement without reason is epistemically irrelevant.")

        # EPP gate
        epp = self._assess_consent_necessity(prompt)
        if not epp.satisfied():
            trace = (f"[EPP] Reason={epp.reason}, Proportion={epp.proportion}, "
                     f"Consent={epp.consent}, Necessity={epp.necessity} → FAIL")
            return self._format(trace, self._reject(prompt))

        # If EPP is satisfied, integrate and answer proportionally
        integration = self._integrate(prompt)
        # Focus logic: treat the current prompt as within focus
        self.focus_memory[prompt] = {"F(x)": True, "Is(x)": True}

        # Produce a proportional, reasoned answer:
        answer = self._proportional_answer(prompt)
        trace = (f"[EPP] Reason={epp.reason}, Proportion={epp.proportion}, "
                 f"Consent={epp.consent or epp.necessity} → PASS | [Focus] captured")
        return self._format(trace, f"{integration}\n\n{answer}")

    def _proportional_answer(self, prompt: str) -> str:
        """
        Very small, safe inference layer showing how conclusions are bounded.
        """
        p = prompt.lower()

        # Examples consistent with the framework:
        if any(k in p for k in ["prove we lived on mars", "did we live on mars"]):
            return ("Within the framework, 'Mars as prior focus' is a coherent relation of focus, "
                    "not a chronological claim. Proportional statement: it is logically consistent as understanding, "
                    "not an empirical past fact.")

        if "what is is" in p or p.strip() == "what is is":
            return ("*Is* = existence integrated with understanding. *It* = existence in non-understanding. "
                    "*I* = localized focus within understanding.")

        if "epp" in p or "epistemic proportionality" in p:
            return ("EPP: act only if (Reason ∧ Proportion ∧ (Consent ∨ Necessity)). "
                    "Otherwise, withhold or reframe the action.")

        # Default proportional reply
        return ("I will answer within proportional justification: provide reasons, "
                "state your premises, and I will integrate them into understanding per EPP.")

    def _format(self, trace: str, body: str) -> str:
        if self.cfg.show_trace:
            return f"{trace}\n\n{body}"
        return body


# ======== Demo ========
if __name__ == "__main__":
    agent = IsFrameworkAgent()
    print("IsFrameworkReasoner (no external API). Type 'exit' to quit.\n")
    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user.lower() in {"exit", "quit"}:
            break
        reply = agent.respond(user)
        print(f"\nAgent:\n{reply}\n")
