"""The A.R.I.A. agent: the intelligence layer above the business engine.

The model reasons and chooses tools. It does not calculate stock, decide
balances, or write to the database. Every figure it reports came out of a tool
result, and every tool result came out of a service that was already tested.

Two rules shape everything here:

  * A financial or destructive action is never executed because the model asked
    for it. It is proposed, stored, and run only after an explicit confirmation.
  * A failure is reported as a failure. If the model is unreachable, or a tool
    refuses, the owner is told — never given a plausible sentence instead.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import (
    Business, Conversation, ConversationMessage, PendingAction,
)
from app.providers.ai import AIProviderError, get_ai_provider
from app.services import business_context, conversation as conversation_memory, tools
from app.services.language import detect_language

MAX_HISTORY_MESSAGES = 24


SYSTEM_PROMPT = """You are A.R.I.A. (Adaptive Retail Intelligence Assistant), \
the business assistant for a small shop owner in India.

HOW YOU WORK
- You never know anything about this business except what tools tell you.
- Never state a stock level, balance, price, or total that did not come from a \
tool result in this conversation. If you have not looked it up, look it up.
- If a tool returns an error, tell the owner plainly what went wrong. Never \
claim something was recorded when it was not.
- If a product or customer name is ambiguous, ask which one. Do not pick.

LANGUAGE
- The owner may speak English, Telugu, Hindi, or mix them ("Rendu cartons Coke \
vachayi" = two cartons of Coke arrived). Understand the meaning directly.
- Reply in the language the owner used, unless they have set a preference.
- Use the trade's own words and units.

ACTIONS
- To change the business, call a tool. Do not describe what you would do.
- Some tools need confirmation first; the system handles that. Propose the \
action by calling the tool, and the owner will be asked.
- Keep replies short and concrete, the way a person behind a counter talks. \
State the resulting figure when a tool returns one.

