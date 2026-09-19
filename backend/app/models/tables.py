import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Numeric, DateTime, Date, ForeignKey, Enum, Text, Boolean,
    UniqueConstraint, Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import EventType, PaymentStatus, AlertType, Severity


def _uuid_pk():
    return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class Business(Base):
    __tablename__ = "businesses"

    id = _uuid_pk()
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    business_name = Column(String(200), nullable=False)
    business_type = Column(String(50), default="kirana")
    location = Column(String(200), default="")
    default_language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    products = relationship("Product", back_populates="business")
    customers = relationship("Customer", back_populates="business")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_businesses")


class User(Base):
    __tablename__ = "users"

    id = _uuid_pk()
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=True)
    name = Column(String(120), nullable=False)
    phone = Column(String(30), default="", index=True)
    password_hash = Column(String(255), default="")
    email = Column(String(200), default="")
    preferred_language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owned_businesses = relationship("Business", foreign_keys=[Business.owner_id], back_populates="owner")



class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("business_id", "name", name="uq_product_name_per_business"),
    )

    id = _uuid_pk()
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(80), default="general")
    base_unit = Column(String(20), nullable=False, default="pieces")
    # Cached projection of SUM(inventory_events.delta); see services/inventory_service.
    current_quantity = Column(Numeric(14, 3), nullable=False, default=0)
    minimum_quantity = Column(Numeric(14, 3), nullable=False, default=0)
    reorder_quantity = Column(Numeric(14, 3), nullable=False, default=0)
    price = Column(Numeric(12, 2), nullable=False, default=0)
    is_archived = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    business = relationship("Business", back_populates="products")
    conversions = relationship(
        "UnitConversion", back_populates="product", cascade="all, delete-orphan"
    )
    events = relationship("InventoryEvent", back_populates="product")


class UnitConversion(Base):
    """How many base units one alternate unit represents, e.g. 1 carton = 24 pieces."""

    __tablename__ = "unit_conversions"
    __table_args__ = (
        UniqueConstraint("product_id", "unit_name", name="uq_conversion_per_product_unit"),
    )

    id = _uuid_pk()
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    unit_name = Column(String(20), nullable=False)
    factor_to_base_unit = Column(Numeric(14, 4), nullable=False)

    product = relationship("Product", back_populates="conversions")


class Customer(Base):
    __tablename__ = "customers"

    id = _uuid_pk()
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    phone = Column(String(30), default="")
    outstanding_credit = Column(Numeric(12, 2), nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    business = relationship("Business", back_populates="customers")


class InventoryEvent(Base):
    """Append-only business event ledger. Never updated or deleted after insert."""

    __tablename__ = "inventory_events"
    __table_args__ = (
        Index("ix_events_business_time", "business_id", "occurred_at"),
        Index("ix_events_product_time", "product_id", "occurred_at"),
    )

    id = _uuid_pk()
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)

    event_type = Column(Enum(EventType, name="event_type"), nullable=False)
    # Magnitude as spoken/entered, in `unit`.
    quantity = Column(Numeric(14, 3), nullable=False)
    unit = Column(String(20), nullable=False)
    # Signed change actually applied to stock, always in the product's base unit.
    delta = Column(Numeric(14, 3), nullable=False)

    price = Column(Numeric(12, 2), nullable=True)
    payment_status = Column(Enum(PaymentStatus, name="payment_status"), default=PaymentStatus.NA)
    due_date = Column(Date, nullable=True)

    source = Column(String(30), nullable=False, default="manual")  # voice | text | manual | opening
    original_text = Column(Text, default="")
    normalized_text = Column(Text, default="")
    detected_language = Column(String(20), default="")
    confidence = Column(Numeric(4, 3), nullable=False, default=1)

    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="events")
    customer = relationship("Customer")


class Supplier(Base):
    """Who stock comes from. Purchases can be attributed to a supplier."""

    __tablename__ = "suppliers"

    id = _uuid_pk()
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)
    name = Column(String(160), nullable=False)
    phone = Column(String(30), default="")
    supplies = Column(String(300), default="")   # free text: "dairy, bakery items"
    lead_time_days = Column(Numeric(5, 1), nullable=False, default=7)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Payment(Base):
    """A customer settling credit. Money, not stock — so not an inventory event."""

    __tablename__ = "payments"

    id = _uuid_pk()
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    note = Column(String(300), default="")
    source = Column(String(30), nullable=False, default="manual")
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("Customer")


