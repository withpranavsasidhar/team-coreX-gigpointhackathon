"""A.R.I.A. Vision.

The provider is exercised over a real socket, so request building, image
encoding, JSON decoding and error handling are genuine. Behind it, matching,
confidence banding and the apply path run against the real catalogue, the real
tool layer and the real event engine.

What these cannot prove: that a hosted vision model reads a real photograph
correctly. That needs a real VISION_MODEL and a real image.
"""
import base64
import json

import pytest

from app.models import EventType, InventoryEvent, VisionAnalysis
from app.providers.vision import (
    VisionError, VisionUnavailable, decode_image, vision_status,
)
from app.services import vision_service
from tests import fake_openai_server as fake

# A 1x1 PNG. Enough to be a valid image payload; the model is scripted anyway.
PNG_1X1 = base64.b64encode(bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000a49444154789c6360000002000100ffff0300000600"
    "05570c1d0000000049454e44ae426082"
)).decode()
IMAGE_URI = f"data:image/png;base64,{PNG_1X1}"


def vision_message(payload: dict) -> dict:
    return {"role": "assistant", "content": json.dumps(payload)}


@pytest.fixture()
def live_vision(monkeypatch):
    """Point the real vision provider at a local OpenAI-compatible server."""
    server = fake.start(port=8772)
    fake.SCRIPT.clear()
    fake.SEEN_REQUESTS.clear()

    from app.config import settings
    monkeypatch.setattr(settings, "ai_api_key", "vision-key")
    monkeypatch.setattr(settings, "ai_base_url", "http://127.0.0.1:8772")
    monkeypatch.setattr(settings, "vision_model", "test/vision-model")

    from app.providers.vision import OpenAICompatibleVisionProvider
    provider = OpenAICompatibleVisionProvider()
    monkeypatch.setattr("app.services.vision_service.get_vision_provider", lambda: provider)

    yield provider
    server.shutdown()


# --- image validation (before anything is sent anywhere) ------------------

def test_valid_png_is_accepted():
    image = decode_image(IMAGE_URI)
    assert image.mime == "image/png"
    assert image.data


@pytest.mark.parametrize("bad", ["", "not-an-image", "data:text/plain;base64,aGk="])
def test_non_images_are_refused(bad):
    with pytest.raises(VisionError):
        decode_image(bad)


def test_unsupported_image_type_is_refused():
    with pytest.raises(VisionError) as exc:
        decode_image("data:image/gif;base64,R0lGODlhAQABAAAAACw=")
    assert "not supported" in str(exc.value)


def test_oversized_image_is_refused(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "vision_max_image_mb", 0.000001)
    with pytest.raises(VisionError) as exc:
        decode_image(IMAGE_URI)
    assert "MB" in str(exc.value)


# --- unconfigured behaviour ----------------------------------------------

def test_vision_is_unavailable_without_a_model():
    from app.providers.vision import get_vision_provider
    get_vision_provider.cache_clear()
    status = vision_status()
    assert status["available"] is False
    assert "vision-capable" in status["reason"]


def test_unavailable_provider_raises_rather_than_returning_nothing():
    from app.providers.vision import UnavailableVisionProvider
    with pytest.raises(VisionUnavailable):
        UnavailableVisionProvider().read_image(decode_image(IMAGE_URI))


# --- reading and matching -------------------------------------------------

def test_stock_list_is_read_matched_and_banded(db, business, catalogue, live_vision):
    fake.SCRIPT.append(vision_message({
        "document_type": "handwritten_list",
        "language": "en",
        "readable": True,
        "quality_issues": [],
        "notes": "A handwritten stock list.",
        "items": [
            {"raw_name": "Rice", "normalized_name": "Rice", "quantity": 50,
             "unit": "bags", "confidence": 0.96, "item_note": ""},
            {"raw_name": "Coke", "normalized_name": "Coke", "quantity": 5,
             "unit": "cartons", "confidence": 0.93, "item_note": ""},
            {"raw_name": "Oil", "normalized_name": "Cooking Oil", "quantity": 20,
             "unit": "litres", "confidence": 0.78, "item_note": ""},
        ],
    }))

    result = vision_service.analyze_image(db, business, IMAGE_URI)

    assert result["counts"]["total"] == 3
    names = [i["product_name"] for i in result["items"]]
    assert names == ["Rice", "Coke", "Cooking Oil"]          # matched to the real catalogue
    assert result["items"][0]["confidence_band"] == "high"
    assert result["items"][2]["confidence_band"] == "medium"

    # Analysis alone must never move stock.
    assert db.query(InventoryEvent).filter(
        InventoryEvent.source == "vision"
    ).count() == 0


