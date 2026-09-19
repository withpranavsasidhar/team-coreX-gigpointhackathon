class AriaError(Exception):
    """Base for all domain errors. Maps to the standard API error envelope."""

    code = "INTERNAL_ERROR"
    status_code = 500

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFound(AriaError):
    code = "NOT_FOUND"
    status_code = 404


class ProductNotFound(NotFound):
    code = "PRODUCT_NOT_FOUND"


class BusinessNotFound(NotFound):
    code = "BUSINESS_REQUIRED"
    status_code = 400


class ValidationFailed(AriaError):
    code = "VALIDATION_ERROR"
    status_code = 422


class DuplicateProduct(AriaError):
    code = "DUPLICATE_PRODUCT"
    status_code = 409


class AmbiguousProduct(AriaError):
    code = "PRODUCT_AMBIGUOUS"
    status_code = 409


class AIProviderError(AriaError):
    code = "AI_PROVIDER_ERROR"
    status_code = 502