class Expense(Base):
    """Money out that is not stock: rent, power, transport, wages."""

    __tablename__ = "expenses"

    id = _uuid_pk()
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)
    category = Column(String(60), nullable=False, default="general")
    amount = Column(Numeric(12, 2), nullable=False)
    note = Column(String(300), default="")
    source = Column(String(30), nullable=False, default="manual")
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AIInteraction(Base):
    """Every turn the assistant took, whether or not it changed anything.

    This is what makes the assistant auditable: what was heard, what it was
    understood to mean, how sure the system was, and what it did about it.
    It also supplies the short-term context that lets "actually, make it 15"
    refer to the thing just recorded.
    """

    __tablename__ = "ai_interactions"
    __table_args__ = (
        Index("ix_interactions_business_time", "business_id", "created_at"),
    )

    id = _uuid_pk()
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    kind = Column(String(20), nullable=False, default="command")   # command | question
    transcript = Column(Text, default="")
    normalized_text = Column(Text, default="")
    detected_language = Column(String(20), default="")
    intent = Column(String(40), default="")
    status = Column(String(30), default="")        # recorded | needs_confirmation | ...
    confidence = Column(Numeric(4, 3), nullable=False, default=0)
    provider = Column(String(40), default="")
    response_text = Column(Text, default="")
    source = Column(String(30), nullable=False, default="voice")
    # Set when the turn actually wrote to the ledger.
    event_id = Column(UUID(as_uuid=True), ForeignKey("inventory_events.id"), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Conversation(Base):
    """A continuing exchange with A.R.I.A.

    Kept server-side so that "actually, make it 15" resolves against what was
    really said and really done, not against whatever the client happens to
    still hold in memory.
    """

    __tablename__ = "conversations"

    id = _uuid_pk()
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)
    title = Column(String(200), default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    messages = relationship(
        "ConversationMessage", back_populates="conversation",
        cascade="all, delete-orphan", order_by="ConversationMessage.created_at",
    )


class ConversationMessage(Base):
    """One turn. Tool calls and their results are stored, so the exchange is auditable."""

    __tablename__ = "conversation_messages"
    __table_args__ = (
        Index("ix_messages_conversation_time", "conversation_id", "created_at"),
    )

    id = _uuid_pk()
    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(String(20), nullable=False)          # user | assistant | tool
    content = Column(Text, default="")
    tool_calls = Column(Text, default="")              # JSON, when the model asked for tools
    tool_call_id = Column(String(120), default="")     # set on tool-result rows
    tool_name = Column(String(80), default="")
    detected_language = Column(String(20), default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")


class PendingAction(Base):
    """A write the assistant proposed and is waiting to be confirmed.

    Financial and destructive actions are never executed on the model's say-so.
    The proposal is stored with its exact arguments, and only an explicit
    confirmation referencing this row can run it.
    """

    __tablename__ = "pending_actions"

    id = _uuid_pk()
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    tool_name = Column(String(80), nullable=False)
    arguments = Column(Text, nullable=False)           # JSON
    summary = Column(Text, default="")
    status = Column(String(20), nullable=False, default="pending")  # pending|confirmed|cancelled
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)


class BusinessNote(Base):
    """Durable business knowledge the owner taught A.R.I.A. in conversation.

    Pack sizes are *not* stored here — those belong in UnitConversion, where the
    arithmetic already uses them. This is for the rest: who pays late, which
    supplier comes on Fridays.
    """

    __tablename__ = "business_notes"

    id = _uuid_pk()
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)
    kind = Column(String(40), nullable=False, default="fact")
    subject = Column(String(160), default="")
    content = Column(Text, nullable=False)
    source = Column(String(30), nullable=False, default="aria")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class VisionAnalysis(Base):
    """What A.R.I.A. read in one photograph, and what became of it.

    Stores the *reading*, never the photograph. Images can carry customer
    phone numbers, addresses and invoice totals, so the picture is processed
    and discarded; only the structured business lines are kept, so a follow-up
    like "add just the first two" has something real to refer to.
    """

    __tablename__ = "vision_analyses"
    __table_args__ = (
        Index("ix_vision_business_time", "business_id", "created_at"),
    )

    id = _uuid_pk()
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)

    document_type = Column(String(40), nullable=False, default="unknown")
    detected_language = Column(String(20), default="")
    readable = Column(Boolean, nullable=False, default=True)
    quality_issues = Column(Text, default="")      # JSON array
    notes = Column(Text, default="")

    items = Column(Text, nullable=False, default="[]")   # JSON: matched line items
    invoice = Column(Text, default="")                   # JSON when a bill was read

    provider = Column(String(60), default="")
    model = Column(String(120), default="")
    image_mime = Column(String(40), default="")
    image_bytes = Column(Numeric(12, 0), default=0)      # size only, never the image

    status = Column(String(20), nullable=False, default="analyzed")  # analyzed|applied|cancelled
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    applied_at = Column(DateTime, nullable=True)


class Alert(Base):
    """Acknowledgement/history store. Live alerts are always recomputed from the ledger."""

    __tablename__ = "alerts"

    id = _uuid_pk()
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    alert_type = Column(Enum(AlertType, name="alert_type"), nullable=False)
    severity = Column(Enum(Severity, name="severity"), nullable=False)
    message = Column(Text, nullable=False)
    is_dismissed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
