import re
from app.repository import Repository


class Guardrails:
    def __init__(self, repo: Repository):
        self.rules = [
            (r.code, re.compile(r.pattern, re.IGNORECASE), r.answer)
            for r in repo.enabled_guardrails()
        ]

    def check(self, text: str) -> tuple[str, str] | None:
        """Возвращает (code, answer), если сработало правило."""
        for code, rx, ans in self.rules:
            if rx.search(text):
                return code, ans
        return None