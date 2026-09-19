"""Natural-language business questions, answered from the ledger.

Flow: question -> intent detection -> database query -> verified facts ->
reasoning layer -> human-friendly response.

The reasoning layer never sees the question without the facts, and never
produces a figure of its own: every number in an answer is computed here in
Python/SQL first. When no language model is configured, the templated answer
below is used verbatim, so the feature works either way.
"""
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Business, Customer, EventType, InventoryEvent, Product
from app.providers.ai import get_ai_provider
from app.services import insights_service, inventory_service
from app.services.language import detect_language, primary_language
from app.services.product_matcher import match_product

# --- intents ---------------------------------------------------------------
STOCK_LEVEL = "stock_level"
LOW_STOCK = "low_stock"
REORDER = "reorder"
SOLD_PERIOD = "sold_period"
RECEIVED_PERIOD = "received_period"
EXPLAIN = "explain"
CUSTOMER_ACTIVITY = "customer_activity"
CREDIT_BOOK = "credit_book"
WHAT_CHANGED = "what_changed"
UNUSUAL = "unusual"
OVERVIEW = "overview"

INTENT_PATTERNS: list[tuple[str, list[str]]] = [
    # "Who owes me money" is about the credit book as a whole, so it must be
    # tested before the per-customer patterns below can claim the word "owes".
    (CREDIT_BOOK, [r"who owes", r"owes me", r"who has to pay", r"outstanding credit",
                   r"credit book", r"\bpending payments?\b", r"who.*not paid",
                   r"how much.*owed", r"ఎవరు.*బాకీ", r"कौन.*उधार"]),
    (EXPLAIN, [r"\bwhy\b", r"\bwhere did\b", r"\bwhere.*\bgo\b", r"\bwhat happened to\b",
               "ఎందుకు", "ఎక్కడ", "क्यों", "कहां", "कहाँ"]),
    (WHAT_CHANGED, [r"what changed", r"what happened (today|this week|yesterday)",
                    r"what.*activity", r"summar(y|ise|ize)", r"how did.*(go|do)",
                    r"ఏం జరిగింది", r"क्या हुआ"]),
    (LOW_STOCK, [r"running low", r"\blow stock\b", r"running out", r"needs attention",
                 r"what is low", r"what's low", r"almost finished", r"about to finish"]),
    (REORDER, [r"should i order", r"what to order", r"\breorder\b", r"need to order",
               r"what should i buy"]),
    (UNUSUAL, [r"unusual", r"strange", r"spike", r"selling fast", r"moving fast"]),
    (SOLD_PERIOD, [r"did i sell", r"did we sell", r"\bsold\b", r"\bsales\b"]),
    (RECEIVED_PERIOD, [r"came in", r"stock came", r"\breceived\b", r"\bpurchased\b",
                       r"did i buy", r"stock in"]),
    (CUSTOMER_ACTIVITY, [r"\btake\b", r"\btook\b", r"\bowes?\b", r"\bcredit\b"]),
    (STOCK_LEVEL, [r"how much", r"how many", r"stock of", r"\bleft\b", r"do i have",
                   r"ఎన్ని", r"कितना", r"कितने"]),
]

# window phrase -> (days back, label)
WINDOWS: list[tuple[str, int, str]] = [
    (r"\btoday\b|ఈరోజు|आज", 1, "today"),
    (r"\byesterday\b|నిన్న", 2, "yesterday"),
    (r"this week|last 7 days|past week|ఈ వారం|इस हफ्ते", 7, "this week"),
    (r"this month|last 30 days|past month|ఈ నెల|इस महीने", 30, "this month"),
]

OUTFLOW_PHRASES = {
    EventType.SALE: "{n:g} {verb} sold",
    EventType.CREDIT_SALE: "{n:g} {verb} sold on credit",
    EventType.DAMAGE: "{n:g} {verb} recorded as damaged",
    EventType.LOSS: "{n:g} {verb} recorded as lost",
    EventType.STOCK_OUT: "{n:g} {verb} taken out",
}
INFLOW_PHRASES = {
    EventType.PURCHASE: "{n:g} {verb} purchased",
    EventType.STOCK_IN: "{n:g} came in",
    EventType.RETURN: "{n:g} came back as returns",
}


def _join(items: list[str]) -> str:
    """Join a short list the way a person would say it, with a final 'and'."""
    if len(items) <= 1:
        return items[0] if items else ""
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def _verb(n: float) -> str:
    return "was" if abs(n) == 1 else "were"


