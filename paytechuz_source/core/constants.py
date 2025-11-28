"""
Constants for payment gateways.
"""
from enum import Enum

class TransactionState(Enum):
    """Transaction states."""
    CREATED = 0
    INITIATING = 1
    SUCCESSFULLY = 2
    CANCELED = -2
    CANCELED_DURING_INIT = -1


class PaymentGateway(Enum):
    """Payment gateway types."""
    PAYME = "payme"
    CLICK = "click"
    ATMOS = "atmos"

class PaymeEndpoints:
    """Payme API endpoints."""
    RECEIPTS_CREATE = "receipts.create"
    RECEIPTS_PAY = "receipts.pay"
    RECEIPTS_SEND = "receipts.send"
    RECEIPTS_CHECK = "receipts.check"
    RECEIPTS_CANCEL = "receipts.cancel"
    RECEIPTS_GET = "receipts.get"
    CARDS_CREATE = "cards.create"
    CARDS_VERIFY = "cards.verify"
    CARDS_CHECK = "cards.check"
    CARDS_REMOVE = "cards.remove"
    CARDS_GET_VERIFY_CODE = "cards.get_verify_code"


class PaymeNetworks:
    """Payme API networks."""
    TEST_NET = "https://checkout.test.paycom.uz/api"
    PROD_NET = "https://checkout.paycom.uz/api"

class ClickEndpoints:
    """Click API endpoints."""
    PREPARE = "prepare"
    COMPLETE = "complete"
    MERCHANT_API = "merchant/api"


class ClickNetworks:
    """Click API networks."""
    TEST_NET = "https://api.click.uz/v2/merchant"
    PROD_NET = "https://api.click.uz/v2/merchant"

class ClickActions:
    """Click API actions."""
    PREPARE = 0
    COMPLETE = 1


class PaymeCancelReason:
    """Payme cancel reason codes."""
    REASON_USER_NOT_FOUND = 1
    REASON_DEBIT_OPERATION_FAILED = 2
    REASON_EXECUTION_ERROR = 3
    REASON_TIMEOUT = 4
    REASON_FUND_RETURNED = 5
    REASON_UNKNOWN = 6
    REASON_CANCELLED_BY_USER = 7
    REASON_SUSPICIOUS_OPERATION = 8
    REASON_MERCHANT_DECISION = 9


class AtmosEndpoints:
    """Atmos API endpoints."""
    TOKEN = "/token"
    CREATE_PAYMENT = "/merchant/pay/create"
    CHECK_PAYMENT = "/merchant/pay/get-status"
    CANCEL_PAYMENT = "/merchant/pay/cancel"


class AtmosNetworks:
    """Atmos API networks."""
    PROD_NET = "https://partner.atmos.uz"
    TEST_CHECKOUT = "https://test-checkout.pays.uz/invoice/get"
    PROD_CHECKOUT = "https://checkout.pays.uz/invoice/get"


class AtmosTransactionStatus:
    """Atmos transaction status codes."""
    CREATED = "created"
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