def test_the_request_actually_sends_the_image(db, business, catalogue, live_vision):
    fake.SCRIPT.append(vision_message({"items": [], "readable": True}))
    vision_service.analyze_image(db, business, IMAGE_URI, hint="today's delivery")

    sent = fake.SEEN_REQUESTS[0]
    assert sent["model"] == "test/vision-model"
    assert sent["authorization"] == "Bearer vision-key"
    parts = sent["messages"][0]["content"]
    assert any(p.get("type") == "image_url" for p in parts)
    assert any("delivery" in p.get("text", "") for p in parts if p.get("type") == "text")


def test_unknown_product_is_flagged_never_auto_created(db, business, catalogue, live_vision):
    from app.models import Product
    before = db.query(Product).count()

    fake.SCRIPT.append(vision_message({
        "document_type": "inventory_list", "readable": True,
        "items": [{"raw_name": "Sunrise Oil", "normalized_name": "Sunrise Oil",
                   "quantity": 10, "unit": "pieces", "confidence": 0.95}],
    }))
    result = vision_service.analyze_image(db, business, IMAGE_URI)

    item = result["items"][0]
    # "Sunrise Oil" shares a word with "Cooking Oil", so the matcher may offer
    # it as a weak candidate. What matters is that it is never applied on that
    # basis and never created on A.R.I.A.'s own initiative.
    assert item["ready"] is False
    assert item["suggest_create"] is True
    assert any("catalogue" in i for i in item["issues"])
    assert db.query(Product).count() == before, "must not create the product"


def test_ambiguous_product_asks_instead_of_choosing(db, business, catalogue, live_vision):
    from app.models import Product
    db.add(Product(business_id=business.id, name="Engine Oil", base_unit="litres",
                   current_quantity=5, minimum_quantity=1, reorder_quantity=1, price=300))
    db.commit()

    fake.SCRIPT.append(vision_message({
        "readable": True,
        "items": [{"raw_name": "Oil", "normalized_name": "Oil", "quantity": 4,
                   "unit": "litres", "confidence": 0.95}],
    }))
    result = vision_service.analyze_image(db, business, IMAGE_URI)

    item = result["items"][0]
    assert item["match_state"] == "ambiguous"
    assert item["ready"] is False
    assert len(item["candidates"]) >= 2


def test_missing_quantity_is_never_invented(db, business, catalogue, live_vision):
    fake.SCRIPT.append(vision_message({
        "readable": True,
        "items": [{"raw_name": "Biscuits", "normalized_name": "Biscuits",
                   "quantity": None, "unit": "pieces", "confidence": 0.9,
                   "item_note": "quantity smudged"}],
    }))
    result = vision_service.analyze_image(db, business, IMAGE_URI)

    item = result["items"][0]
    assert item["quantity"] is None
    assert item["ready"] is False
    assert any("Quantity unclear" in i for i in item["issues"])


def test_low_confidence_line_is_not_ready(db, business, catalogue, live_vision):
    fake.SCRIPT.append(vision_message({
        "readable": True,
        "items": [{"raw_name": "Rice", "normalized_name": "Rice", "quantity": 10,
                   "unit": "bags", "confidence": 0.41}],
    }))
    result = vision_service.analyze_image(db, business, IMAGE_URI)
    assert result["items"][0]["confidence_band"] == "low"
    assert result["items"][0]["ready"] is False