@dataclass
class QueryAnswer:
    intent: str
    answer: str
    facts: dict
    items: list[dict] = field(default_factory=list)
    visual: str = "none"  # stock | list | breakdown | timeline | none
    product_id: UUID | None = None
    product_name: str | None = None
    window_label: str | None = None
    grounded_by: str = "template"


def detect_intent(question: str) -> str:
    lowered = question.lower()
    for intent, patterns in INTENT_PATTERNS:
        if any(re.search(p, lowered) for p in patterns):
            return intent
    return OVERVIEW


def detect_window(question: str, default_days: int = 7) -> tuple[datetime, datetime, str]:
    lowered = question.lower()
    now = datetime.utcnow()
    for pattern, days, label in WINDOWS:
        if re.search(pattern, lowered):
            if label == "today":
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                return start, now, "today"
            if label == "yesterday":
                start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                return start, start + timedelta(days=1), "yesterday"
            return now - timedelta(days=days), now, label
    label = {1: "today", 7: "this week", 30: "this month"}.get(
        default_days, f"in the last {default_days} days"
    )
    return now - timedelta(days=default_days), now, label


# Interrogatives and framing words that are never part of a product name.
QUESTION_WORDS = {
    "what", "happened", "happen", "how", "much", "many", "where", "why", "when",
    "did", "do", "does", "is", "are", "was", "were", "go", "gone", "going",
    "left", "stock", "have", "had", "me", "show", "tell", "about", "week",
    "month", "day", "days", "today", "yesterday", "should", "order", "need",
    "running", "low", "sell", "sold", "take", "took", "get", "got", "there",
}


def find_product(db: Session, business_id: UUID, question: str) -> Product | None:
    products = inventory_service.list_products(db, business_id)
    lowered = question.lower()

    # A catalogue name appearing verbatim is the strongest signal.
    best = max((p for p in products if p.name.lower() in lowered),
               key=lambda p: len(p.name), default=None)
    if best:
        return best

    from app.services.language import product_tokens

    asked = {t for t in product_tokens(question) if t not in QUESTION_WORDS}
    if not asked:
        return None

    # A product is meant if its distinctive words appear in the question —
    # "oil" should reach "Cooking Oil" without the full name being spoken.
    scored: list[tuple[float, Product]] = []
    for product in products:
        words = {w.lower() for w in product.name.split() if w.lower() not in QUESTION_WORDS}
        if words and (words & asked):
            scored.append((len(words & asked) / len(words), product))

    if scored:
        scored.sort(key=lambda s: s[0], reverse=True)
        # Only accept when one product stands out.
        if len(scored) == 1 or scored[0][0] > scored[1][0]:
            return scored[0][1]
        return None

    match = match_product(" ".join(asked), products)
    if match.best and match.score >= 0.6 and not match.ambiguous:
        return match.best.product
    return None


def find_customer(db: Session, business_id: UUID, question: str) -> Customer | None:
    customers = db.execute(
        select(Customer).where(Customer.business_id == business_id)
    ).scalars().all()
    lowered = question.lower()
    return next((c for c in customers if c.name.lower() in lowered), None)


# --- intent handlers -------------------------------------------------------

def _stock_level(db: Session, business_id: UUID, question: str) -> QueryAnswer:
    product = find_product(db, business_id, question)
    if not product:
        return _overview(db, business_id, question)

    info = inventory_service.product_status(db, product)
    qty, unit = info["current_quantity"], product.base_unit
    days = info["estimated_days_to_stockout"]

    answer = f"You have {qty:g} {unit} of {product.name}."
    if days is not None:
        answer += f" At about {info['avg_daily_usage']:g} {unit} a day, that lasts roughly {days:.0f} more days."
    if qty <= info["minimum_quantity"]:
        answer += f" That is below your minimum of {info['minimum_quantity']:g}."

    return QueryAnswer(
        intent=STOCK_LEVEL, answer=answer, facts=info, visual="stock",
        items=[info], product_id=product.id, product_name=product.name,
    )


def _low_stock(db: Session, business_id: UUID, question: str) -> QueryAnswer:
    found = insights_service.alerts(db, business_id)
    if not found:
        answer = "Nothing is running low. Every product is above its minimum with comfortable cover."
    else:
        names = ", ".join(a["product_name"] for a in found[:3])
        answer = (
            f"{len(found)} product{'s' if len(found) != 1 else ''} need attention: {names}"
            f"{' and others' if len(found) > 3 else ''}. "
            f"{found[0]['message']}"
        )
    return QueryAnswer(intent=LOW_STOCK, answer=answer, facts={"alerts": found},
                       items=found, visual="list")


