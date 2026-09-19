"""End-to-end through the real provider HTTP path.

These run the genuine `OpenAICompatibleProvider` against a local
OpenAI-compatible server, so the request building, auth header, JSON decoding
and tool-call parsing are all real, and everything behind them — agent loop,
tool validation, business services, event engine, database — is real too.

The one thing standing in for production is the model's own judgement. A hosted
model's choice of tool is not something these can prove; that needs a real key.
"""
import json

import pytest

from app.models import EventType, InventoryEvent
from tests import fake_openai_server as fake
from tests.fake_openai_server import text_message, tool_call_message


@pytest.fixture()
def live_provider(monkeypatch):
    """Point the real provider at a local server and hand back the agent module."""
    server = fake.start(port=8771)
    fake.SCRIPT.clear()
    fake.SEEN_REQUESTS.clear()

    from app.config import settings
    monkeypatch.setattr(settings, "ai_api_key", "test-key-123")
    monkeypatch.setattr(settings, "ai_base_url", "http://127.0.0.1:8771")
    monkeypatch.setattr(settings, "ai_model", "test/model")

    from app.providers.ai.openai_compatible import OpenAICompatibleProvider
    provider = OpenAICompatibleProvider()
    monkeypatch.setattr("app.services.aria_agent.get_ai_provider", lambda: provider)

    yield provider
    server.shutdown()


def test_real_http_round_trip_records_stock(db, business, catalogue, live_provider):
    """The headline flow, over a real socket, into the real ledger."""
    fake.SCRIPT.extend([
        tool_call_message("add_stock", {"product": "Coke", "quantity": 2, "unit": "cartons"}),
        text_message("Done. 2 cartons of Coke have been added."),
    ])

    from app.services import aria_agent
    result = aria_agent.chat(db, business, "Rendu cartons Coke vachayi", source="voice")

    # Language was detected from the real utterance.
    assert "te" in result.language

    # The tool ran and the database moved.
    assert result.status == "completed"
    assert result.tool_calls[0]["tool"] == "add_stock"
    db.refresh(catalogue["Coke"])
    assert float(catalogue["Coke"].current_quantity) == 122  # 120 + 2 (no carton rule yet)

    # A real ledger event exists, attributed to the assistant.
    event = (db.query(InventoryEvent)
             .filter_by(product_id=catalogue["Coke"].id)
             .order_by(InventoryEvent.created_at.desc()).first())
    assert event.event_type == EventType.STOCK_IN
    assert event.source == "aria"
    assert event.original_text == "Rendu cartons Coke vachayi"


def test_the_request_we_actually_send_is_well_formed(db, business, catalogue, live_provider):
    fake.SCRIPT.append(text_message("Hello."))
    from app.services import aria_agent
    aria_agent.chat(db, business, "hello")

    sent = fake.SEEN_REQUESTS[0]
    assert sent["authorization"] == "Bearer test-key-123"
    assert sent["model"] == "test/model"
    # Tools are advertised in OpenAI function shape.
    assert sent["tools"], "tools must be offered to the model"
    assert sent["tools"][0]["type"] == "function"
    assert "name" in sent["tools"][0]["function"]
    # The system prompt carries this business's real context.
    system = sent["messages"][0]["content"]
    assert business.business_name in system


def test_pack_size_taught_then_used_over_http(db, business, catalogue, live_provider):
    """'One carton has 24 bottles' must change later arithmetic, not just be stored."""
    from app.services import aria_agent

    fake.SCRIPT.extend([
        tool_call_message("set_unit_conversion",
                          {"product": "Coke", "unit": "cartons", "equals_base_units": 24}),
        text_message("Noted: one carton of Coke is 24 pieces."),
    ])
    aria_agent.chat(db, business, "One Coke carton has 24 bottles")

    before = float(catalogue["Coke"].current_quantity)

    fake.SCRIPT.extend([
        tool_call_message("add_stock", {"product": "Coke", "quantity": 2, "unit": "cartons"}),
        text_message("Added 2 cartons."),
    ])
    aria_agent.chat(db, business, "Two cartons of Coke came in")

    db.refresh(catalogue["Coke"])
    assert float(catalogue["Coke"].current_quantity) == before + 48


def test_reading_stock_reports_the_database_figure(db, business, catalogue, live_provider):
    from app.services import aria_agent
    fake.SCRIPT.extend([
        tool_call_message("get_product", {"product": "Rice"}),
        text_message("You have 40 bags of Rice."),
    ])
    result = aria_agent.chat(db, business, "Rice stock entha undi?")

    tool_result = result.tool_calls[0]["result"]
    assert tool_result["current_quantity"] == float(catalogue["Rice"].current_quantity)
    # The figure handed to the model is the database's, not the model's.
    tool_message = next(m for m in fake.SEEN_REQUESTS[-1]["messages"] if m.get("role") == "tool")
    assert json.loads(tool_message["content"])["current_quantity"] == 40


def test_expense_over_http_waits_for_confirmation(db, business, live_provider):
    from app.services import aria_agent
    from app.models import Expense

    fake.SCRIPT.append(
        tool_call_message("record_expense", {"amount": 2000, "category": "transport"})
    )
    result = aria_agent.chat(db, business, "I spent 2000 rupees on transport today")

    assert result.requires_confirmation is True
    assert "2,000" in result.pending_action["summary"]
    assert db.query(Expense).count() == 0, "must not write before confirmation"

    from uuid import UUID
    confirmed = aria_agent.confirm(db, business, UUID(result.pending_action["id"]), True)
    assert confirmed.status == "completed"
    assert db.query(Expense).count() == 1


def test_supplier_creation_over_http(db, business, live_provider):
    from app.services import aria_agent
    from app.models import Supplier

    fake.SCRIPT.append(tool_call_message("create_supplier", {"name": "Kumar"}))
    result = aria_agent.chat(db, business, "Add Kumar as my supplier")
    assert result.requires_confirmation is True

    from uuid import UUID
    aria_agent.confirm(db, business, UUID(result.pending_action["id"]), True)
    assert db.query(Supplier).filter_by(name="Kumar").count() == 1


def test_product_creation_over_http(db, business, live_provider):
    from app.services import aria_agent
    from app.models import Product

    fake.SCRIPT.append(
        tool_call_message("create_product",
                          {"name": "Sunrise Oil", "base_unit": "litres", "price": 145})
    )
    result = aria_agent.chat(db, business, "Create a product called Sunrise Oil")
    assert result.requires_confirmation is True

    from uuid import UUID
    confirmed = aria_agent.confirm(db, business, UUID(result.pending_action["id"]), True)
    assert confirmed.status == "completed"
    assert db.query(Product).filter_by(name="Sunrise Oil").count() == 1


def test_http_error_is_reported_not_papered_over(db, business, monkeypatch):
    """A 500 from the vendor must reach the owner as a failure."""
    from app.config import settings
    monkeypatch.setattr(settings, "ai_api_key", "test-key")
    monkeypatch.setattr(settings, "ai_base_url", "http://127.0.0.1:9")  # nothing listening
    monkeypatch.setattr(settings, "ai_model", "test/model")

    from app.providers.ai.openai_compatible import OpenAICompatibleProvider
    provider = OpenAICompatibleProvider()
    monkeypatch.setattr("app.services.aria_agent.get_ai_provider", lambda: provider)

    from app.services import aria_agent
    result = aria_agent.chat(db, business, "How much rice?")

    assert result.status == "error"
    assert "temporarily unavailable" in result.response
    assert "Nothing was changed" in result.response
