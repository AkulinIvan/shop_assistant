import re
from app.config import load_config
from app.db import session_scope
from app.repository import Repository
from app.guardrails import Guardrails
from app.matcher import Matcher


class AssistantService:
    def __init__(self, cfg=None):
        self.cfg = cfg or load_config()

    def ask(self, question: str) -> dict:
        with session_scope() as s:
            repo = Repository(s)
            guard = Guardrails(repo)
            matcher = Matcher(repo)

            # 1) guardrails
            hit = guard.check(question)
            if hit:
                code, ans = hit
                repo.log(question, ans, f"guardrail:{code}", None)
                return {"answer": ans, "source": f"guardrail:{code}", "intent": None}
            
            unknown = [re.compile(p, re.IGNORECASE) for p in repo.unknown_topics()]
            if any(rx.search(question) for rx in unknown):
                ans = self.cfg.fallback
                repo.log(question, ans, "unknown_topic", None)
                return {"answer": ans, "source": "unknown_topic", "intent": None}
            
            # интент
            intent = matcher.match_intent(question)
            if intent is None:
                ans = self.cfg.fallback
                repo.log(question, ans, "unknown", None)
                return {"answer": ans, "source": "unknown", "intent": None}

            # 3) спец-логика поверх фактов (числа, подкоды)
            fact, variables = self._choose_fact(matcher, intent, question)
            if fact is None:
                ans = self.cfg.fallback
                repo.log(question, ans, f"missing_fact:{intent.code}", intent.code)
                return {"answer": ans, "source": f"missing_fact:{intent.code}",
                        "intent": intent.code}

            # 4) подстановка переменных + вычисляемые
            variables.update(self._computed_vars(intent.code, question))
            try:
                text = fact.template.format(**variables)
            except KeyError:
                text = self.cfg.fallback

            repo.log(question, text, f"fact:{intent.code}/{fact.code}", intent.code)
            return {"answer": text, "source": f"fact:{intent.code}/{fact.code}",
                    "intent": intent.code}

    # ---- выбор спец-факта ----
    def _choose_fact(self, matcher: Matcher, intent, question: str):
        q = question.lower()
        repo_facts = matcher.repo.facts_for_intent(intent.id)
        by_code = {f.code: f for f in repo_facts}

        # returns: overdue / opened / general
        if intent.code == "returns":
            m = re.search(r"(\d+)\s*-?\s*(й|день|дня|дней)", q)
            if m and "days" in {v.name for f in repo_facts for v in f.variables}:
                day = int(m.group(1))
                days_val = None
                for f in repo_facts:
                    for v in f.variables:
                        if v.name == "days":
                            days_val = int(re.sub(r"\D", "", v.value) or 0)
                if days_val is not None and day > days_val and "overdue" in by_code:
                    return by_code["overdue"], matcher._vars(by_code["overdue"])
            if any(w in q for w in ["вскрыт", "открыт", "упаковк"]) and "opened" in by_code:
                return by_code["opened"], matcher._vars(by_code["opened"])

        # defect внутри returns
        if "брак" in q and "defect" in {i.code for i in matcher.intents}:
            pass  # будет обработано матчером отдельно

        # general / самый приоритетный
        if "general" in by_code:
            return by_code["general"], matcher._vars(by_code["general"])
        best = max(repo_facts, key=lambda f: f.priority, default=None)
        return (best, matcher._vars(best)) if best else (None, {})

    # ---- вычисляемые переменные ----
    @staticmethod
    def _computed_vars(intent_code: str, question: str) -> dict[str, str]:
        out: dict[str, str] = {}
        if intent_code == "returns":
            m = re.search(r"(\d+)\s*-?\s*(й|день|дня|дней)", question.lower())
            if m:
                out["day"] = m.group(1)
        return out