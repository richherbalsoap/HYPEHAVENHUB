class AtelierException(Exception):
    """Base exception class for all custom application errors."""
    def __init__(self, message, status_code=400, code="bad_request"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


class InventoryConflictError(AtelierException):
    """Raised when an inventory validation or adjustment conflict arises (e.g. out of stock)."""
    def __init__(self, message="Insufficient inventory to fulfill the request.", status_code=409, code="out_of_stock"):
        super().__init__(message, status_code, code)


class PaymentGatewayError(AtelierException):
    """Raised when a payment processor transaction fails or verification fails."""
    def __init__(self, message="Payment processing failed. Please try again.", status_code=400, code="payment_failed"):
        super().__init__(message, status_code, code)


class CouponValidationError(AtelierException):
    """Raised when a coupon validation fails."""
    def __init__(self, message="Invalid or expired discount coupon.", status_code=400, code="invalid_coupon"):
        super().__init__(message, status_code, code)