def _reorder(db: Session, business_id: UUID, question: str) -> QueryAnswer:
    found = insights_service.reorder_list(db, business_id)
    if not found:
        answer = "Nothing needs reordering right now — every product covers its lead time."
    else:
        lead = _join(
            [f"{r['suggested_quantity']:g} {r['base_unit']} of {r['product_name']}" for r in found[:3]]
        )
        answer = f"Order {lead}"
        answer += f" — and {len(found) - 3} more." if len(found) > 3 else "."
    return QueryAnswer(intent=REORDER, answer=answer, facts={"recommendations": found},
                       items=found, visual="list")


def _period(db: Session, business_id: UUID, question: str, outgoing: bool) -> QueryAnswer:
    start, end, label = detect_window(question, default_days=1 if outgoing else 7)
    types = ({EventType.SALE, EventType.CREDIT_SALE} if outgoing
             else {EventType.PURCHASE, EventType.STOCK_IN})
    rows = insights_service.period_totals(db, business_id, start, end, types)
    verb = "sold" if outgoing else "came in"

    if not rows:
        answer = f"Nothing {verb} {label}."
    else:
        lead = _join([f"{r['quantity']:g} {r['base_unit']} of {r['product_name']}" for r in rows[:3]])
        total_lines = len(rows)
        answer = f"{label.capitalize()} you {verb if outgoing else 'received'} {lead}"
        answer += f" — {total_lines} products in all." if total_lines > 3 else "."

    return QueryAnswer(
        intent=SOLD_PERIOD if outgoing else RECEIVED_PERIOD,
        answer=answer, facts={"rows": rows, "window": label},
        items=rows, visual="list", window_label=label,
    )


def _explain(db: Session, business_id: UUID, question: str) -> QueryAnswer:
    """The WHY engine: reconstruct what moved a product's stock, and say so."""
    product = find_product(db, business_id, question)
    if not product:
        return _overview(db, business_id, question)

    start, end, label = detect_window(question, default_days=7)
    days = max((end - start).days, 1)
    breakdown = inventory_service.movement_breakdown(db, product.id, days)
    unit = product.base_unit

    outflow = [b for b in breakdown if b["net_change"] < 0]
    inflow = [b for b in breakdown if b["net_change"] > 0]
    total_out = sum(abs(b["net_change"]) for b in outflow)
    total_in = sum(b["net_change"] for b in inflow)

    if not breakdown:
        answer = f"{product.name} has not moved in {label}. It is still at {float(product.current_quantity):g} {unit}."
    else:
        def phrases(rows, templates, signed):
            out = []
            for row in sorted(rows, key=lambda b: b["net_change"] * (1 if signed else -1)):
                template = templates.get(row["event_type"])
                if template:
                    value = abs(row["net_change"])
                    out.append(template.format(n=value, verb=_verb(value)))
            return out

        out_parts = _join(phrases(outflow, OUTFLOW_PHRASES, signed=True))
        in_parts = _join(phrases(inflow, INFLOW_PHRASES, signed=False))

        asks_where = bool(re.search(r"\bwhere\b|ఎక్కడ|कहां|कहाँ", question.lower()))

        # The clause after the colon has to explain the headline. Leading with
        # an increase and then listing what left reads as a contradiction, so
        # the direction of the headline decides which list follows it.
        if asks_where and total_out > 0:
            headline = f"{total_out:g} {unit} of {product.name} left the shop {label}"
            leading, trailing = out_parts, in_parts
        elif total_out > total_in:
            headline = f"{product.name} decreased by {total_out - total_in:g} {unit} {label}"
            leading, trailing = out_parts, in_parts
        else:
            headline = f"{product.name} increased by {total_in - total_out:g} {unit} {label}"
            leading, trailing = in_parts, out_parts

        answer = headline + (f": {leading}." if leading else ".")
        if trailing:
            answer += f" Against that, {trailing}."
        answer += f" It now stands at {float(product.current_quantity):g} {unit}."

        # A "why is X low" question about something that is no longer low has
        # been overtaken by events; say so rather than leaving the owner to
        # work it out from the numbers.
        asks_low = bool(re.search(r"\blow\b|\bout of stock\b|\brunning out\b", question.lower()))
        if asks_low and float(product.current_quantity) > float(product.minimum_quantity):
            answer += f" That is above your minimum of {float(product.minimum_quantity):g}, so it is no longer low."

    facts = {
        "product": product.name,
        "unit": unit,
        "window": label,
        "current_quantity": float(product.current_quantity),
        "total_in": round(total_in, 2),
        "total_out": round(total_out, 2),
        "breakdown": [
            {"event_type": b["event_type"].value if hasattr(b["event_type"], "value") else b["event_type"],
             "net_change": b["net_change"], "count": b["count"]}
            for b in breakdown
        ],
    }
    return QueryAnswer(intent=EXPLAIN, answer=answer, facts=facts, items=facts["breakdown"],
                       visual="breakdown", product_id=product.id, product_name=product.name,
                       window_label=label)