def test_unreadable_image_refuses_to_guess(db, business, catalogue, live_vision):
    fake.SCRIPT.append(vision_message({
        "document_type": "other", "readable": False,
        "quality_issues": ["blur", "dark"], "items": [],
    }))
    result = vision_service.analyze_image(db, business, IMAGE_URI)

    assert result["readable"] is False
    assert result["items"] == []
    assert "couldn't read this image clearly" in result["summary"]
    assert "Try better lighting." in result["quality_advice"]


def test_no_business_items_is_said_plainly(db, business, catalogue, live_vision):
    fake.SCRIPT.append(vision_message({"readable": True, "items": []}))
    result = vision_service.analyze_image(db, business, IMAGE_URI)
    assert "couldn't identify any recognisable business items" in result["summary"]


def test_invoice_details_are_extracted(db, business, catalogue, live_vision):
    fake.SCRIPT.append(vision_message({
        "document_type": "invoice", "readable": True,
        "invoice": {"supplier": "Kumar Traders", "invoice_number": "INV-42",
                    "date": "2026-09-19", "total": 12500},
        "items": [{"raw_name": "Rice", "normalized_name": "Rice", "quantity": 10,
                   "unit": "bags", "price": 14500, "confidence": 0.95}],
    }))
    result = vision_service.analyze_image(db, business, IMAGE_URI)

    assert result["document_type"] == "invoice"
    assert result["invoice"]["supplier"] == "Kumar Traders"


def test_multilingual_line_is_read_and_matched(db, business, catalogue, live_vision):
    """Telugu script on the page, real product underneath."""
    fake.SCRIPT.append(vision_message({
        "language": "te-en", "readable": True,
        "items": [{"raw_name": "బియ్యం", "normalized_name": "Rice", "quantity": 50,
                   "unit": "kg", "confidence": 0.92}],
    }))
    result = vision_service.analyze_image(db, business, IMAGE_URI)

    item = result["items"][0]
    assert item["raw_name"] == "బియ్యం"
    assert item["product_name"] == "Rice"
    assert result["language"] == "te-en"


def test_unrecognised_unit_is_flagged(db, business, catalogue, live_vision):
    fake.SCRIPT.append(vision_message({
        "readable": True,
        "items": [{"raw_name": "Rice", "normalized_name": "Rice", "quantity": 2,
                   "unit": "wheelbarrows", "confidence": 0.95}],
    }))
    result = vision_service.analyze_image(db, business, IMAGE_URI)
    assert any("not a unit I recognise" in i for i in result["items"][0]["issues"])


# --- the image itself is not kept ----------------------------------------

def test_the_photograph_is_not_stored(db, business, catalogue, live_vision):
    fake.SCRIPT.append(vision_message({
        "readable": True,
        "items": [{"raw_name": "Rice", "normalized_name": "Rice", "quantity": 5,
                   "unit": "bags", "confidence": 0.95}],
    }))
    vision_service.analyze_image(db, business, IMAGE_URI)

    record = db.query(VisionAnalysis).one()
    stored = json.dumps({c.name: str(getattr(record, c.name))
                         for c in record.__table__.columns})
    assert PNG_1X1[:40] not in stored, "the image must not be persisted"
    assert float(record.image_bytes) > 0, "only its size is kept"


# --- applying goes through the existing engine ---------------------------

def test_apply_writes_through_the_existing_event_engine(db, business, catalogue, live_vision):
    fake.SCRIPT.append(vision_message({
        "readable": True,
        "items": [
            {"raw_name": "Rice", "normalized_name": "Rice", "quantity": 50,
             "unit": "bags", "confidence": 0.96},
            {"raw_name": "Coke", "normalized_name": "Coke", "quantity": 5,
             "unit": "pieces", "confidence": 0.94},
        ],
    }))
    analysis = vision_service.analyze_image(db, business, IMAGE_URI)

    rice_before = float(catalogue["Rice"].current_quantity)
    coke_before = float(catalogue["Coke"].current_quantity)

    from uuid import UUID
    result = vision_service.apply_analysis(
        db, business, UUID(analysis["analysis_id"]),
        [{"product_name": "Rice", "quantity": 50, "unit": "bags"},
         {"product_name": "Coke", "quantity": 5, "unit": "pieces"}],
    )

    assert result["counts"]["applied"] == 2
    db.refresh(catalogue["Rice"])
    db.refresh(catalogue["Coke"])
    assert float(catalogue["Rice"].current_quantity) == rice_before + 50
    assert float(catalogue["Coke"].current_quantity) == coke_before + 5

    # Real ledger events, stamped as vision-originated.
    events = db.query(InventoryEvent).filter(InventoryEvent.source == "vision").all()
    assert len(events) == 2
    assert all(e.event_type == EventType.STOCK_IN for e in events)


