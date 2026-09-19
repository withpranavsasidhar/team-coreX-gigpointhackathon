"""Suppliers and expenses — the parts of running a shop that are not stock."""
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.dependencies import require_business
from app.core.exceptions import NotFound
from app.database import get_db
from app.models import Business, Expense, Payment, Supplier
from app.schemas import ExpenseCreate, ExpenseOut, SupplierCreate, SupplierOut
from app.services.units import to_decimal

router = APIRouter(tags=["operations"])


# ---------- Suppliers ----------
@router.post("/suppliers", response_model=SupplierOut, status_code=201)
def create_supplier(
    payload: SupplierCreate,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    supplier = Supplier(
        business_id=business.id,
        name=payload.name.strip(),
        phone=payload.phone,
        supplies=payload.supplies,
        lead_time_days=to_decimal(payload.lead_time_days),
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get("/suppliers", response_model=list[SupplierOut])
def list_suppliers(
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    return list(
        db.execute(
            select(Supplier).where(Supplier.business_id == business.id).order_by(Supplier.name)
        ).scalars()
    )


@router.delete("/suppliers/{supplier_id}", status_code=204)
def delete_supplier(
    supplier_id: UUID,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    supplier = db.execute(
        select(Supplier).where(Supplier.id == supplier_id, Supplier.business_id == business.id)
    ).scalar_one_or_none()
    if not supplier:
        raise NotFound("That supplier does not exist.")
    db.delete(supplier)
    db.commit()


# ---------- Expenses ----------
@router.post("/expenses", response_model=ExpenseOut, status_code=201)
def create_expense(
    payload: ExpenseCreate,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    expense = Expense(
        business_id=business.id,
        category=payload.category.strip() or "general",
        amount=to_decimal(payload.amount),
        note=payload.note,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/expenses", response_model=list[ExpenseOut])
def list_expenses(
    days: int = 30,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(days=days)
    return list(
        db.execute(
            select(Expense)
            .where(Expense.business_id == business.id, Expense.occurred_at >= since)
            .order_by(Expense.occurred_at.desc())
        ).scalars()
    )


# ---------- Money summary ----------
@router.get("/money")
def money_summary(
    days: int = 30,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    """Cash in, cash out and credit outstanding for the period."""
    since = datetime.utcnow() - timedelta(days=days)

    expenses_total = db.execute(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.business_id == business.id, Expense.occurred_at >= since
        )
    ).scalar_one()

    payments_total = db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.business_id == business.id, Payment.occurred_at >= since
        )
    ).scalar_one()

    by_category = db.execute(
        select(Expense.category, func.sum(Expense.amount))
        .where(Expense.business_id == business.id, Expense.occurred_at >= since)
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
    ).all()

    return {
        "window_days": days,
        "expenses_total": float(expenses_total),
        "payments_received": float(payments_total),
        "expenses_by_category": [
            {"category": category, "amount": float(amount)} for category, amount in by_category
        ],
    }
