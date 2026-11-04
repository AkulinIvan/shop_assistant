"""
Идемпотентная загрузка данных регламента и guardrails в БД.
Всё берётся из seed/*.json.
"""
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db import session_scope                       # noqa: E402
from app.models import (Intent, Keyword, Fact,          # noqa: E402
                        FactVariable, GuardrailRule,
                        UnknownTopic)

SEED_DIR = PROJECT_ROOT / "seed"


def load_json(name: str):
    with open(SEED_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_knowledge(s) -> None:
    data = load_json("knowledge.json")
    for it in data["intents"]:
        intent = s.query(Intent).filter_by(code=it["code"]).one_or_none()
        if not intent:
            intent = Intent(code=it["code"], title=it["title"],
                            priority=it.get("priority", 0))
            s.add(intent)
            s.flush()
        else:
            intent.title = it["title"]
            intent.priority = it.get("priority", 0)     # ← теперь читается
        existing = {k.pattern for k in intent.keywords}
        for pattern in it["keywords"]:
            if pattern not in existing:
                s.add(Keyword(intent_id=intent.id, pattern=pattern, weight=1))
        for f in it["facts"]:
            fact = s.query(Fact).filter_by(intent_id=intent.id,
                                           code=f["code"]).one_or_none()
            if not fact:
                fact = Fact(intent_id=intent.id, code=f["code"],
                            template=f["template"],
                            priority=f.get("priority", 0))
                s.add(fact)
                s.flush()
            else:
                fact.template = f["template"]
                fact.priority = f.get("priority", 0)
                s.query(FactVariable).filter_by(fact_id=fact.id).delete()
            for name, value in f.get("variables", {}).items():
                s.add(FactVariable(fact_id=fact.id, name=name, value=str(value)))


def seed_guardrails(s) -> None:
    data = load_json("guardrails.json")
    for r in data["rules"]:
        rule = s.query(GuardrailRule).filter_by(code=r["code"]).one_or_none()
        if not rule:
            rule = GuardrailRule(code=r["code"], pattern=r["pattern"],
                                 answer=r["answer"], enabled=True)
            s.add(rule)
        else:
            rule.pattern = r["pattern"]
            rule.answer = r["answer"]
            rule.enabled = True


def seed_unknown_topics(s) -> None:                     # ← новая функция
    data = load_json("unknown_topics.json")
    existing = {r.pattern for r in s.query(UnknownTopic).all()}
    for pattern in data["patterns"]:
        if pattern not in existing:
            s.add(UnknownTopic(pattern=pattern))


def main() -> None:
    with session_scope() as s:
        seed_knowledge(s)
        seed_guardrails(s)
        seed_unknown_topics(s)                          
    print("Seed загружен.")


if __name__ == "__main__":
    main()