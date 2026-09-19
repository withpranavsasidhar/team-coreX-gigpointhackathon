from decimal import Decimal

from app.models import Product


def to_decimal(value) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def conversion_factor(product: Product, unit: str | None) -> Decimal:
    """Base units represented by one `unit` of this product.

    Falls back to 1 when the unit is the base unit or has no configured rule —
    per the Phase 2 rule, an unmapped unit is trusted as-is rather than rejected.
    """
    if not unit or unit == product.base_unit:
        return Decimal(1)
    for rule in product.conversions:
        if rule.unit_name == unit:
            return to_decimal(rule.factor_to_base_unit)
    return Decimal(1)


def to_base_units(product: Product, quantity, unit: str | None) -> Decimal:
    return to_decimal(quantity) * conversion_factor(product, unit)
