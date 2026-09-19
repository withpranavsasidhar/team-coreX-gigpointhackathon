"""The agent loop: tool orchestration, the confirmation gate, conversation
state, authorization scoping, and honest failure."""
import json

import pytest

from app.models import Business, Conversation, ConversationMessage, PendingAction
from app.providers.ai.base import ChatTurn
from app.services import aria_agent
from tests.conftest import turn_calling


# --- basic conversation ---------------------------------------------------

def test_plain_reply_is_returned_and_stored(db, business, stub_provider):
    stub_provider([ChatTurn(content="You have 40 bags of rice.")])
    result = aria_agent.chat(db, business, "How much rice?")

    assert result.status == "completed"
    assert result.response == "You have 40 bags of rice."
    roles = [m.role for m in db.query(ConversationMessage).all()]
    assert roles == ["user", "assistant"]


def test_conversation_is_continued_not_restarted(db, business, stub_provider):
    stub_provider([ChatTurn(content="First.")])
    first = aria_agent.chat(db, business, "Hello")

    stub = stub_provider([ChatTurn(content="Second.")])
    second = aria_agent.chat(db, business, "And again", conversation_id=first.conversation_id)

    assert second.conversation_id == first.conversation_id
    assert db.query(Conversation).count() == 1
    # The model was shown the earlier turns.
    contents = [m.get("content") for m in stub.seen_messages[0]]
    assert "Hello" in contents and "First." in contents


def test_empty_message_is_rejected(db, business, stub_provider):
    stub_provider([])
    result = aria_agent.chat(db, business, "   ")
    assert result.status == "error"


# --- tool orchestration ---------------------------------------------------

def test_tool_result_is_fed_back_to_the_model(db, business, catalogue, stub_provider):
    stub = stub_provider([
        turn_calling("get_product", {"product": "Rice"}),
        ChatTurn(content="You have 40 bags of Rice."),
    ])
    result = aria_agent.chat(db, business, "How much rice do I have?")

    assert result.status == "completed"
    assert result.tool_calls[0]["tool"] == "get_product"
    assert result.tool_calls[0]["result"]["current_quantity"] == 40
    # The second model call included the tool's output.
    second_call = stub.seen_messages[1]
    assert any(m.get("role") == "tool" for m in second_call)


def test_non_confirming_write_executes_immediately(db, business, catalogue, stub_provider):
    stub_provider([
        turn_calling("add_stock", {"product": "Rice", "quantity": 5}),
        ChatTurn(content="Added 5 bags."),
    ])
    result = aria_agent.chat(db, business, "5 bags of rice came in")

    assert result.status == "completed"
    db.refresh(catalogue["Rice"])
    assert float(catalogue["Rice"].current_quantity) == 45


def test_tool_error_is_surfaced_not_hidden(db, business, catalogue, stub_provider):
    stub_provider([
        turn_calling("add_stock", {"product": "Caviar", "quantity": 5}),
        ChatTurn(content="I couldn't find that product."),
    ])
    result = aria_agent.chat(db, business, "add 5 caviar")
    assert "error" in result.tool_calls[0]["result"]


def test_runaway_tool_loop_is_stopped_honestly(db, business, catalogue, stub_provider):
    stub_provider([turn_calling("get_inventory", {}) for _ in range(20)])
    result = aria_agent.chat(db, business, "loop forever")
    assert result.status == "error"
    assert result.error == "max_tool_rounds_exceeded"
    assert "couldn't finish" in result.response


# --- the confirmation gate ------------------------------------------------

@pytest.mark.parametrize("tool_name,args", [
    ("record_payment", {"customer": "Ramesh", "amount": 400}),
    ("record_expense", {"amount": 2000, "category": "transport"}),
    ("delete_product", {"product": "Rice"}),
])
def test_risky_actions_stop_for_confirmation(db, business, catalogue, customer,
                                             stub_provider, tool_name, args):
    stub_provider([turn_calling(tool_name, args)])
    result = aria_agent.chat(db, business, "do the risky thing")

    assert result.requires_confirmation is True
    assert result.status == "needs_confirmation"
    assert result.pending_action["tool"] == tool_name
    # Crucially: nothing ran.
    assert result.tool_calls == []
    assert db.query(PendingAction).filter_by(status="pending").count() == 1


def test_payment_only_moves_money_after_confirmation(db, business, customer, stub_provider):
    stub_provider([turn_calling("record_payment", {"customer": "Ramesh", "amount": 400})])
    proposal = aria_agent.chat(db, business, "Ramesh paid 400")

    db.refresh(customer)
    assert float(customer.outstanding_credit) == 1000, "balance must not move before confirming"

    from uuid import UUID
    confirmed = aria_agent.confirm(db, business, UUID(proposal.pending_action["id"]), True)

    db.refresh(customer)
    assert float(customer.outstanding_credit) == 600
    assert confirmed.status == "completed"
    assert "600" in confirmed.response


