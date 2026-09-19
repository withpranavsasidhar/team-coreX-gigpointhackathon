import enum


class EventType(str, enum.Enum):
    STOCK_IN = "STOCK_IN"
    PURCHASE = "PURCHASE"
    RETURN = "RETURN"
    SALE = "SALE"
    STOCK_OUT = "STOCK_OUT"
    CREDIT_SALE = "CREDIT_SALE"
    DAMAGE = "DAMAGE"
    LOSS = "LOSS"
    ADJUSTMENT = "ADJUSTMENT"


INCREASING_EVENTS = {EventType.STOCK_IN, EventType.PURCHASE, EventType.RETURN}
DECREASING_EVENTS = {
    EventType.SALE,
    EventType.STOCK_OUT,
    EventType.CREDIT_SALE,
    EventType.DAMAGE,
    EventType.LOSS,
}
# ADJUSTMENT carries its own sign and is applied as given.

# Events that represent real consumption, used for usage-rate and stockout math.
CONSUMPTION_EVENTS = {
    EventType.SALE,
    EventType.STOCK_OUT,
    EventType.CREDIT_SALE,
    EventType.DAMAGE,
    EventType.LOSS,
}


class PaymentStatus(str, enum.Enum):
    PAID = "PAID"
    CREDIT = "CREDIT"
    NA = "NA"


class Unit(str, enum.Enum):
    PIECES = "pieces"
    KG = "kg"
    GRAMS = "grams"
    LITRES = "litres"
    ML = "ml"
    BAGS = "bags"
    CARTONS = "cartons"
    BOXES = "boxes"
    PACKETS = "packets"
    DOZENS = "dozens"
    QUINTALS = "quintals"
    # Trade-specific units: bakery trays, vegetable crates, hardware lengths,
    # clothing pairs. See services/business_context for who uses what.
    CRATES = "crates"
    TRAYS = "trays"
    METERS = "meters"
    ROLLS = "rolls"
    PAIRS = "pairs"
    SETS = "sets"
    BUNCHES = "bunches"
    REAMS = "reams"


SUPPORTED_UNITS = [u.value for u in Unit]


class AlertType(str, enum.Enum):
    LOW_STOCK = "LOW_STOCK"
    STOCKOUT_RISK = "STOCKOUT_RISK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    DISCREPANCY = "DISCREPANCY"
    UNUSUAL_MOVEMENT = "UNUSUAL_MOVEMENT"


class Severity(str, enum.Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
