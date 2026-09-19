"""The Business Context Engine.

One application, many trades. A kirana store, a bakery and a hardware shop run
the same event ledger, the same voice pipeline and the same reasoning engine —
what changes is the *context*: which units are natural, what the shelves are
called, and which words the owner uses for the things they sell.

This module is data, not logic. Supporting a new trade means adding an entry
here; no pipeline, router or component changes.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StarterProduct:
    name: str
    base_unit: str
    category: str
    minimum_quantity: float
    reorder_quantity: float
    price: float
    # "1 <unit> = n base units" rules the trade takes for granted.
    conversions: tuple[tuple[str, float], ...] = ()


@dataclass(frozen=True)
class BusinessType:
    key: str
    label: str
    descriptor: str          # how the owner would describe the shop out loud
    emoji: str
    units: tuple[str, ...]   # offered first in pickers, in order of naturalness
    categories: tuple[str, ...]
    sample_utterances: tuple[str, ...]
    starter_products: tuple[StarterProduct, ...]
    # Trade words that mean a product, merged into the matcher's alias table.
    product_aliases: dict[str, tuple[str, ...]] = field(default_factory=dict)


def _p(name, unit, category, minimum, reorder, price, conversions=()):
    return StarterProduct(name, unit, category, minimum, reorder, price, conversions)


BUSINESS_TYPES: dict[str, BusinessType] = {
    "kirana": BusinessType(
        key="kirana",
        label="Kirana / General Store",
        descriptor="a kirana store",
        emoji="🏪",
        units=("kg", "litres", "bags", "pieces", "packets", "cartons", "dozens", "grams"),
        categories=("staples", "oils", "snacks", "beverages", "dairy", "household"),
        sample_utterances=(
            "Rendu cartons Coke vachayi",
            "Ramesh took two boxes of oil, he'll pay Friday",
            "Rice stock entha undi?",
        ),
        starter_products=(
            _p("Rice", "bags", "staples", 15, 40, 1450, (("quintals", 2.0),)),
            _p("Wheat", "kg", "staples", 40, 120, 38),
            _p("Sugar", "kg", "staples", 25, 75, 45),
            _p("Cooking Oil", "litres", "oils", 20, 60, 145, (("boxes", 15.0),)),
            _p("Tea Powder", "kg", "staples", 5, 15, 420),
            _p("Biscuits", "pieces", "snacks", 150, 300, 10, (("cartons", 120.0),)),
            _p("Maggi", "pieces", "snacks", 72, 144, 14, (("cartons", 48.0),)),
            _p("Coke", "pieces", "beverages", 60, 120, 40, (("cartons", 24.0),)),
            _p("Milk", "litres", "dairy", 15, 60, 54, (("crates", 12.0),)),
            _p("Eggs", "pieces", "dairy", 60, 180, 6, (("trays", 30.0),)),
        ),
        product_aliases={
            "Cooking Oil": ("oil", "nune", "నూనె", "तेल", "tel", "refined"),
            "Tea Powder": ("tea", "chai", "టీ", "चाय"),
            "Coke": ("cola", "cold drink", "soft drink", "కోక్"),
        },
    ),
    "bakery": BusinessType(
        key="bakery",
        label="Bakery",
        descriptor="a bakery",
        emoji="🥐",
        units=("pieces", "trays", "kg", "boxes", "packets", "dozens", "grams"),
        categories=("bread", "cakes", "savouries", "ingredients", "beverages"),
        sample_utterances=(
            "Twenty bread loaves came in",
            "Sold three trays of puffs",
            "Maida 10 kg vachindi",
        ),
        starter_products=(
            _p("Bread Loaf", "pieces", "bread", 20, 60, 45),
            _p("Bun", "pieces", "bread", 40, 120, 12, (("trays", 24.0),)),
            _p("Veg Puff", "pieces", "savouries", 30, 90, 25, (("trays", 30.0),)),
            _p("Cream Cake", "pieces", "cakes", 5, 15, 450),
            _p("Cake Rusk", "packets", "savouries", 20, 60, 60),
            _p("Maida", "kg", "ingredients", 25, 75, 42),
            _p("Butter", "kg", "ingredients", 5, 15, 520),
            _p("Sugar", "kg", "ingredients", 20, 60, 45),
            _p("Eggs", "pieces", "ingredients", 90, 270, 6, (("trays", 30.0),)),
            _p("Fresh Cream", "litres", "ingredients", 4, 12, 280),
        ),
        product_aliases={
            "Bread Loaf": ("bread", "loaf", "బ్రెడ్", "ब्रेड"),
            "Veg Puff": ("puff", "puffs", "పఫ్"),
            "Maida": ("flour", "పిండి", "आटा", "pindi"),
        },
    ),
    "vegetable": BusinessType(
        key="vegetable",
        label="Vegetable / Fruit Shop",
        descriptor="a vegetable shop",
        emoji="🥬",
        units=("kg", "crates", "bags", "pieces", "bunches", "grams", "quintals"),
        categories=("vegetables", "leafy", "fruits", "roots"),
        sample_utterances=(
            "Kal 20 kg tomato vachindi",
            "Sold 5 kg onions",
            "Two crates of banana came in",
        ),
        starter_products=(
            _p("Tomato", "kg", "vegetables", 20, 60, 30, (("crates", 25.0),)),
            _p("Onion", "kg", "roots", 30, 90, 35, (("bags", 50.0),)),
            _p("Potato", "kg", "roots", 30, 90, 28, (("bags", 50.0),)),
            _p("Brinjal", "kg", "vegetables", 10, 30, 40),
            _p("Carrot", "kg", "roots", 10, 30, 55),
            _p("Green Chilli", "kg", "vegetables", 5, 15, 60),
            _p("Coriander", "bunches", "leafy", 20, 60, 10),
            _p("Curry Leaves", "bunches", "leafy", 15, 45, 5),
            _p("Banana", "dozens", "fruits", 10, 30, 60),
            _p("Cabbage", "pieces", "vegetables", 15, 45, 30),
        ),
        product_aliases={
            "Tomato": ("tomatoes", "టమాటా", "टमाटर", "tamata"),
            "Onion": ("onions", "ఉల్లిపాయ", "प्याज", "ullipaya", "pyaz"),
            "Potato": ("potatoes", "బంగాళాదుంప", "आलू", "aloo"),
            "Green Chilli": ("chilli", "chillies", "మిర్చి", "मिर्च", "mirchi"),
        },
    ),
    "hardware": BusinessType(
        key="hardware",
        label="Hardware / Construction Material",
        descriptor="a hardware shop",
        emoji="🔩",
        units=("pieces", "boxes", "packets", "meters", "bags", "kg", "rolls"),
        categories=("cement", "electrical", "plumbing", "fasteners", "paint", "tools"),
        sample_utterances=(
            "Fifty bags of cement arrived",
            "Sold 20 meters of wire",
            "Two boxes of screws came in",
        ),
        starter_products=(
            _p("Cement", "bags", "cement", 30, 100, 410),
            _p("Steel Rod 8mm", "pieces", "cement", 25, 75, 480),
            _p("Wall Paint", "litres", "paint", 20, 60, 320, (("boxes", 20.0),)),
            _p("Nails", "kg", "fasteners", 10, 30, 90),
            _p("Screws", "boxes", "fasteners", 15, 45, 180),
            _p("PVC Pipe", "meters", "plumbing", 50, 150, 85),
            _p("Electrical Wire", "meters", "electrical", 100, 300, 28, (("rolls", 90.0),)),
            _p("Switch", "pieces", "electrical", 40, 120, 65),
            _p("Door Hinge", "pieces", "fasteners", 30, 90, 45),
            _p("Insulation Tape", "pieces", "electrical", 50, 150, 12, (("boxes", 10.0),)),
        ),
        product_aliases={
            "Cement": ("simenti", "సిమెంట్", "सीमेंट"),
            "Electrical Wire": ("wire", "cable", "వైర్", "तार"),
            "PVC Pipe": ("pipe", "pipes", "పైపు", "पाइप"),
        },
    ),
    "clothing": BusinessType(
        key="clothing",
        label="Clothing / Fashion Store",
        descriptor="a clothing store",
        emoji="👗",
        units=("pieces", "sets", "pairs", "boxes", "dozens"),
        categories=("menswear", "womenswear", "kidswear", "accessories"),
        sample_utterances=(
            "Ten cotton shirts came in",
            "Sold two sarees today",
            "Five pairs of socks sold",
        ),
        starter_products=(
            _p("Cotton Shirt", "pieces", "menswear", 15, 45, 650),
            _p("T-Shirt", "pieces", "menswear", 20, 60, 380),
            _p("Jeans", "pieces", "menswear", 12, 36, 1100),
            _p("Saree", "pieces", "womenswear", 15, 45, 1800),
            _p("Kurta", "pieces", "womenswear", 15, 45, 750),
            _p("Leggings", "pieces", "womenswear", 20, 60, 320),
            _p("Dupatta", "pieces", "accessories", 18, 54, 280),
            _p("Kids Frock", "pieces", "kidswear", 12, 36, 480),
            _p("Towel", "pieces", "accessories", 20, 60, 220),
            _p("Socks", "pairs", "accessories", 30, 90, 90, (("dozens", 12.0),)),
        ),
        product_aliases={
            "Cotton Shirt": ("shirt", "shirts", "చొక్కా", "कमीज़"),
            "Saree": ("sarees", "చీర", "साड़ी", "cheera"),
        },
    ),
    "dairy": BusinessType(
        key="dairy",
        label="Dairy Shop",
        descriptor="a dairy shop",
        emoji="🥛",
        units=("litres", "kg", "packets", "pieces", "crates", "ml", "grams"),
        categories=("milk", "curd", "fats", "sweets"),
        sample_utterances=(
            "Fifty litres of milk came in",
            "Sold 10 packets of curd",
            "Paneer 2 kg vachindi",
        ),
        starter_products=(
            _p("Milk", "litres", "milk", 40, 120, 54, (("crates", 12.0),)),
            _p("Curd", "kg", "curd", 15, 45, 60, (("packets", 0.4),)),
            _p("Butter", "kg", "fats", 5, 15, 520),
            _p("Ghee", "litres", "fats", 6, 18, 620),
            _p("Paneer", "kg", "fats", 4, 12, 380),
            _p("Lassi", "pieces", "curd", 24, 72, 25, (("crates", 24.0),)),
            _p("Buttermilk", "litres", "curd", 10, 30, 30),
            _p("Cheese", "kg", "fats", 3, 9, 480),
            _p("Fresh Cream", "litres", "fats", 4, 12, 280),
            _p("Khoa", "kg", "sweets", 3, 9, 420),
        ),
        product_aliases={
            "Milk": ("paalu", "పాలు", "दूध", "doodh"),
            "Curd": ("perugu", "పెరుగు", "दही", "dahi", "yogurt"),
            "Ghee": ("neyyi", "నెయ్యి", "घी"),
        },
    ),
    "restaurant": BusinessType(
        key="restaurant",
        label="Restaurant / Cloud Kitchen",
        descriptor="a restaurant",
        emoji="🍽",
        units=("kg", "litres", "pieces", "packets", "crates", "trays", "grams"),
        categories=("grains", "proteins", "vegetables", "dairy", "supplies"),
        sample_utterances=(
            "Ten kg chicken came in",
            "Used 5 kg onions today",
            "One gas cylinder finished",
        ),
        starter_products=(
            _p("Rice", "kg", "grains", 50, 150, 62),
            _p("Chicken", "kg", "proteins", 15, 45, 240),
            _p("Paneer", "kg", "proteins", 5, 15, 380),
            _p("Onion", "kg", "vegetables", 25, 75, 35),
            _p("Tomato", "kg", "vegetables", 20, 60, 30),
            _p("Cooking Oil", "litres", "supplies", 20, 60, 145),
            _p("Garam Masala", "kg", "supplies", 2, 6, 780),
            _p("Curd", "kg", "dairy", 10, 30, 60),
            _p("Wheat Flour", "kg", "grains", 30, 90, 42),
            _p("Gas Cylinder", "pieces", "supplies", 2, 4, 1850),
        ),
        product_aliases={
            "Chicken": ("kodi", "కోడి", "मुर्गा", "murga"),
            "Wheat Flour": ("atta", "आटा", "గోధుమ పిండి"),
        },
    ),
    "mobile": BusinessType(
        key="mobile",
        label="Mobile & Accessories",
        descriptor="a mobile accessories shop",
        emoji="📱",
        units=("pieces", "boxes", "packets", "sets"),
        categories=("charging", "audio", "protection", "storage"),
        sample_utterances=(
            "Twenty chargers came in",
            "Sold three tempered glasses",
            "Two power banks left",
        ),
        starter_products=(
            _p("Charger", "pieces", "charging", 20, 60, 320, (("boxes", 20.0),)),
            _p("USB Cable", "pieces", "charging", 30, 90, 150, (("boxes", 25.0),)),
            _p("Earphones", "pieces", "audio", 20, 60, 280),
            _p("Bluetooth Speaker", "pieces", "audio", 6, 18, 950),
            _p("Back Cover", "pieces", "protection", 40, 120, 180),
            _p("Tempered Glass", "pieces", "protection", 40, 120, 120),
            _p("Power Bank", "pieces", "charging", 8, 24, 1250),
            _p("Memory Card", "pieces", "storage", 15, 45, 480),
            _p("Car Charger", "pieces", "charging", 10, 30, 350),
            _p("Phone Stand", "pieces", "protection", 15, 45, 160),
        ),
        product_aliases={
            "Tempered Glass": ("screen guard", "glass", "tempered"),
            "Back Cover": ("cover", "case", "కవర్"),
        },
    ),
    "stationery": BusinessType(
        key="stationery",
        label="Stationery / Book Store",
        descriptor="a stationery shop",
        emoji="✏️",
        units=("pieces", "packets", "boxes", "dozens", "reams"),
        categories=("paper", "writing", "office", "school"),
        sample_utterances=(
            "Fifty notebooks came in",
            "Sold two reams of A4 paper",
            "One box of pens finished",
        ),
        starter_products=(
            _p("Notebook", "pieces", "school", 50, 150, 45, (("dozens", 12.0),)),
            _p("Ball Pen", "pieces", "writing", 100, 300, 10, (("boxes", 50.0),)),
            _p("Pencil", "pieces", "writing", 100, 300, 5, (("boxes", 50.0),)),
            _p("Eraser", "pieces", "writing", 60, 180, 5),
            _p("A4 Paper", "reams", "paper", 10, 30, 320),
            _p("File Folder", "pieces", "office", 30, 90, 35),
            _p("Marker", "pieces", "writing", 25, 75, 45),
            _p("Glue Stick", "pieces", "office", 20, 60, 30),
            _p("Stapler", "pieces", "office", 10, 30, 120),
            _p("Chart Paper", "pieces", "paper", 50, 150, 12),
        ),
        product_aliases={
            "Ball Pen": ("pen", "pens", "పెన్", "कलम"),
            "A4 Paper": ("paper", "a4", "xerox paper"),
        },
    ),
}

DEFAULT_TYPE = "kirana"

# Every unit any trade uses, so the picker and validator agree with the data.
ALL_UNITS: tuple[str, ...] = tuple(
    dict.fromkeys(unit for bt in BUSINESS_TYPES.values() for unit in bt.units)
)


def get_type(business_type: str | None) -> BusinessType:
    """Resolve a stored business_type string; unknown trades fall back sanely."""
    return BUSINESS_TYPES.get((business_type or "").strip().lower(), BUSINESS_TYPES[DEFAULT_TYPE])


def units_for(business_type: str | None) -> list[str]:
    """Trade-natural units first, then everything else the system understands."""
    natural = list(get_type(business_type).units)
    return natural + [u for u in ALL_UNITS if u not in natural]


def aliases_for(business_type: str | None) -> dict[str, tuple[str, ...]]:
    return dict(get_type(business_type).product_aliases)


def describe_types() -> list[dict]:
    """The onboarding menu: enough for a card, not the whole catalogue."""
    return [
        {
            "key": bt.key,
            "label": bt.label,
            "descriptor": bt.descriptor,
            "emoji": bt.emoji,
            "units": list(bt.units),
            "categories": list(bt.categories),
            "sample_utterances": list(bt.sample_utterances),
            "starter_product_count": len(bt.starter_products),
            "starter_product_names": [p.name for p in bt.starter_products[:5]],
        }
        for bt in BUSINESS_TYPES.values()
    ]


def match_type_from_speech(text: str) -> str | None:
    """Map "I run a bakery" / "vegetable shop" onto a business type key.

    Deliberately conservative: an unrecognised trade returns None so the caller
    can ask rather than guess a whole catalogue wrong.
    """
    lowered = (text or "").lower()
    if not lowered.strip():
        return None

    # Longest, most specific markers first so "cloud kitchen" beats "kitchen".
    markers: list[tuple[str, str]] = [
        ("cloud kitchen", "restaurant"), ("restaurant", "restaurant"), ("hotel", "restaurant"),
        ("tiffin", "restaurant"), ("mess", "restaurant"), ("canteen", "restaurant"),
        ("bakery", "bakery"), ("baker", "bakery"), ("cake", "bakery"), ("bread", "bakery"),
        ("vegetable", "vegetable"), ("veggie", "vegetable"), ("fruit", "vegetable"),
        ("sabzi", "vegetable"), ("kuragayalu", "vegetable"),
        ("hardware", "hardware"), ("construction", "hardware"), ("cement", "hardware"),
        ("paint", "hardware"), ("electrical", "hardware"), ("plumbing", "hardware"),
        ("clothing", "clothing"), ("cloth", "clothing"), ("garment", "clothing"),
        ("fashion", "clothing"), ("boutique", "clothing"), ("saree", "clothing"),
        ("textile", "clothing"), ("dress", "clothing"),
        ("dairy", "dairy"), ("milk", "dairy"), ("paal", "dairy"), ("curd", "dairy"),
        ("mobile", "mobile"), ("phone", "mobile"), ("accessor", "mobile"),
        ("electronics", "mobile"),
        ("stationery", "stationery"), ("stationary", "stationery"), ("book", "stationery"),
        ("xerox", "stationery"),
        ("kirana", "kirana"), ("grocery", "kirana"), ("general store", "kirana"),
        ("provision", "kirana"), ("super market", "kirana"), ("supermarket", "kirana"),
        ("departmental", "kirana"),
    ]
    for marker, key in markers:
        if marker in lowered:
            return key
    return None