def test_cancelling_changes_nothing(db, business, customer, stub_provider):
    stub_provider([turn_calling("record_payment", {"customer": "Ramesh", "amount": 400})])
    proposal = aria_agent.chat(db, business, "Ramesh paid 400")

    from uuid import UUID
    result = aria_agent.confirm(db, business, UUID(proposal.pending_action["id"]), False)

    db.refresh(customer)
    assert float(customer.outstanding_credit) == 1000
    assert "Cancelled" in result.response
    assert db.query(PendingAction).one().status == "cancelled"


def test_an_action_cannot_be_confirmed_twice(db, business, customer, stub_provider):
    stub_provider([turn_calling("record_payment", {"customer": "Ramesh", "amount": 400})])
    proposal = aria_agent.chat(db, business, "Ramesh paid 400")

    from uuid import UUID
    action_id = UUID(proposal.pending_action["id"])
    aria_agent.confirm(db, business, action_id, True)
    again = aria_agent.confirm(db, business, action_id, True)

    assert again.status == "error"
    db.refresh(customer)
    assert float(customer.outstanding_credit) == 600, "must not be charged twice"


def test_confirmation_summary_states_the_real_amount(db, business, customer, stub_provider):
    stub_provider([turn_calling("record_payment", {"customer": "Ramesh", "amount": 450})])
    result = aria_agent.chat(db, business, "Ramesh paid 450")
    assert "450" in result.pending_action["summary"]
    assert "Ramesh" in result.pending_action["summary"]


def test_a_failed_confirmed_action_reports_failure(db, business, customer, stub_provider):
    """If the underlying service refuses, the reply must not claim success."""
    stub_provider([turn_calling("record_payment", {"customer": "Ramesh", "amount": 999999})])
    proposal = aria_agent.chat(db, business, "Ramesh paid a fortune")

    from uuid import UUID
    result = aria_agent.confirm(db, business, UUID(proposal.pending_action["id"]), True)

    assert result.status == "error"
    assert "Nothing was changed" in result.response
    db.refresh(customer)
    assert float(customer.outstanding_credit) == 1000


# --- authorization --------------------------------------------------------

def test_another_businesss_action_cannot_be_confirmed(db, business, customer, stub_provider):
    stub_provider([turn_calling("record_payment", {"customer": "Ramesh", "amount": 400})])
    proposal = aria_agent.chat(db, business, "Ramesh paid 400")

    intruder = Business(business_name="Someone Else", business_type="bakery")
    db.add(intruder)
    db.commit()

    from uuid import UUID
    result = aria_agent.confirm(db, intruder, UUID(proposal.pending_action["id"]), True)

    assert result.status == "error"
    db.refresh(customer)
    assert float(customer.outstanding_credit) == 1000


def test_another_businesss_conversation_is_not_continued(db, business, stub_provider):
    stub_provider([ChatTurn(content="Hi")])
    mine = aria_agent.chat(db, business, "Hello")

    intruder = Business(business_name="Someone Else", business_type="bakery")
    db.add(intruder)
    db.commit()

    stub_provider([ChatTurn(content="Hi")])
    theirs = aria_agent.chat(db, intruder, "Hello", conversation_id=mine.conversation_id)

    assert theirs.conversation_id != mine.conversation_id


# --- honest failure -------------------------------------------------------

def test_provider_failure_is_reported_as_unavailable(db, business, stub_provider):
    stub_provider([], fail=True)
    result = aria_agent.chat(db, business, "How much rice?")

    assert result.status == "error"
    assert "temporarily unavailable" in result.response
    assert "Nothing was changed" in result.response


def test_unconfigured_agent_says_so_rather_than_pretending(db, business, monkeypatch):
    from app.providers.ai.rule_based import RuleBasedExtractionProvider
    monkeypatch.setattr("app.services.aria_agent.get_ai_provider",
                        lambda: RuleBasedExtractionProvider())

    result = aria_agent.chat(db, business, "Add 5 bags of rice")

    assert result.status == "unavailable"
    assert "not configured" in result.response.lower()
    # And it must not have silently written anything.
    assert result.tool_calls == []


# --- the multi-turn correction the spec calls for -------------------------

def test_correction_across_turns(db, business, catalogue, stub_provider):
    """'Add 20' then 'actually make it 15' must land on 15, via a real adjustment."""
    stub_provider([
        turn_calling("add_stock", {"product": "Coke", "quantity": 20}),
        ChatTurn(content="Added 20."),
    ])
    first = aria_agent.chat(db, business, "Add 20 Coke")
    db.refresh(catalogue["Coke"])
    assert float(catalogue["Coke"].current_quantity) == 140

    stub_provider([
        turn_calling("adjust_stock", {"product": "Coke", "counted_quantity": 135}),
    ])
    second = aria_agent.chat(db, business, "Actually make it 15",
                             conversation_id=first.conversation_id)

    # adjust_stock is gated, so it is proposed rather than executed.
    assert second.requires_confirmation is True
    from uuid import UUID
    aria_agent.confirm(db, business, UUID(second.pending_action["id"]), True)

    db.refresh(catalogue["Coke"])
    assert float(catalogue["Coke"].current_quantity) == 135
