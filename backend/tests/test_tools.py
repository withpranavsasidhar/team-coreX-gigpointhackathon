"""Tool layer: validation, resolution, and the guarantee that writes go through
the existing business engine rather than around it."""
import pytest

from app.models import EventType, InventoryEvent, Product
from app.services import tools
from app.services.event_engine import recompute_current_quantity


@pytest.fixture()
def ctx(db, business):
    return tools.ToolContext(db=db, business=business, source="aria")


# --- registry ------------------------------------------------------------

def test_every_tool_has_a_strict_schema():
    for name, tool in tools.REGISTRY.items():
        params = tool.parameters
        assert params["type"] == "object", name
        # Strict: unknown arguments must be rejectable.
        assert params.get("additionalProperties") is False, name
        assert isinstance(params.get("properties"), dict), name


def test_financial_and_destructive_tools_require_confirmation():
    for name in ("record_payment", "record_expense", "make_credit_sale",
                 "delete_product", "adjust_stock"):
        assert tools.REGISTRY[name].needs_confirmation, name


def test_read_tools_never_require_confirmation():
    for name in ("get_inventory", "get_customers", "get_alerts", "predict_stockout"):
        assert not tools.REGISTRY[name].needs_confirmation, name


# --- argument validation --------------------------------------------------

def test_unknown_tool_is_refused(ctx):
    result = tools.execute(ctx, "drop_all_tables", {})
    assert "not a tool" in result["error"]


def test_missing_required_argument_is_refused(ctx, catalogue):
    result = tools.execute(ctx, "add_stock", {"product": "Rice"})
    assert "needs" in result["error"] and "quantity" in result["error"]


def test_unsupported_argument_is_refused(ctx, catalogue):
    result = tools.execute(ctx, "add_stock",
                           {"product": "Rice", "quantity": 5, "sql": "DROP TABLE products"})
    assert "Unsupported argument" in result["error"]


def test_malformed_arguments_are_refused(ctx):
    result = tools.execute(ctx, "add_stock", {"__malformed__": "{{{"})
    assert "not valid JSON" in result["error"]


# --- product resolution ---------------------------------------------------

def test_unknown_product_is_reported_not_invented(ctx, catalogue):
    result = tools.execute(ctx, "add_stock", {"product": "Caviar", "quantity": 2})
    assert "couldn't find" in result["error"]
    assert "recorded" not in result


def test_ambiguous_product_asks_instead_of_guessing(ctx, db, business, catalogue):
    # Two plausible matches for "oil".
    db.add(Product(business_id=business.id, name="Engine Oil", base_unit="litres",
                   current_quantity=5, minimum_quantity=1, reorder_quantity=1, price=300))
    db.commit()
    result = tools.execute(ctx, "add_stock", {"product": "oil", "quantity": 2})
    assert "ambiguous" in result["error"].lower()
    assert "Cooking Oil" in result["error"] and "Engine Oil" in result["error"]


# --- writes go through the event engine ----------------------------------

def test_add_stock_creates_a_ledger_event_and_moves_cached_quantity(ctx, db, catalogue):
    before = float(catalogue["Rice"].current_quantity)
    result = tools.execute(ctx, "add_stock", {"product": "Rice", "quantity": 10})

    assert result["recorded"] is True
    assert result["resulting_quantity"] == before + 10

    events = db.query(InventoryEvent).filter_by(product_id=catalogue["Rice"].id).all()
    assert any(e.event_type == EventType.STOCK_IN and float(e.quantity) == 10 for e in events)
    # The invariant the whole system rests on.
    assert recompute_current_quantity(db, catalogue["Rice"]) == catalogue["Rice"].current_quantity


def test_sale_decreases_and_is_attributed(ctx, db, catalogue):
    before = float(catalogue["Coke"].current_quantity)
    result = tools.execute(ctx, "make_sale",
                           {"product": "Coke", "quantity": 12, "price": 480})
    assert result["resulting_quantity"] == before - 12
    assert result["applied_change"] == -12


def test_credit_sale_increases_customer_balance(ctx, db, catalogue, customer):
    tools.execute(ctx, "make_credit_sale",
                  {"product": "Coke", "quantity": 5, "price": 200, "customer": "Ramesh"})
    db.refresh(customer)
    assert float(customer.outstanding_credit) == 1200


def test_tool_writes_are_tagged_with_their_source(ctx, db, catalogue):
    tools.execute(ctx, "add_stock", {"product": "Rice", "quantity": 3})
    event = (db.query(InventoryEvent)
             .filter_by(product_id=catalogue["Rice"].id)
             .order_by(InventoryEvent.created_at.desc()).first())
    # Never disguised as demo or as something the user typed by hand.
    assert event.source == "aria"


def test_adjust_stock_records_only_the_difference(ctx, db, catalogue):
    rice = catalogue["Rice"]
    result = tools.execute(ctx, "adjust_stock", {"product": "Rice", "counted_quantity": 37})
    assert result["previous_quantity"] == 40
    assert result["resulting_quantity"] == 37
    last = (db.query(InventoryEvent).filter_by(product_id=rice.id)
            .order_by(InventoryEvent.created_at.desc()).first())
    assert last.event_type == EventType.ADJUSTMENT
    assert float(last.delta) == -3


