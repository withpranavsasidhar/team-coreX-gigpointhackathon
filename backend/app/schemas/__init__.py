from datetime import datetime, date
from typing import Optional, Dict, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.enums import EventType, PaymentStatus, SUPPORTED_UNITS


def _validate_unit(value: str) -> str:
    if value not in SUPPORTED_UNITS:
        raise ValueError(f"Unit must be one of: {', '.join(SUPPORTED_UNITS)}")
    return value


# ---------- Business ----------
class BusinessCreate(BaseModel):
    business_name: str = Field(min_length=1, max_length=200)
    business_type: str = "kirana"
    location: str = ""
    default_language: str = "en"


class BusinessOut(BaseModel):
    id: UUID
    business_name: str
    business_type: str
    location: str
    default_language: str

    model_config = {"from_attributes": True}


class BusinessOnboard(BaseModel):
    """Onboarding accepts either a chosen type or the sentence the owner spoke."""

    business_name: str = Field(min_length=1, max_length=200)
    business_type: Optional[str] = None
    spoken_description: Optional[str] = None   # "I run a bakery"
    location: str = ""
    default_language: str = "en"
    seed_catalogue: bool = True
    seed_demo_history: bool = False


class BusinessSummaryOut(BaseModel):
    id: UUID
    business_name: str
    business_type: str
    type_label: str
    type_emoji: str
    descriptor: str
    location: str
    default_language: str
    units: List[str]
    categories: List[str]
    sample_utterances: List[str]
    product_count: int
    event_count: int
    is_configured: bool


class BusinessTypeOut(BaseModel):
    key: str
    label: str
    descriptor: str
    emoji: str
    units: List[str]
    categories: List[str]
    sample_utterances: List[str]
    starter_product_count: int
    starter_product_names: List[str]


# ---------- Suppliers ----------
class SupplierCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    phone: str = ""
    supplies: str = ""
    lead_time_days: float = Field(default=7, ge=0, le=365)


class SupplierOut(BaseModel):
    id: UUID
    name: str
    phone: str
    supplies: str
    lead_time_days: float

    model_config = {"from_attributes": True}


# ---------- Money ----------
class PaymentCreate(BaseModel):
    customer_id: UUID
    amount: float = Field(gt=0)
    note: str = ""


class PaymentOut(BaseModel):
    id: UUID
    customer_id: UUID
    amount: float
    note: str
    occurred_at: datetime

    model_config = {"from_attributes": True}


class ExpenseCreate(BaseModel):
    category: str = "general"
    amount: float = Field(gt=0)
    note: str = ""


class ExpenseOut(BaseModel):
    id: UUID
    category: str
    amount: float
    note: str
    occurred_at: datetime

    model_config = {"from_attributes": True}


# ---------- Products ----------
class UnitConversionIn(BaseModel):
    unit_name: str
    factor_to_base_unit: float = Field(gt=0)

    _check_unit = field_validator("unit_name")(_validate_unit)


class UnitConversionOut(UnitConversionIn):
    id: UUID
    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: str = "general"
    base_unit: str = "pieces"
    opening_stock: float = Field(default=0, ge=0)
    minimum_quantity: float = Field(default=0, ge=0)
    reorder_quantity: float = Field(default=0, ge=0)
    price: float = Field(default=0, ge=0)
    conversions: List[UnitConversionIn] = []

    _check_unit = field_validator("base_unit")(_validate_unit)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    category: Optional[str] = None
    base_unit: Optional[str] = None
    minimum_quantity: Optional[float] = Field(default=None, ge=0)
    reorder_quantity: Optional[float] = Field(default=None, ge=0)
    price: Optional[float] = Field(default=None, ge=0)
    conversions: Optional[List[UnitConversionIn]] = None

    @field_validator("base_unit")
    @classmethod
    def check_unit(cls, v):
        return _validate_unit(v) if v is not None else v


class ProductOut(BaseModel):
    id: UUID
    business_id: UUID
    name: str
    category: str
    base_unit: str
    current_quantity: float
    minimum_quantity: float
    reorder_quantity: float
    price: float
    is_archived: bool
    conversions: List[UnitConversionOut] = []

    model_config = {"from_attributes": True}


