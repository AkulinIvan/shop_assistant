from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime, Text


class Base(DeclarativeBase):
    pass


class Intent(Base):
    """Тема вопроса: delivery, returns, product, defect, discounts, ..."""
    __tablename__ = "intents"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))

    keywords: Mapped[list["Keyword"]] = relationship(back_populates="intent",
                                                     cascade="all, delete-orphan")
    facts: Mapped[list["Fact"]] = relationship(back_populates="intent",
                                               cascade="all, delete-orphan")
    priority: Mapped[int] = mapped_column(Integer, default=0)


class Keyword(Base):
    """Синоним/триггер для интента (регулярка или подстрока)"""
    __tablename__ = "keywords"
    id: Mapped[int] = mapped_column(primary_key=True)
    intent_id: Mapped[int] = mapped_column(ForeignKey("intents.id", ondelete="CASCADE"))
    pattern: Mapped[str] = mapped_column(String(255))   # regex
    weight: Mapped[int] = mapped_column(Integer, default=1)

    intent: Mapped[Intent] = relationship(back_populates="keywords")


class Fact(Base):
    """Конкретный факт регламента. template — строка с {placeholders}."""
    __tablename__ = "facts"
    id: Mapped[int] = mapped_column(primary_key=True)
    intent_id: Mapped[int] = mapped_column(ForeignKey("intents.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(64), index=True)  # general, opened, overdue...
    template: Mapped[str] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(Integer, default=0)  # больше = выше

    intent: Mapped[Intent] = relationship(back_populates="facts")
    variables: Mapped[list["FactVariable"]] = relationship(
        back_populates="fact", cascade="all, delete-orphan")


class FactVariable(Base):
    """Значение переменной для подстановки в template."""
    __tablename__ = "fact_variables"
    id: Mapped[int] = mapped_column(primary_key=True)
    fact_id: Mapped[int] = mapped_column(ForeignKey("facts.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(64))
    value: Mapped[str] = mapped_column(String(255))

    fact: Mapped[Fact] = relationship(back_populates="variables")


class GuardrailRule(Base):
    """Правило защиты: regex + фиксированный ответ."""
    __tablename__ = "guardrail_rules"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    pattern: Mapped[str] = mapped_column(String(512))
    answer: Mapped[str] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(128))
    intent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    
    
class UnknownTopic(Base):
    __tablename__ = "unknown_topics"
    id: Mapped[int] = mapped_column(primary_key=True)
    pattern: Mapped[str] = mapped_column(String(255), unique=True)