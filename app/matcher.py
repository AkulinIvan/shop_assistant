import re
from app.models import Intent, Fact
from app.repository import Repository


class Matcher:
    def __init__(self, repo: Repository):
        self.repo = repo
        self.intents: list[Intent] = repo.all_intents()
        # предкомпилируем ключевые слова из БД
        self._compiled = []
        for it in self.intents:
            kws = [(re.compile(k.pattern, re.IGNORECASE), k.weight) for k in it.keywords]
            self._compiled.append((it, kws))

    def match_intent(self, text: str):
        best = None  # (score_key, intent)
        for intent, kws in self._compiled:
            hits = sum(1 for rx, _ in kws if rx.search(text))
            if hits == 0:
                continue
            # сначала по priority интента, потом по числу совпавших ключей
            key = (intent.priority, hits)
            if best is None or key > best[0]:
                best = (key, intent)
        return best[1] if best else None

    def select_fact(self, intent: Intent, text: str) -> tuple[Fact, dict[str, str]]:
        """
        Берём факт с наибольшим priority, чей код релевантен вопросу.
        Спец-факты (opened/overdue) требуют доп. условий, которые передаёт service.
        """
        facts = self.repo.facts_for_intent(intent.id)
        # базовый факт — general
        general = next((f for f in facts if f.code == "general"), facts[0])
        return general, self._vars(general)

    @staticmethod
    def _vars(fact: Fact) -> dict[str, str]:
        return {v.name: v.value for v in fact.variables}