def _customer_activity(db: Session, business_id: UUID, question: str) -> QueryAnswer:
    customer = find_customer(db, business_id, question)
    if not customer:
        return _overview(db, business_id, question)

    rows = db.execute(
        select(InventoryEvent, Product.name, Product.base_unit)
        .join(Product, Product.id == InventoryEvent.product_id)
        .where(InventoryEvent.customer_id == customer.id)
        .order_by(InventoryEvent.occurred_at.desc())
        .limit(30)
    ).all()

    items = [
        {
            "product_name": name,
            "base_unit": unit,
            "event_type": event.event_type.value,
            "quantity": float(event.quantity),
            "unit": event.unit,
            "delta": float(event.delta),
            "occurred_at": event.occurred_at.isoformat(),
            "price": float(event.price) if event.price is not None else None,
        }
        for event, name, unit in rows
    ]

    if not items:
        answer = f"{customer.name} has no recorded transactions."
    else:
        # Totals are summed in base units (the event delta), never in the spoken
        # unit, so "2 bags" and "5 kg" of the same product cannot be added together.
        totals: dict[str, float] = {}
        units: dict[str, str] = {}
        for item in items:
            name = item["product_name"]
            totals[name] = totals.get(name, 0) + abs(item["delta"])
            units[name] = item["base_unit"]
        ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
        summary = _join([f"{qty:g} {units[name]} of {name}" for name, qty in ranked[:3]])
        answer = (
            f"{customer.name} has taken {summary} across {len(items)} transactions. "
            f"Outstanding credit is ₹{float(customer.outstanding_credit):,.0f}."
        )

    return QueryAnswer(
        intent=CUSTOMER_ACTIVITY, answer=answer,
        facts={"customer": customer.name,
               "outstanding_credit": float(customer.outstanding_credit),
               "events": items},
        items=items, visual="timeline",
    )


def _credit_book(db: Session, business_id: UUID, question: str) -> QueryAnswer:
    """Who owes money, worst first — the question every shop owner asks."""
    customers = db.execute(
        select(Customer)
        .where(Customer.business_id == business_id, Customer.outstanding_credit > 0)
        .order_by(Customer.outstanding_credit.desc())
    ).scalars().all()

    items = [
        {
            "customer_id": c.id,
            "customer_name": c.name,
            "phone": c.phone or "",
            "outstanding_credit": float(c.outstanding_credit),
        }
        for c in customers
    ]
    total = sum(item["outstanding_credit"] for item in items)

    if not items:
        answer = "Nobody owes you anything right now — the credit book is clear."
    else:
        lead = _join([f"{i['customer_name']} ₹{i['outstanding_credit']:,.0f}" for i in items[:3]])
        answer = (
            f"₹{total:,.0f} is outstanding across {len(items)} "
            f"customer{'s' if len(items) != 1 else ''}: {lead}"
        )
        answer += f" — and {len(items) - 3} more." if len(items) > 3 else "."

    return QueryAnswer(
        intent=CREDIT_BOOK, answer=answer,
        facts={"total_outstanding": round(total, 2), "customers": items},
        items=items, visual="list",
    )