def test_apply_uses_the_owners_edits_not_the_readings(db, business, catalogue, live_vision):
    """What gets applied is what the person approved, not what the model read."""
    fake.SCRIPT.append(vision_message({
        "readable": True,
        "items": [{"raw_name": "Rice", "normalized_name": "Rice", "quantity": 50,
                   "unit": "bags", "confidence": 0.96}],
    }))
    analysis = vision_service.analyze_image(db, business, IMAGE_URI)
    before = float(catalogue["Rice"].current_quantity)

    from uuid import UUID
    vision_service.apply_analysis(
        db, business, UUID(analysis["analysis_id"]),
        [{"product_name": "Rice", "quantity": 12, "unit": "bags"}],   # corrected by hand
    )
    db.refresh(catalogue["Rice"])
    assert float(catalogue["Rice"].current_quantity) == before + 12


def test_apply_refuses_an_unknown_product(db, business, catalogue, live_vision):
    fake.SCRIPT.append(vision_message({"readable": True, "items": []}))
    analysis = vision_service.analyze_image(db, business, IMAGE_URI)

    from uuid import UUID
    result = vision_service.apply_analysis(
        db, business, UUID(analysis["analysis_id"]),
        [{"product_name": "Caviar", "quantity": 3}],
    )
    assert result["counts"]["applied"] == 0
    assert "couldn't find" in result["failed"][0]["error"]
    assert "Nothing" in result["summary"]


def test_apply_refuses_a_missing_quantity(db, business, catalogue, live_vision):
    fake.SCRIPT.append(vision_message({"readable": True, "items": []}))
    analysis = vision_service.analyze_image(db, business, IMAGE_URI)

    from uuid import UUID
    result = vision_service.apply_analysis(
        db, business, UUID(analysis["analysis_id"]),
        [{"product_name": "Rice", "quantity": None}],
    )
    assert result["counts"]["applied"] == 0


def test_another_businesss_analysis_cannot_be_applied(db, business, catalogue, live_vision):
    from app.models import Business
    fake.SCRIPT.append(vision_message({"readable": True, "items": []}))
    analysis = vision_service.analyze_image(db, business, IMAGE_URI)

    intruder = Business(business_name="Someone Else", business_type="bakery")
    db.add(intruder)
    db.commit()

    from uuid import UUID
    with pytest.raises(VisionError):
        vision_service.apply_analysis(
            db, intruder, UUID(analysis["analysis_id"]),
            [{"product_name": "Rice", "quantity": 5}],
        )


# --- transport failure ----------------------------------------------------

def test_vision_service_failure_is_reported(db, business, catalogue, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "ai_api_key", "k")
    monkeypatch.setattr(settings, "ai_base_url", "http://127.0.0.1:9")
    monkeypatch.setattr(settings, "vision_model", "test/vision")

    from app.providers.vision import OpenAICompatibleVisionProvider
    provider = OpenAICompatibleVisionProvider()
    monkeypatch.setattr("app.services.vision_service.get_vision_provider", lambda: provider)

    with pytest.raises(VisionError) as exc:
        vision_service.analyze_image(db, business, IMAGE_URI)
    assert "temporarily unavailable" in str(exc.value)


def test_unparseable_model_output_is_refused(db, business, catalogue, live_vision):
    fake.SCRIPT.append({"role": "assistant", "content": "I think I saw some rice maybe"})
    with pytest.raises(VisionError) as exc:
        vision_service.analyze_image(db, business, IMAGE_URI)
    assert "couldn't read a clear result" in str(exc.value)
