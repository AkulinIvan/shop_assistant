from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Intent, Fact, GuardrailRule, AuditLog, UnknownTopic


class Repository:
    def __init__(self, session: Session):
        self.s = session

    # ---- intents ----
    def all_intents(self) -> list[Intent]:
        return list(self.s.scalars(select(Intent)))

    # ---- facts ----
    def facts_for_intent(self, intent_id: int) -> list[Fact]:
        q = (select(Fact)
             .where(Fact.intent_id == intent_id)
             .order_by(Fact.priority.desc()))
        return list(self.s.scalars(q))

    # ---- guardrails ----
    def enabled_guardrails(self) -> list[GuardrailRule]:
        return list(self.s.scalars(
            select(GuardrailRule).where(GuardrailRule.enabled.is_(True))))

    # ---- audit ----
    def log(self, question: str, answer: str, source: str, intent: str | None) -> None:
        self.s.add(AuditLog(question=question, answer=answer,
                            source=source, intent=intent))
        
    def unknown_topics(self) -> list[str]:
        return [r.pattern for r in self.s.scalars(select(UnknownTopic))]