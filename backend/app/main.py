from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.error_handlers import register_error_handlers
from app.database import Base, engine
from app.models import tables  # noqa: F401  (import registers models on Base)
from app.routers import (
    aria, auth, businesses, context, customers, events, intelligence, inventory, memory,
    operations, products, vision, voice,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="A.R.I.A. — Smart Voice Inventory Assistant", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

# Order matters: context.router owns literal paths like /businesses/summary,
# which would otherwise be swallowed by businesses.router's /businesses/{id}.
for router in (
    auth.router, context.router, businesses.router, products.router, inventory.router,
    events.router, memory.router, customers.router, operations.router,
    voice.router, intelligence.router, aria.router, vision.router,
):
    app.include_router(router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