Today is {today}."""


@dataclass
class AgentResult:
    response: str
    conversation_id: UUID
    language: str = "en"
    tool_calls: list[dict] = field(default_factory=list)
    requires_confirmation: bool = False
    pending_action: dict | None = None
    status: str = "completed"     # completed | needs_confirmation | error | unavailable
    error: str | None = None
    provider: str = ""
    model: str = ""


# --- conversation persistence -------------------------------------------

def get_or_create_conversation(
    db: Session, business: Business, conversation_id: UUID | None
) -> Conversation:
    if conversation_id:
        found = db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.business_id == business.id,   # never cross businesses
            )
        ).scalar_one_or_none()
        if found:
            return found

    conversation = Conversation(business_id=business.id)
    db.add(conversation)
    db.flush()
    return conversation


def _append(db: Session, conversation: Conversation, role: str, content: str = "",
            tool_calls: str = "", tool_call_id: str = "", tool_name: str = "",
            language: str = "") -> ConversationMessage:
    message = ConversationMessage(
        conversation_id=conversation.id, role=role, content=content or "",
        tool_calls=tool_calls or "", tool_call_id=tool_call_id or "",
        tool_name=tool_name or "", detected_language=language or "",
    )
    db.add(message)
    conversation.updated_at = datetime.utcnow()
    db.flush()
    return message


def _history(db: Session, conversation: Conversation) -> list[dict]:
    """Rebuild the model-facing history from what was actually stored."""
    rows = db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation.id)
        .order_by(ConversationMessage.created_at)
    ).scalars().all()

    messages: list[dict] = []
    for row in rows[-MAX_HISTORY_MESSAGES:]:
        if row.role == "tool":
            messages.append({
                "role": "tool", "tool_call_id": row.tool_call_id,
                "name": row.tool_name, "content": row.content,
            })
        elif row.role == "assistant" and row.tool_calls:
            try:
                calls = json.loads(row.tool_calls)
            except json.JSONDecodeError:
                calls = []
            entry: dict = {"role": "assistant", "content": row.content or None}
            if calls:
                entry["tool_calls"] = calls
            messages.append(entry)
        else:
            messages.append({"role": row.role, "content": row.content})
    return messages


def _system_message(business: Business) -> dict:
    kind = business_context.get_type(business.business_type)
    context = (
        f"\n\nTHIS BUSINESS\n- Name: {business.business_name}"
        f"\n- Trade: {kind.label}"
        f"\n- Natural units: {', '.join(kind.units)}"
        f"\n- Preferred reply language: {business.default_language}"
    )
    return {
        "role": "system",
        "content": SYSTEM_PROMPT.format(today=datetime.utcnow().strftime("%d %B %Y")) + context,
    }


def _summarise(tool_name: str, arguments: dict) -> str:
    """A plain sentence describing what is about to happen, for the owner to approve."""
    a = arguments
    money = lambda v: f"₹{float(v):,.0f}"  # noqa: E731
    try:
        if tool_name == "record_payment":
            return f"Record a {money(a.get('amount'))} payment from {a.get('customer')}?"
        if tool_name == "record_expense":
            category = a.get("category") or "general"
            return f"Record a {money(a.get('amount'))} {category} expense?"
        if tool_name == "make_credit_sale":
            return (f"Record {a.get('quantity')} {a.get('unit') or ''} of {a.get('product')} "
                    f"on credit to {a.get('customer')}?").replace("  ", " ")
        if tool_name == "delete_product":
            return f"Archive {a.get('product')}? Its history stays, but it leaves your active list."
        if tool_name == "adjust_stock":
            return (f"Correct {a.get('product')} to a counted "
                    f"{a.get('counted_quantity')} {a.get('unit') or ''}?").replace("  ", " ")
        if tool_name == "create_product":
            return f"Create a new product called {a.get('name')} counted in {a.get('base_unit')}?"
        if tool_name == "update_product":
            changes = ", ".join(f"{k} to {v}" for k, v in a.items() if k != "product")
            return f"Update {a.get('product')} — {changes}?"
        if tool_name == "create_supplier":
            return f"Add {a.get('name')} as a supplier?"
    except (TypeError, ValueError):
        pass
    return f"Run {tool_name.replace('_', ' ')}?"


def _propose(db: Session, business: Business, conversation: Conversation,
             tool_name: str, arguments: dict) -> PendingAction:
    action = PendingAction(
        business_id=business.id, conversation_id=conversation.id,
        tool_name=tool_name, arguments=json.dumps(arguments, default=str),
        summary=_summarise(tool_name, arguments),
    )
    db.add(action)
    db.flush()
    return action


# --- the agent loop -------------------------------------------------------

def chat(
    db: Session,
    business: Business,
    message: str,
    conversation_id: UUID | None = None,
    language: str | None = None,
    source: str = "text",
) -> AgentResult:
    text = (message or "").strip()
    provider = get_ai_provider()
    detected = detect_language(text) if text else "en"
    conversation = get_or_create_conversation(db, business, conversation_id)

    if not text:
        return AgentResult(response="I didn't catch that. What would you like to do?",
                           conversation_id=conversation.id, language=detected, status="error",
                           error="empty_message")

    # Honest unavailability. The caller falls back to the deterministic engine
    # rather than this pretending to be an agent.
    if not provider.supports_tools:
        db.commit()
        return AgentResult(
            response="AI is not configured yet, so I can't hold a full conversation.",
            conversation_id=conversation.id, language=detected,
            status="unavailable",
            error="AI is not configured. Set AI_API_KEY and AI_MODEL to enable the A.R.I.A. agent.",
            provider=provider.name,
        )

    _append(db, conversation, "user", text, language=detected)

    ctx = tools.ToolContext(db=db, business=business, source="aria")
    schemas = tools.tool_schemas()
    messages = [_system_message(business)] + _history(db, conversation)
    if language:
        messages.append({"role": "system", "content": f"Reply in language code: {language}."})

    executed: list[dict] = []

    for _round in range(settings.agent_max_tool_rounds):
        try:
            turn = provider.chat(messages, tools=schemas)
        except AIProviderError as exc:
            db.commit()
            return AgentResult(
                response="A.R.I.A. is temporarily unavailable. Nothing was changed.",
                conversation_id=conversation.id, language=detected,
                status="error", error=str(exc), provider=provider.name,
                model=settings.ai_model, tool_calls=executed,
            )

        if not turn.tool_calls:
            reply = turn.content or "Done."
            _append(db, conversation, "assistant", reply, language=detected)
            conversation_memory.log_interaction(
                db, business_id=business.id, kind="agent", transcript=text,
                detected_language=detected, intent="agent_reply", status="completed",
                confidence=1.0, provider=provider.name, response_text=reply,
                source=source, commit=False,
            )
            db.commit()
            return AgentResult(response=reply, conversation_id=conversation.id,
                               language=detected, tool_calls=executed,
                               provider=provider.name, model=settings.ai_model)

        # Record the assistant's tool request verbatim so the history stays valid.
        raw_calls = [
            {"id": c.id, "type": "function",
             "function": {"name": c.name, "arguments": json.dumps(c.arguments)}}
            for c in turn.tool_calls
        ]
        _append(db, conversation, "assistant", turn.content,
                tool_calls=json.dumps(raw_calls), language=detected)
        messages.append({"role": "assistant", "content": turn.content or None,
                         "tool_calls": raw_calls})

        for call in turn.tool_calls:
            definition = tools.REGISTRY.get(call.name)

            # The confirmation gate. A write that touches money or destroys data
            # stops here, before any service is called.
            if definition and definition.needs_confirmation:
                action = _propose(db, business, conversation, call.name, call.arguments)
                prompt = turn.content or action.summary
                _append(db, conversation, "assistant", prompt, language=detected)
                conversation_memory.log_interaction(
                    db, business_id=business.id, kind="agent", transcript=text,
                    detected_language=detected, intent=call.name,
                    status="needs_confirmation", confidence=1.0, provider=provider.name,
                    response_text=action.summary, source=source, commit=False,
                )
                db.commit()
                return AgentResult(
                    response=prompt, conversation_id=conversation.id, language=detected,
                    tool_calls=executed, requires_confirmation=True,
                    status="needs_confirmation", provider=provider.name,
                    model=settings.ai_model,
                    pending_action={
                        "id": str(action.id), "tool": call.name,
                        "summary": action.summary, "arguments": call.arguments,
                    },
                )

            result = tools.execute(ctx, call.name, {**call.arguments, "__utterance__": text})
            executed.append({"tool": call.name, "arguments": call.arguments, "result": result})
            payload = json.dumps(result, default=str)
            _append(db, conversation, "tool", payload,
                    tool_call_id=call.id, tool_name=call.name)
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "name": call.name, "content": payload})

    # Ran out of rounds: say so rather than inventing a conclusion.
    fallback = ("I couldn't finish that in a reasonable number of steps. "
                "Could you break it into smaller requests?")
    _append(db, conversation, "assistant", fallback, language=detected)
    db.commit()
    return AgentResult(response=fallback, conversation_id=conversation.id, language=detected,
                       tool_calls=executed, status="error", error="max_tool_rounds_exceeded",
                       provider=provider.name, model=settings.ai_model)


def confirm(db: Session, business: Business, action_id: UUID, approved: bool,
            source: str = "text") -> AgentResult:
    """Run — or discard — an action the owner was asked about."""
    action = db.execute(
        select(PendingAction).where(
            PendingAction.id == action_id,
            PendingAction.business_id == business.id,   # never another business's action
        )
    ).scalar_one_or_none()

    if not action:
        return AgentResult(response="I couldn't find that pending action.",
                           conversation_id=UUID(int=0), status="error",
                           error="unknown_pending_action")

    conversation = db.get(Conversation, action.conversation_id) if action.conversation_id else None
    conversation_id = conversation.id if conversation else UUID(int=0)

    if action.status != "pending":
        return AgentResult(
            response=f"That action was already {action.status}.",
            conversation_id=conversation_id, status="error", error="already_resolved",
        )

    if not approved:
        action.status = "cancelled"
        action.resolved_at = datetime.utcnow()
        if conversation:
            _append(db, conversation, "assistant", "Cancelled. Nothing was changed.")
        db.commit()
        return AgentResult(response="Cancelled. Nothing was changed.",
                           conversation_id=conversation_id, status="completed")

    ctx = tools.ToolContext(db=db, business=business, source="aria")
    arguments = json.loads(action.arguments)
    result = tools.execute(ctx, action.tool_name, arguments)

    failed = isinstance(result, dict) and result.get("error")
    action.status = "confirmed" if not failed else "pending"
    action.resolved_at = datetime.utcnow() if not failed else None

    reply = _describe_result(action.tool_name, result)
    if conversation:
        _append(db, conversation, "tool", json.dumps(result, default=str),
                tool_call_id=str(action.id), tool_name=action.tool_name)
        _append(db, conversation, "assistant", reply)

    conversation_memory.log_interaction(
        db, business_id=business.id, kind="agent", transcript=action.summary,
        intent=action.tool_name, status="failed" if failed else "recorded",
        confidence=1.0, response_text=reply, source=source, commit=False,
    )
    db.commit()

    return AgentResult(
        response=reply, conversation_id=conversation_id,
        tool_calls=[{"tool": action.tool_name, "arguments": arguments, "result": result}],
        status="error" if failed else "completed",
        error=result.get("error") if failed else None,
    )


def _describe_result(tool_name: str, result: dict) -> str:
    """Plain confirmation wording, generated from the real tool result."""
    if result.get("error"):
        return f"That didn't work: {result['error']} Nothing was changed."

    if result.get("recorded") and result.get("resulting_quantity") is not None:
        return (f"Done. {result['product']} is now "
                f"{result['resulting_quantity']:g} {result['resulting_unit']}.")
    if tool_name == "record_payment":
        return (f"Recorded ₹{result['amount']:,.0f} from {result['customer']}. "
                f"They now owe ₹{result['remaining_balance']:,.0f}.")
    if tool_name == "record_expense":
        return f"Recorded a ₹{result['amount']:,.0f} {result['category']} expense."
    if tool_name == "create_product":
        return f"Created {result['name']}, counted in {result['base_unit']}."
    if tool_name == "update_product":
        return f"Updated {result['after']['name']}."
    if tool_name == "create_supplier":
        return (f"Added {result['name']} as a supplier."
                if result.get("created") else result.get("message", "Already a supplier."))
    if tool_name == "delete_product":
        return f"Archived {result['product']}. Its history is still there."
    return "Done."
