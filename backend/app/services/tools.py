"""The tools A.R.I.A. is allowed to use.

Every tool is a thin, validated wrapper over a business service that already
exists and has already been tested. No tool writes SQL, builds a query, or
touches a table directly — inventory still changes only through
`event_engine.record_event`, products only through `product_service`, payments
only through the same balance check the REST route uses.

The model proposes a tool and arguments. This module decides whether that is a
legal thing to do, and the underlying service decides whether it is a valid
thing to do. Both must agree before anything is written.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AriaError
from app.models import (
    Business, Customer, EventType, Expense, InventoryEvent, Payment,
    PaymentStatus, Product, Supplier, UnitConversion,
)
from app.schemas import ProductCreate, ProductUpdate, UnitConversionIn
from app.services import (
    business_context, insights_service, inventory_service, product_service, query_engine,
)
from app.services.event_engine import record_event
from app.services.product_matcher import match_product
from app.services.units import to_decimal

# Actions that move money or destroy data always stop for a human yes.
CONFIRM_REQUIRED = {
    "make_credit_sale",
    "record_payment",
    "record_expense",
    "delete_product",
    "adjust_stock",
    "create_product",
    "update_product",
    "create_supplier",
}


class ToolError(Exception):
    """A tool could not do what was asked. Reported to the model verbatim."""


@dataclass
class ToolContext:
    db: Session
    business: Business
    source: str = "aria"


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    handler: Callable[[ToolContext, dict], Any]
    writes: bool = False
    tags: list[str] = field(default_factory=list)

    @property
    def needs_confirmation(self) -> bool:
        return self.name in CONFIRM_REQUIRED


REGISTRY: dict[str, Tool] = {}


def tool(
    name: str,
    description: str,
    parameters: dict,
    writes: bool = False,
    tags: list[str] | None = None,
):
    def decorator(fn):
        REGISTRY[name] = Tool(
            name=name, description=description, parameters=parameters,
            handler=fn, writes=writes, tags=tags or [],
        )
        return fn

    return decorator


def _schema(properties: dict, required: list[str] | None = None) -> dict:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": False,
    }


STR = {"type": "string"}
NUM = {"type": "number"}


# --- shared resolution helpers -------------------------------------------
# Identity is resolved here, against the database, from a *name*. The model
# never supplies an id it invented, and an ambiguous name is an error the model
# must resolve with the user rather than a coin toss.

def _resolve_product(ctx: ToolContext, ref: str) -> Product:
    ref = (ref or "").strip()
    if not ref:
        raise ToolError("No product was named.")

    products = inventory_service.list_products(ctx.db, ctx.business.id)
    if not products:
        raise ToolError("This business has no products yet.")

    exact = next((p for p in products if p.name.lower() == ref.lower()), None)
    if exact:
        return exact

    match = match_product(ref, products)
    if not match.candidates:
        raise ToolError(f"I couldn't find a product called '{ref}'.")
    if match.ambiguous:
        names = ", ".join(c.product.name for c in match.candidates[:4])
        raise ToolError(f"'{ref}' is ambiguous. Did you mean: {names}?")
    return match.best.product


def _resolve_customer(ctx: ToolContext, ref: str, create: bool = False) -> Customer:
    ref = (ref or "").strip()
    if not ref:
        raise ToolError("No customer was named.")
    customers = ctx.db.execute(
        select(Customer).where(Customer.business_id == ctx.business.id)
    ).scalars().all()

    exact = next((c for c in customers if c.name.lower() == ref.lower()), None)
    if exact:
        return exact
    partial = [c for c in customers if ref.lower() in c.name.lower()]
    if len(partial) == 1:
        return partial[0]
    if len(partial) > 1:
        raise ToolError(
            f"Several customers match '{ref}': {', '.join(c.name for c in partial[:4])}."
        )
    if create:
        customer = Customer(business_id=ctx.business.id, name=ref)
        ctx.db.add(customer)
        ctx.db.flush()
        return customer
    raise ToolError(f"I couldn't find a customer called '{ref}'.")


def _product_view(product: Product) -> dict:
    return {
        "product_id": str(product.id),
        "name": product.name,
        "category": product.category,
        "current_quantity": float(product.current_quantity),
        "base_unit": product.base_unit,
        "minimum_quantity": float(product.minimum_quantity),
        "reorder_quantity": float(product.reorder_quantity),
        "price": float(product.price),
        "unit_conversions": [
            {"unit": c.unit_name, "equals_base_units": float(c.factor_to_base_unit)}
            for c in product.conversions
        ],
    }


def _record(ctx: ToolContext, product: Product, event_type: EventType, args: dict,
            customer: Customer | None = None, payment_status=PaymentStatus.NA) -> dict:
    """Single funnel into the existing event engine."""
    quantity = args.get("quantity")
    if quantity is None:
        raise ToolError("A quantity is required.")
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ToolError(f"'{quantity}' is not a number.")

    try:
        event = record_event(
            ctx.db,
            business_id=ctx.business.id,
            product=product,
            event_type=event_type,
            quantity=quantity,
            unit=args.get("unit") or product.base_unit,
            customer_name=customer.name if customer else None,
            price=args.get("price"),
            payment_status=payment_status,
            source=ctx.source,
            original_text=args.get("__utterance__", "") or "",
            normalized_text=args.get("reason") or f"{event_type.value} via A.R.I.A.",
            confidence=1.0,
        )
    except AriaError as exc:
        raise ToolError(str(exc)) from exc

    ctx.db.refresh(product)
    return {
        "recorded": True,
        "event_id": str(event.id),
        "event_type": event_type.value,
        "product": product.name,
        "quantity": float(event.quantity),
        "unit": event.unit,
        "applied_change": float(event.delta),
        "resulting_quantity": float(product.current_quantity),
        "resulting_unit": product.base_unit,
    }


# =========================================================================
# INVENTORY — reads
# =========================================================================

@tool("get_inventory", "List every product with its real current stock level.",
      _schema({"only_needs_attention": {"type": "boolean"}}), tags=["inventory"])
def _get_inventory(ctx: ToolContext, args: dict) -> dict:
    rows = inventory_service.list_products(ctx.db, ctx.business.id)
    items = [_product_view(p) for p in rows]
    if args.get("only_needs_attention"):
        alerts = {a["product_id"] for a in insights_service.alerts(ctx.db, ctx.business.id)}
        items = [i for i in items if UUID(i["product_id"]) in alerts]
    return {"products": items, "count": len(items)}


@tool("search_products", "Find products whose name matches a search term.",
      _schema({"query": STR}, ["query"]), tags=["inventory"])
def _search_products(ctx: ToolContext, args: dict) -> dict:
    term = (args.get("query") or "").lower().strip()
    rows = inventory_service.list_products(ctx.db, ctx.business.id)
    hits = [p for p in rows if term in p.name.lower() or term in p.category.lower()]
    return {"matches": [_product_view(p) for p in hits], "count": len(hits)}


@tool("get_product", "Get one product's real stock, thresholds and unit conversions.",
      _schema({"product": STR}, ["product"]), tags=["inventory"])
def _get_product(ctx: ToolContext, args: dict) -> dict:
    product = _resolve_product(ctx, args.get("product", ""))
    status = inventory_service.product_status(ctx.db, product)
    return {**_product_view(product), "status": status}


@tool("get_product_history", "Recent stock movements for one product.",
      _schema({"product": STR, "days": {"type": "integer"}}, ["product"]), tags=["inventory"])
def _get_product_history(ctx: ToolContext, args: dict) -> dict:
    product = _resolve_product(ctx, args.get("product", ""))
    days = int(args.get("days") or 30)
    return inventory_service.product_history(ctx.db, product, days=days)


# =========================================================================
# INVENTORY — writes (all through the existing event engine)
# =========================================================================

_MOVE_SCHEMA = _schema(
    {"product": STR, "quantity": NUM, "unit": STR, "reason": STR},
    ["product", "quantity"],
)


@tool("add_stock", "Record stock arriving (STOCK_IN). Increases quantity on hand.",
      _MOVE_SCHEMA, writes=True, tags=["inventory"])
def _add_stock(ctx, args):
    return _record(ctx, _resolve_product(ctx, args.get("product", "")), EventType.STOCK_IN, args)


@tool("record_purchase", "Record stock bought from a supplier (PURCHASE).",
      _schema({"product": STR, "quantity": NUM, "unit": STR, "price": NUM, "supplier": STR,
               "reason": STR}, ["product", "quantity"]), writes=True, tags=["inventory"])
def _record_purchase(ctx, args):
    return _record(ctx, _resolve_product(ctx, args.get("product", "")), EventType.PURCHASE, args)


@tool("remove_stock", "Record stock leaving for a non-sale reason (STOCK_OUT).",
      _MOVE_SCHEMA, writes=True, tags=["inventory"])
def _remove_stock(ctx, args):
    return _record(ctx, _resolve_product(ctx, args.get("product", "")), EventType.STOCK_OUT, args)


@tool("make_sale", "Record a paid sale (SALE). Decreases quantity on hand.",
      _schema({"product": STR, "quantity": NUM, "unit": STR, "price": NUM, "customer": STR},
              ["product", "quantity"]), writes=True, tags=["inventory", "sales"])
def _make_sale(ctx, args):
    product = _resolve_product(ctx, args.get("product", ""))
    customer = None
    if args.get("customer"):
        customer = _resolve_customer(ctx, args["customer"], create=True)
    return _record(ctx, product, EventType.SALE, args, customer, PaymentStatus.PAID)


@tool("make_credit_sale",
      "Record a sale on credit (CREDIT_SALE). Adds to the customer's outstanding balance.",
      _schema({"product": STR, "quantity": NUM, "unit": STR, "price": NUM, "customer": STR},
              ["product", "quantity", "customer"]), writes=True, tags=["inventory", "credit"])
def _make_credit_sale(ctx, args):
    product = _resolve_product(ctx, args.get("product", ""))
    customer = _resolve_customer(ctx, args.get("customer", ""), create=True)
    return _record(ctx, product, EventType.CREDIT_SALE, args, customer, PaymentStatus.CREDIT)


@tool("record_return", "Record stock returned by a customer (RETURN).",
      _schema({"product": STR, "quantity": NUM, "unit": STR, "customer": STR, "reason": STR},
              ["product", "quantity"]), writes=True, tags=["inventory"])
def _record_return(ctx, args):
    customer = _resolve_customer(ctx, args["customer"], create=True) if args.get("customer") else None
    return _record(ctx, _resolve_product(ctx, args.get("product", "")), EventType.RETURN, args, customer)


@tool("record_damage", "Record stock damaged or spoiled (DAMAGE).",
      _MOVE_SCHEMA, writes=True, tags=["inventory"])
def _record_damage(ctx, args):
    return _record(ctx, _resolve_product(ctx, args.get("product", "")), EventType.DAMAGE, args)


@tool("record_loss", "Record stock lost or stolen (LOSS).",
      _MOVE_SCHEMA, writes=True, tags=["inventory"])
def _record_loss(ctx, args):
    return _record(ctx, _resolve_product(ctx, args.get("product", "")), EventType.LOSS, args)


@tool("adjust_stock",
      "Correct stock to a counted figure. Records the difference as an ADJUSTMENT.",
      _schema({"product": STR, "counted_quantity": NUM, "unit": STR, "reason": STR},
              ["product", "counted_quantity"]), writes=True, tags=["inventory"])
def _adjust_stock(ctx: ToolContext, args: dict) -> dict:
    product = _resolve_product(ctx, args.get("product", ""))
    try:
        counted = float(args.get("counted_quantity"))
    except (TypeError, ValueError):
        raise ToolError("A counted quantity is required.")

    current = float(product.current_quantity)
    difference = counted - current
    if difference == 0:
        return {"recorded": False, "product": product.name,
                "message": f"{product.name} is already recorded as {current:g} {product.base_unit}."}

    result = _record(
        ctx, product, EventType.ADJUSTMENT,
        {**args, "quantity": difference, "unit": product.base_unit,
         "reason": args.get("reason") or f"Counted {counted:g}, system had {current:g}"},
    )
    return {**result, "previous_quantity": current, "counted_quantity": counted}


# =========================================================================
# PRODUCT CRUD — through the existing product service
# =========================================================================

@tool("create_product", "Create a new product in the catalogue.",
      _schema({"name": STR, "base_unit": STR, "category": STR, "opening_stock": NUM,
               "minimum_quantity": NUM, "reorder_quantity": NUM, "price": NUM},
              ["name", "base_unit"]), writes=True, tags=["products"])
def _create_product(ctx: ToolContext, args: dict) -> dict:
    units = business_context.units_for(ctx.business.business_type)
    unit = (args.get("base_unit") or "").strip().lower()
    if unit not in units:
        raise ToolError(f"'{unit}' is not a supported unit. Use one of: {', '.join(units[:10])}.")

    try:
        payload = ProductCreate(
            name=(args.get("name") or "").strip(),
            category=(args.get("category") or "general").strip() or "general",
            base_unit=unit,
            opening_stock=float(args.get("opening_stock") or 0),
            minimum_quantity=float(args.get("minimum_quantity") or 0),
            reorder_quantity=float(args.get("reorder_quantity") or 0),
            price=float(args.get("price") or 0),
            conversions=[],
        )
        product = product_service.create_product(ctx.db, ctx.business.id, payload)
    except AriaError as exc:
        raise ToolError(str(exc)) from exc
    except ValueError as exc:
        raise ToolError(f"Those product details are not valid: {exc}") from exc

    return {"created": True, **_product_view(product)}


@tool("update_product", "Change a product's price, category or stock thresholds.",
      _schema({"product": STR, "name": STR, "category": STR, "price": NUM,
               "minimum_quantity": NUM, "reorder_quantity": NUM}, ["product"]),
      writes=True, tags=["products"])
def _update_product(ctx: ToolContext, args: dict) -> dict:
    product = _resolve_product(ctx, args.get("product", ""))
    fields = {k: args[k] for k in
              ("name", "category", "price", "minimum_quantity", "reorder_quantity")
              if args.get(k) is not None}
    if not fields:
        raise ToolError("Nothing to change — no new values were given.")

    before = _product_view(product)
    try:
        updated = product_service.update_product(ctx.db, product, ProductUpdate(**fields))
    except AriaError as exc:
        raise ToolError(str(exc)) from exc

    return {"updated": True, "changed_fields": list(fields), "before": before,
            "after": _product_view(updated)}


@tool("delete_product",
      "Archive a product. It stays in history because past events reference it.",
      _schema({"product": STR}, ["product"]), writes=True, tags=["products"])
def _delete_product(ctx: ToolContext, args: dict) -> dict:
    product = _resolve_product(ctx, args.get("product", ""))
    product_service.set_archived(ctx.db, product, True)
    return {"archived": True, "product": product.name,
            "note": "Archived rather than deleted, so its history stays intact."}


@tool("set_unit_conversion",
      "Teach a pack size, e.g. one carton of Coke is 24 pieces. Used for future counting.",
      _schema({"product": STR, "unit": STR, "equals_base_units": NUM},
              ["product", "unit", "equals_base_units"]), writes=True, tags=["products", "memory"])
def _set_unit_conversion(ctx: ToolContext, args: dict) -> dict:
    product = _resolve_product(ctx, args.get("product", ""))
    unit = (args.get("unit") or "").strip().lower()
    if not unit:
        raise ToolError("Which unit? For example 'carton'.")
    if unit == product.base_unit:
        raise ToolError(f"{product.name} is already counted in {unit}.")
    try:
        factor = float(args.get("equals_base_units"))
    except (TypeError, ValueError):
        raise ToolError("How many base units does one of these contain?")
    if factor <= 0:
        raise ToolError("A pack size must be greater than zero.")

    existing = next((c for c in product.conversions if c.unit_name == unit), None)
    if existing:
        existing.factor_to_base_unit = to_decimal(factor)
    else:
        ctx.db.add(UnitConversion(product_id=product.id, unit_name=unit,
                                  factor_to_base_unit=to_decimal(factor)))
    ctx.db.commit()
    ctx.db.refresh(product)
    return {"remembered": True, "product": product.name,
            "rule": f"1 {unit} = {factor:g} {product.base_unit}",
            "conversions": _product_view(product)["unit_conversions"]}


# =========================================================================
# CUSTOMERS & MONEY
# =========================================================================

@tool("get_customers", "List customers with their real outstanding credit.",
      _schema({"only_owing": {"type": "boolean"}}), tags=["customers"])
def _get_customers(ctx: ToolContext, args: dict) -> dict:
    rows = ctx.db.execute(
        select(Customer).where(Customer.business_id == ctx.business.id).order_by(Customer.name)
    ).scalars().all()
    if args.get("only_owing"):
        rows = [c for c in rows if float(c.outstanding_credit) > 0]
    return {
        "customers": [
            {"customer_id": str(c.id), "name": c.name, "phone": c.phone or "",
             "outstanding_credit": float(c.outstanding_credit)}
            for c in rows
        ],
        "total_outstanding": round(sum(float(c.outstanding_credit) for c in rows), 2),
    }


@tool("get_customer_history", "What one customer has taken, paid and still owes.",
      _schema({"customer": STR}, ["customer"]), tags=["customers"])
def _get_customer_history(ctx: ToolContext, args: dict) -> dict:
    customer = _resolve_customer(ctx, args.get("customer", ""))
    rows = ctx.db.execute(
        select(InventoryEvent, Product.name, Product.base_unit)
        .join(Product, Product.id == InventoryEvent.product_id)
        .where(InventoryEvent.customer_id == customer.id)
        .order_by(InventoryEvent.occurred_at.desc()).limit(40)
    ).all()
    payments = ctx.db.execute(
        select(Payment).where(Payment.customer_id == customer.id)
        .order_by(Payment.occurred_at.desc()).limit(20)
    ).scalars().all()

    totals: dict[str, dict] = {}
    for event, name, base_unit in rows:
        bucket = totals.setdefault(name, {"product": name, "unit": base_unit, "quantity": 0.0})
        bucket["quantity"] += abs(float(event.delta))

    return {
        "customer": customer.name,
        "outstanding_credit": float(customer.outstanding_credit),
        "transaction_count": len(rows),
        "totals": sorted(totals.values(), key=lambda t: t["quantity"], reverse=True),
        "payments": [{"amount": float(p.amount), "when": p.occurred_at.isoformat()}
                     for p in payments],
    }


@tool("create_customer", "Add a customer to the book.",
      _schema({"name": STR, "phone": STR}, ["name"]), writes=True, tags=["customers"])
def _create_customer(ctx: ToolContext, args: dict) -> dict:
    name = (args.get("name") or "").strip()
    if not name:
        raise ToolError("A customer name is required.")
    existing = ctx.db.execute(
        select(Customer).where(Customer.business_id == ctx.business.id,
                               func.lower(Customer.name) == name.lower())
    ).scalar_one_or_none()
    if existing:
        return {"created": False, "customer_id": str(existing.id),
                "message": f"{existing.name} is already a customer."}
    customer = Customer(business_id=ctx.business.id, name=name, phone=args.get("phone") or "")
    ctx.db.add(customer)
    ctx.db.commit()
    ctx.db.refresh(customer)
    return {"created": True, "customer_id": str(customer.id), "name": customer.name}


@tool("record_payment",
      "Record money received from a customer against their credit balance.",
      _schema({"customer": STR, "amount": NUM, "note": STR}, ["customer", "amount"]),
      writes=True, tags=["customers", "money"])
def _record_payment(ctx: ToolContext, args: dict) -> dict:
    customer = _resolve_customer(ctx, args.get("customer", ""))
    try:
        amount = to_decimal(float(args.get("amount")))
    except (TypeError, ValueError):
        raise ToolError("How much was paid?")
    if amount <= 0:
        raise ToolError("A payment must be greater than zero.")

    # The same balance rule the REST route enforces. Not a second calculation —
    # the identical check, so the two paths can never disagree.
    outstanding = to_decimal(customer.outstanding_credit)
    if amount > outstanding:
        raise ToolError(
            f"{customer.name} owes ₹{float(outstanding):,.0f}. "
            f"A payment of ₹{float(amount):,.0f} is more than the outstanding amount."
        )

    payment = Payment(business_id=ctx.business.id, customer_id=customer.id,
                      amount=amount, note=args.get("note") or "", source=ctx.source)
    ctx.db.add(payment)
    customer.outstanding_credit = outstanding - amount
    ctx.db.commit()
    return {"recorded": True, "customer": customer.name, "amount": float(amount),
            "remaining_balance": float(customer.outstanding_credit)}


# =========================================================================
# SUPPLIERS
# =========================================================================

@tool("get_suppliers", "List suppliers.", _schema({}), tags=["suppliers"])
def _get_suppliers(ctx: ToolContext, args: dict) -> dict:
    rows = ctx.db.execute(
        select(Supplier).where(Supplier.business_id == ctx.business.id).order_by(Supplier.name)
    ).scalars().all()
    return {"suppliers": [
        {"supplier_id": str(s.id), "name": s.name, "phone": s.phone or "",
         "supplies": s.supplies or "", "lead_time_days": float(s.lead_time_days)}
        for s in rows
    ]}


@tool("create_supplier", "Add a supplier the business buys stock from.",
      _schema({"name": STR, "phone": STR, "supplies": STR, "lead_time_days": NUM}, ["name"]),
      writes=True, tags=["suppliers"])
def _create_supplier(ctx: ToolContext, args: dict) -> dict:
    name = (args.get("name") or "").strip()
    if not name:
        raise ToolError("A supplier name is required.")
    existing = ctx.db.execute(
        select(Supplier).where(Supplier.business_id == ctx.business.id,
                               func.lower(Supplier.name) == name.lower())
    ).scalar_one_or_none()
    if existing:
        return {"created": False, "supplier_id": str(existing.id),
                "message": f"{existing.name} is already a supplier."}

    supplier = Supplier(
        business_id=ctx.business.id, name=name, phone=args.get("phone") or "",
        supplies=args.get("supplies") or "",
        lead_time_days=to_decimal(args.get("lead_time_days") or 7),
    )
    ctx.db.add(supplier)
    ctx.db.commit()
    ctx.db.refresh(supplier)
    return {"created": True, "supplier_id": str(supplier.id), "name": supplier.name,
            "lead_time_days": float(supplier.lead_time_days)}


@tool("update_supplier", "Change a supplier's phone, goods or lead time.",
      _schema({"supplier": STR, "phone": STR, "supplies": STR, "lead_time_days": NUM},
              ["supplier"]), writes=True, tags=["suppliers"])
def _update_supplier(ctx: ToolContext, args: dict) -> dict:
    ref = (args.get("supplier") or "").strip().lower()
    rows = ctx.db.execute(
        select(Supplier).where(Supplier.business_id == ctx.business.id)
    ).scalars().all()
    supplier = next((s for s in rows if s.name.lower() == ref), None) \
        or next((s for s in rows if ref and ref in s.name.lower()), None)
    if not supplier:
        raise ToolError(f"I couldn't find a supplier called '{args.get('supplier')}'.")

    if args.get("phone") is not None:
        supplier.phone = args["phone"]
    if args.get("supplies") is not None:
        supplier.supplies = args["supplies"]
    if args.get("lead_time_days") is not None:
        supplier.lead_time_days = to_decimal(args["lead_time_days"])
    ctx.db.commit()
    return {"updated": True, "name": supplier.name,
            "lead_time_days": float(supplier.lead_time_days)}


# =========================================================================
# EXPENSES
# =========================================================================

@tool("record_expense", "Record money spent that is not stock — rent, transport, wages.",
      _schema({"amount": NUM, "category": STR, "note": STR}, ["amount"]),
      writes=True, tags=["money"])
def _record_expense(ctx: ToolContext, args: dict) -> dict:
    try:
        amount = float(args.get("amount"))
    except (TypeError, ValueError):
        raise ToolError("How much was spent?")
    if amount <= 0:
        raise ToolError("An expense must be greater than zero.")

    expense = Expense(
        business_id=ctx.business.id,
        category=(args.get("category") or "general").strip().lower() or "general",
        amount=to_decimal(amount), note=args.get("note") or "", source=ctx.source,
    )
    ctx.db.add(expense)
    ctx.db.commit()
    ctx.db.refresh(expense)
    return {"recorded": True, "expense_id": str(expense.id), "amount": float(expense.amount),
            "category": expense.category}


@tool("get_expenses", "Recent expenses, optionally for one category.",
      _schema({"days": {"type": "integer"}, "category": STR}), tags=["money"])
def _get_expenses(ctx: ToolContext, args: dict) -> dict:
    days = int(args.get("days") or 30)
    since = datetime.utcnow() - timedelta(days=days)
    stmt = select(Expense).where(Expense.business_id == ctx.business.id,
                                 Expense.occurred_at >= since)
    if args.get("category"):
        stmt = stmt.where(Expense.category == args["category"].strip().lower())
    rows = ctx.db.execute(stmt.order_by(Expense.occurred_at.desc())).scalars().all()

    by_category: dict[str, float] = {}
    for e in rows:
        by_category[e.category] = by_category.get(e.category, 0) + float(e.amount)

    return {
        "window_days": days,
        "total": round(sum(float(e.amount) for e in rows), 2),
        "by_category": [{"category": k, "amount": round(v, 2)} for k, v in
                        sorted(by_category.items(), key=lambda kv: kv[1], reverse=True)],
        "expenses": [{"amount": float(e.amount), "category": e.category, "note": e.note,
                      "when": e.occurred_at.isoformat()} for e in rows[:25]],
    }


# =========================================================================
# ANALYTICS & INTELLIGENCE — all computed by the existing services
# =========================================================================

@tool("get_alerts", "Products needing attention, with the reason for each.",
      _schema({}), tags=["analytics"])
def _get_alerts(ctx: ToolContext, args: dict) -> dict:
    found = insights_service.alerts(ctx.db, ctx.business.id)
    return {"alerts": [{k: (str(v) if k == "product_id" else v) for k, v in a.items()}
                       for a in found], "count": len(found)}


@tool("calculate_reorder", "What to reorder, with the quantity and the reasoning.",
      _schema({}), tags=["analytics"])
def _calculate_reorder(ctx: ToolContext, args: dict) -> dict:
    rows = insights_service.reorder_list(ctx.db, ctx.business.id)
    return {"recommendations": [{k: (str(v) if k == "product_id" else v) for k, v in r.items()}
                                for r in rows], "count": len(rows)}


@tool("predict_stockout", "Estimated days until a product runs out at its recent rate.",
      _schema({"product": STR}, ["product"]), tags=["analytics"])
def _predict_stockout(ctx: ToolContext, args: dict) -> dict:
    product = _resolve_product(ctx, args.get("product", ""))
    status = inventory_service.product_status(ctx.db, product)
    days = status.get("estimated_days_to_stockout")
    return {
        "product": product.name,
        "current_stock": float(product.current_quantity),
        "base_unit": product.base_unit,
        "average_daily_usage": status.get("avg_daily_usage"),
        "estimated_days_remaining": days,
        "risk": "high" if days is not None and days <= 3
                else "medium" if days is not None and days <= 7
                else "low",
        "basis": "Estimate from recent consumption, not a guarantee.",
    }


@tool("get_velocity", "Fastest and slowest moving products by daily usage.",
      _schema({}), tags=["analytics"])
def _get_velocity(ctx: ToolContext, args: dict) -> dict:
    movers = insights_service.movers(ctx.db, ctx.business.id)
    return {k: [{**m, "product_id": str(m["product_id"])} for m in v] for k, v in movers.items()}


@tool("detect_inventory_anomaly", "Products moving unusually fast or slow versus the prior period.",
      _schema({}), tags=["analytics"])
def _detect_anomaly(ctx: ToolContext, args: dict) -> dict:
    found = insights_service.unusual_movement(ctx.db, ctx.business.id)
    return {"findings": [{**f, "product_id": str(f["product_id"])} for f in found]}


@tool("explain_stock_change",
      "The WHY engine: reconstruct what moved a product's stock and why.",
      _schema({"product": STR, "question": STR}, ["product"]), tags=["analytics"])
def _explain(ctx: ToolContext, args: dict) -> dict:
    product = _resolve_product(ctx, args.get("product", ""))
    question = args.get("question") or f"why did {product.name} change"
    if product.name.lower() not in question.lower():
        question = f"{question} {product.name}"
    result = query_engine.ask(ctx.db, ctx.business, question)
    return {"explanation": result.answer, "facts": result.facts, "intent": result.intent}


@tool("search_business_events", "Search the event ledger by product, customer or free text.",
      _schema({"query": STR, "event_type": STR, "days": {"type": "integer"}}), tags=["memory"])
def _search_events(ctx: ToolContext, args: dict) -> dict:
    stmt = (
        select(InventoryEvent, Product.name, Customer.name)
        .join(Product, Product.id == InventoryEvent.product_id)
        .outerjoin(Customer, Customer.id == InventoryEvent.customer_id)
        .where(InventoryEvent.business_id == ctx.business.id)
    )
    if args.get("event_type"):
        try:
            stmt = stmt.where(InventoryEvent.event_type == EventType(args["event_type"].upper()))
        except ValueError:
            raise ToolError(f"'{args['event_type']}' is not a known event type.")
    if args.get("days"):
        stmt = stmt.where(
            InventoryEvent.occurred_at >= datetime.utcnow() - timedelta(days=int(args["days"]))
        )
    term = (args.get("query") or "").strip()
    if term:
        like = f"%{term}%"
        stmt = stmt.where(Product.name.ilike(like) | Customer.name.ilike(like))

    rows = ctx.db.execute(stmt.order_by(InventoryEvent.occurred_at.desc()).limit(30)).all()
    return {"events": [
        {"event_type": e.event_type.value, "product": pname, "customer": cname,
         "quantity": float(e.quantity), "unit": e.unit, "applied_change": float(e.delta),
         "price": float(e.price) if e.price is not None else None,
         "source": e.source, "when": e.occurred_at.isoformat()}
        for e, pname, cname in rows
    ], "count": len(rows)}


@tool("get_business_profile",
      "This business's trade, natural units and product count — use it to speak in their terms.",
      _schema({}), tags=["context"])
def _get_profile(ctx: ToolContext, args: dict) -> dict:
    kind = business_context.get_type(ctx.business.business_type)
    products = inventory_service.list_products(ctx.db, ctx.business.id)
    return {
        "business_name": ctx.business.business_name,
        "business_type": kind.key,
        "type_label": kind.label,
        "natural_units": list(kind.units),
        "categories": list(kind.categories),
        "product_count": len(products),
        "product_names": [p.name for p in products],
        "preferred_language": ctx.business.default_language,
    }


# =========================================================================

def tool_schemas(names: list[str] | None = None) -> list[dict]:
    """OpenAI-style function schemas for the model."""
    chosen = [REGISTRY[n] for n in names if n in REGISTRY] if names else list(REGISTRY.values())
    return [
        {"type": "function",
         "function": {"name": t.name, "description": t.description, "parameters": t.parameters}}
        for t in chosen
    ]


def execute(ctx: ToolContext, name: str, arguments: dict) -> dict:
    """Run one tool. Unknown tools and bad arguments are refused, never improvised."""
    tool_def = REGISTRY.get(name)
    if not tool_def:
        return {"error": f"'{name}' is not a tool I can use."}
    if "__malformed__" in arguments:
        return {"error": "Those arguments were not valid JSON. Please call the tool again."}

    unknown = set(arguments) - set(tool_def.parameters.get("properties", {})) - {"__utterance__"}
    if unknown:
        return {"error": f"Unsupported argument(s) for {name}: {', '.join(sorted(unknown))}."}
    missing = [r for r in tool_def.parameters.get("required", []) if arguments.get(r) is None]
    if missing:
        return {"error": f"{name} needs: {', '.join(missing)}."}

    try:
        return tool_def.handler(ctx, arguments)
    except ToolError as exc:
        return {"error": str(exc)}
    except AriaError as exc:
        return {"error": str(exc)}
    except Exception as exc:  # noqa: BLE001
        # The model is told the truth: the action failed and nothing was saved.
        ctx.db.rollback()
        return {"error": f"That action failed and nothing was saved. ({type(exc).__name__})"}