def _what_changed(db: Session, business_id: UUID, question: str) -> QueryAnswer:
    """A plain summary of the period: what moved in, what moved out, what it cost."""
    start, end, label = detect_window(question, default_days=1)

    rows = db.execute(
        select(InventoryEvent, Product.name, Product.base_unit)
        .join(Product, Product.id == InventoryEvent.product_id)
        .where(
            InventoryEvent.business_id == business_id,
            InventoryEvent.occurred_at >= start,
            InventoryEvent.occurred_at <= end,
        )
        .order_by(InventoryEvent.occurred_at.desc())
    ).all()

    if not rows:
        return QueryAnswer(
            intent=WHAT_CHANGED,
            answer=f"Nothing was recorded {label}.",
            facts={"window": label, "event_count": 0},
            items=[], visual="timeline", window_label=label,
        )

    by_type: dict[str, int] = {}
    revenue = 0.0
    credit_given = 0.0
    products_touched: set[str] = set()
    for event, name, _unit in rows:
        key = event.event_type.value
        by_type[key] = by_type.get(key, 0) + 1
        products_touched.add(name)
        if event.price is not None:
            if event.event_type == EventType.SALE:
                revenue += float(event.price)
            elif event.event_type == EventType.CREDIT_SALE:
                credit_given += float(event.price)

    items = [
        {
            "product_name": name,
            "base_unit": unit,
            "event_type": event.event_type.value,
            "quantity": float(event.quantity),
            "unit": event.unit,
            "delta": float(event.delta),
            "occurred_at": event.occurred_at.isoformat(),
            "customer_name": event.customer.name if event.customer else None,
            "price": float(event.price) if event.price is not None else None,
        }
        for event, name, unit in rows[:30]
    ]

    parts = [f"{len(rows)} entries across {len(products_touched)} products"]
    if revenue:
        parts.append(f"₹{revenue:,.0f} in paid sales")
    if credit_given:
        parts.append(f"₹{credit_given:,.0f} given on credit")
    answer = f"{label.capitalize()}: {_join(parts)}."

    losses = by_type.get(EventType.DAMAGE.value, 0) + by_type.get(EventType.LOSS.value, 0)
    if losses:
        answer += f" {losses} entr{'y was' if losses == 1 else 'ies were'} damage or loss."

    return QueryAnswer(
        intent=WHAT_CHANGED, answer=answer,
        facts={
            "window": label,
            "event_count": len(rows),
            "products_touched": len(products_touched),
            "revenue": round(revenue, 2),
            "credit_given": round(credit_given, 2),
            "by_type": by_type,
        },
        items=items, visual="timeline", window_label=label,
    )


def _unusual(db: Session, business_id: UUID, question: str) -> QueryAnswer:
    found = insights_service.unusual_movement(db, business_id)
    answer = (
        "Nothing is moving unusually — recent sales match the previous period."
        if not found else found[0]["message"]
    )
    if len(found) > 1:
        answer += f" {len(found) - 1} other product{'s' if len(found) > 2 else ''} also shifted."
    return QueryAnswer(intent=UNUSUAL, answer=answer, facts={"findings": found},
                       items=found, visual="list")


def _overview(db: Session, business_id: UUID, question: str) -> QueryAnswer:
    products = inventory_service.list_products(db, business_id)
    found = insights_service.alerts(db, business_id)
    snapshot = [
        {"product_name": p.name, "current_quantity": float(p.current_quantity),
         "base_unit": p.base_unit}
        for p in products
    ]
    answer = (
        f"You are tracking {len(products)} products. "
        + (f"{len(found)} need attention, starting with {found[0]['product_name']}."
           if found else "Everything is comfortably stocked.")
    )
    return QueryAnswer(intent=OVERVIEW, answer=answer,
                       facts={"inventory": snapshot, "alerts": found},
                       items=found or snapshot, visual="list")


HANDLERS = {
    STOCK_LEVEL: _stock_level,
    LOW_STOCK: _low_stock,
    REORDER: _reorder,
    EXPLAIN: _explain,
    CUSTOMER_ACTIVITY: _customer_activity,
    CREDIT_BOOK: _credit_book,
    WHAT_CHANGED: _what_changed,
    UNUSUAL: _unusual,
    OVERVIEW: _overview,
}


def ask(db: Session, business: Business, question: str,
        reply_language: str | None = None) -> QueryAnswer:
    question = (question or "").strip()
    if not question:
        return QueryAnswer(intent=OVERVIEW, answer="Ask me anything about your stock.", facts={})

    intent = detect_intent(question)

    # "Show me everything related to Ramesh" names no action, only a person.
    # A question that falls through to the overview but does name a known
    # customer is really about that customer.
    if intent == OVERVIEW and find_customer(db, business.id, question):
        intent = CUSTOMER_ACTIVITY

    if intent == SOLD_PERIOD:
        result = _period(db, business.id, question, outgoing=True)
    elif intent == RECEIVED_PERIOD:
        result = _period(db, business.id, question, outgoing=False)
    else:
        result = HANDLERS.get(intent, _overview)(db, business.id, question)

    # Reasoning layer: rephrase the verified facts, never recompute them.
    language = reply_language or primary_language(detect_language(question))
    provider = get_ai_provider()
    if provider.is_llm:
        try:
            phrased = provider.answer_question(
                question,
                {"intent": result.intent, "computed_answer": result.answer, **result.facts},
                language,
            )
            if phrased:
                result.answer = phrased
                result.grounded_by = provider.name
        except Exception:  # noqa: BLE001 — a phrasing failure must not lose the answer
            pass

    return result