class ProductStatusOut(ProductOut):
    """Product plus the derived signals the inventory screens need."""

    status: str  # healthy | low | critical | out_of_stock
    avg_daily_usage: float
    estimated_days_to_stockout: Optional[float]
    last_movement_at: Optional[datetime]


# ---------- Customers ----------
class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    phone: str = ""


class CustomerOut(BaseModel):
    id: UUID
    name: str
    phone: str
    outstanding_credit: float

    model_config = {"from_attributes": True}


# ---------- Events ----------
class EventCreate(BaseModel):
    product_id: UUID
    event_type: EventType
    quantity: float
    unit: Optional[str] = None
    customer_name: Optional[str] = None
    price: Optional[float] = None
    payment_status: PaymentStatus = PaymentStatus.NA
    due_date: Optional[date] = None
    occurred_at: Optional[datetime] = None
    source: str = "manual"
    original_text: str = ""
    normalized_text: str = ""
    detected_language: str = ""
    confidence: float = 1.0

    @field_validator("unit")
    @classmethod
    def check_unit(cls, v):
        return _validate_unit(v) if v is not None else v

    @field_validator("quantity")
    @classmethod
    def non_zero(cls, v):
        if v == 0:
            raise ValueError("Quantity cannot be zero.")
        return v


class EventOut(BaseModel):
    id: UUID
    product_id: UUID
    product_name: Optional[str] = None
    customer_id: Optional[UUID] = None
    customer_name: Optional[str] = None
    event_type: EventType
    quantity: float
    unit: str
    delta: float
    price: Optional[float]
    payment_status: PaymentStatus
    due_date: Optional[date]
    source: str
    original_text: str
    normalized_text: str
    detected_language: str
    confidence: float
    occurred_at: datetime

    model_config = {"from_attributes": True}


class MovementBreakdown(BaseModel):
    event_type: EventType
    net_change: float
    count: int


class ProductHistoryOut(BaseModel):
    product: ProductStatusOut
    window_days: int
    opening_balance: float
    total_in: float
    total_out: float
    breakdown: List[MovementBreakdown]
    events: List[EventOut]


# ---------- Voice ----------
class VoiceProcessRequest(BaseModel):
    transcript: str = Field(min_length=1, max_length=500)
    language_hint: Optional[str] = None
    reply_language: Optional[str] = None


class ProductCandidateOut(BaseModel):
    product_id: UUID
    name: str
    base_unit: str
    current_quantity: float
    score: float


class VoiceInterpretationOut(BaseModel):
    """recorded | needs_confirmation | needs_clarification | rejected"""

    status: str
    message: str
    transcript: str

    event_type: Optional[EventType] = None
    product_id: Optional[UUID] = None
    product_name: Optional[str] = None
    candidates: List[ProductCandidateOut] = []
    quantity: Optional[float] = None
    unit: Optional[str] = None
    customer_name: Optional[str] = None
    price: Optional[float] = None
    payment_status: PaymentStatus = PaymentStatus.NA
    due_date: Optional[date] = None

    confidence: float = 0.0
    model_confidence: float = 0.0
    match_confidence: float = 0.0
    normalized_text: str = ""
    detected_language: str = ""
    reply_language: str = "en"
    provider: str = ""
    notes: List[str] = []

    created_event: Optional[EventOut] = None
    resulting_quantity: Optional[float] = None
    resulting_unit: Optional[str] = None


class VoiceCapabilitiesOut(BaseModel):
    ai_provider: str
    llm_enabled: bool
    stt_provider: str
    stt_is_client_side: bool
    confidence_threshold: float
    clarification_threshold: float
    degraded_reason: Optional[str] = None
    supported_languages: List[str] = []
    # What the owner is actually talking to, reported plainly.
    agent_available: bool = False
    agent_model: Optional[str] = None
    translation_provider: str = "none"
    translation_available: bool = False


# ---------- Business intelligence ----------
class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=400)
    reply_language: Optional[str] = None


class QueryAnswerOut(BaseModel):
    intent: str
    answer: str
    visual: str
    items: List[dict] = []
    facts: Dict[str, object] = {}
    product_id: Optional[UUID] = None
    product_name: Optional[str] = None
    window_label: Optional[str] = None
    grounded_by: str = "template"


class InsightsOut(BaseModel):
    alerts: List[dict]
    reorder_recommendations: List[dict]
    unusual_movement: List[dict]
    fast_moving: List[dict]
    slow_moving: List[dict]
