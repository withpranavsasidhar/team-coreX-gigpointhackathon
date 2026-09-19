from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import AriaError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AriaError)
    async def handle_aria_error(_: Request, exc: AriaError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError):
        # Pydantic puts the raw exception object in `ctx`, which is not JSON-serializable.
        fields = [
            {"field": ".".join(str(p) for p in err.get("loc", ())), "message": err.get("msg", "")}
            for err in exc.errors()
        ]
        summary = fields[0]["message"] if fields else "The request body was not valid."
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": summary,
                    "details": {"fields": fields},
                }
            },
        )