def test_adjust_stock_is_a_no_op_when_the_count_matches(ctx, catalogue):
    result = tools.execute(ctx, "adjust_stock", {"product": "Rice", "counted_quantity": 40})
    assert result["recorded"] is False


# --- money ----------------------------------------------------------------

def test_payment_reduces_balance(ctx, db, customer):
    result = tools.execute(ctx, "record_payment", {"customer": "Ramesh", "amount": 400})
    assert result["remaining_balance"] == 600
    db.refresh(customer)
    assert float(customer.outstanding_credit) == 600


def test_overpayment_is_refused_with_the_same_rule_as_the_rest_route(ctx, customer):
    result = tools.execute(ctx, "record_payment", {"customer": "Ramesh", "amount": 5000})
    assert "more than the outstanding" in result["error"]


def test_negative_payment_is_refused(ctx, customer):
    result = tools.execute(ctx, "record_payment", {"customer": "Ramesh", "amount": -50})
    assert "greater than zero" in result["error"]


def test_expense_is_recorded(ctx, db, business):
    result = tools.execute(ctx, "record_expense",
                           {"amount": 2000, "category": "Transport", "note": "tempo"})
    assert result["recorded"] is True
    assert result["category"] == "transport"


# --- product CRUD ---------------------------------------------------------

def test_create_product_rejects_a_unit_the_system_does_not_know(ctx):
    result = tools.execute(ctx, "create_product",
                           {"name": "Sunrise Oil", "base_unit": "barrels"})
    assert "not a supported unit" in result["error"]


def test_create_product_uses_the_real_service(ctx, db, business):
    result = tools.execute(ctx, "create_product", {
        "name": "Sunrise Oil", "base_unit": "litres", "price": 145,
        "opening_stock": 12, "minimum_quantity": 5,
    })
    assert result["created"] is True
    product = db.query(Product).filter_by(name="Sunrise Oil").one()
    # Opening stock went in as a ledger event, not a bare column write.
    assert float(product.current_quantity) == 12
    assert recompute_current_quantity(db, product) == product.current_quantity


def test_duplicate_product_is_refused(ctx, catalogue):
    result = tools.execute(ctx, "create_product", {"name": "Rice", "base_unit": "bags"})
    assert "already exists" in result["error"]


def test_update_product_changes_only_named_fields(ctx, db, catalogue):
    result = tools.execute(ctx, "update_product", {"product": "Rice", "price": 1500})
    assert result["updated"] is True
    assert result["after"]["price"] == 1500
    assert result["after"]["minimum_quantity"] == result["before"]["minimum_quantity"]


def test_update_with_nothing_to_change_is_refused(ctx, catalogue):
    result = tools.execute(ctx, "update_product", {"product": "Rice"})
    assert "Nothing to change" in result["error"]


def test_delete_archives_and_keeps_history(ctx, db, catalogue):
    result = tools.execute(ctx, "delete_product", {"product": "Biscuits"})
    assert result["archived"] is True
    product = db.query(Product).filter_by(name="Biscuits").one()
    assert product.is_archived is True
    assert db.query(InventoryEvent).filter_by(product_id=product.id).count() > 0


# --- business memory ------------------------------------------------------

def test_unit_conversion_is_remembered_and_then_used_by_the_engine(ctx, db, catalogue):
    """The pack size the owner teaches must change real arithmetic, not just be stored."""
    result = tools.execute(ctx, "set_unit_conversion",
                           {"product": "Coke", "unit": "cartons", "equals_base_units": 24})
    assert result["remembered"] is True

    before = float(catalogue["Coke"].current_quantity)
    tools.execute(ctx, "add_stock", {"product": "Coke", "quantity": 2, "unit": "cartons"})
    db.refresh(catalogue["Coke"])
    assert float(catalogue["Coke"].current_quantity) == before + 48


def test_conversion_to_the_base_unit_is_refused(ctx, catalogue):
    result = tools.execute(ctx, "set_unit_conversion",
                           {"product": "Coke", "unit": "pieces", "equals_base_units": 1})
    assert "already counted" in result["error"]


# --- suppliers ------------------------------------------------------------

def test_supplier_is_created_once(ctx, db, business):
    first = tools.execute(ctx, "create_supplier", {"name": "Kumar", "supplies": "rice"})
    assert first["created"] is True
    again = tools.execute(ctx, "create_supplier", {"name": "kumar"})
    assert again["created"] is False


# --- reads report the database, nothing else ------------------------------

def test_get_product_reports_the_stored_quantity(ctx, catalogue):
    result = tools.execute(ctx, "get_product", {"product": "Rice"})
    assert result["current_quantity"] == float(catalogue["Rice"].current_quantity)


def test_stockout_prediction_is_labelled_as_an_estimate(ctx, catalogue):
    result = tools.execute(ctx, "predict_stockout", {"product": "Rice"})
    assert "Estimate" in result["basis"]
    assert result["risk"] in {"high", "medium", "low"}
