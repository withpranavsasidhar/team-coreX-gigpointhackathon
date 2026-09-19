"""Test fixtures.

Every test runs against a real SQLite database with the real schema, the real
services and the real event engine. Only the language model is stubbed — the
thing that cannot be called deterministically — so what is under test is the
orchestration, validation and safety logic, not a mock of the business.
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Point at a scratch database before app modules read settings.
os.environ["DATABASE_URL"] = "sqlite:///./test_aria.db"
os.environ.setdefault("AI_API_KEY", "")
os.environ.setdefault("AI_MODEL", "")

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.database import Base  # noqa: E402
from app.models import Business, Customer, Product, Supplier  # noqa: E402
from app.providers.ai.base import AIExtractionProvider, ChatTurn, ToolCall  # noqa: E402
from app.services.event_engine import record_event  # noqa: E402
from app.models import EventType  # noqa: E402


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def business(db):
    row = Business(business_name="Test Kirana", business_type="kirana", default_language="en")
    db.add(row)
    db.flush()
    return row


@pytest.fixture()
def catalogue(db, business):
    """A small, realistic catalogue with stock recorded through the real engine."""
    products = {}
    for name, unit, qty, minimum, price in [
        ("Rice", "bags", 40, 15, 1450),
        ("Cooking Oil", "litres", 30, 20, 145),
        ("Coke", "pieces", 120, 60, 40),
        ("Biscuits", "pieces", 200, 150, 10),
    ]:
        product = Product(
            business_id=business.id, name=name, base_unit=unit,
            minimum_quantity=minimum, reorder_quantity=minimum * 3, price=price,
            current_quantity=0,
        )
        db.add(product)
        db.flush()
        record_event(
            db, business_id=business.id, product=product, event_type=EventType.STOCK_IN,
            quantity=qty, unit=unit, source="opening", commit=False,
        )
        products[name] = product
    db.commit()
    return products


@pytest.fixture()
def customer(db, business):
    row = Customer(business_id=business.id, name="Ramesh", outstanding_credit=1000)
    db.add(row)
    db.commit()
    return row


@pytest.fixture()
def supplier(db, business):
    row = Supplier(business_id=business.id, name="Kumar", supplies="staples")
    db.add(row)
    db.commit()
    return row


class StubProvider(AIExtractionProvider):
    """A scripted model.

    Returns a queued sequence of turns so the agent loop, the tool plumbing and
    the confirmation gate can be tested deterministically. It stands in for the
    model only — every tool it triggers runs the real service against the real
    database.
    """

    name = "stub"

    def __init__(self, turns=None, fail=False):
        self.turns = list(turns or [])
        self.fail = fail
        self.seen_messages = []

    @property
    def is_llm(self):
        return True

    @property
    def supports_tools(self):
        return True

    def chat(self, messages, tools=None, temperature=0.2):
        from app.providers.ai.base import AIProviderError

        self.seen_messages.append(messages)
        if self.fail:
            raise AIProviderError("stubbed transport failure")
        if not self.turns:
            return ChatTurn(content="Done.")
        return self.turns.pop(0)

    def extract_event(self, text, known_products):
        raise NotImplementedError

    def answer_question(self, question, facts, language="en"):
        return ""


def turn_calling(name, arguments, content=""):
    return ChatTurn(content=content, tool_calls=[ToolCall(id=f"call_{name}", name=name,
                                                          arguments=arguments)])


@pytest.fixture()
def stub_provider(monkeypatch):
    """Install a scripted model in place of the real provider."""
    def install(turns=None, fail=False):
        provider = StubProvider(turns=turns, fail=fail)
        monkeypatch.setattr("app.services.aria_agent.get_ai_provider", lambda: provider)
        return provider

    return install
