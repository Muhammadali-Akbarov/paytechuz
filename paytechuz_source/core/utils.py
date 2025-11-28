"""
Utility functions for payment gateways.
"""
import base64
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Union, Optional

logger = logging.getLogger(__name__)

def generate_timestamp() -> int:
    """
    Generate a Unix timestamp.

    Returns:
        Current Unix timestamp in seconds
    """
    return int(time.time())


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID.

    Args:
        prefix: Prefix for the ID

    Returns:
        Unique ID
    """
    timestamp = generate_timestamp()
    unique_id = f"{timestamp}{hash(timestamp)}"
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id

def format_amount(amount: Union[int, float, str]) -> int:
    """
    Format amount to integer (in tiyin/kopeyka).

    Args:
        amount: Amount in som/ruble

    Returns:
        Amount in tiyin/kopeyka (integer)
    """
    try:
        # Convert to float first to handle string inputs
        float_amount = float(amount)
        # Convert to tiyin/kopeyka (multiply by 100) and round to integer
        return int(float_amount * 100)
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to format amount: {amount}, Error: {e}")
        raise ValueError(f"Invalid amount format: {amount}")


def format_datetime(dt: datetime) -> str:
    """
    Format datetime to ISO 8601 format.

    Args:
        dt: Datetime object

    Returns:
        Formatted datetime string
    """
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")

def datetime_to_timestamp(dt: datetime) -> int:
    """
    Convert datetime to Unix timestamp.

    Args:
        dt: Datetime object

    Returns:
        Unix timestamp in seconds
    """
    return int(dt.timestamp())


def timestamp_to_datetime(timestamp: int) -> datetime:
    """
    Convert Unix timestamp to datetime.

    Args:
        timestamp: Unix timestamp in seconds

    Returns:
        Datetime object
    """
    return datetime.fromtimestamp(timestamp)

def generate_hmac_signature(
    data: Union[str, Dict[str, Any], bytes],
    secret_key: str,
    algorithm: str = "sha256"
) -> str:
    """
    Generate HMAC signature.

    Args:
        data: Data to sign
        secret_key: Secret key for signing
        algorithm: Hash algorithm to use

    Returns:
        HMAC signature as hexadecimal string
    """
    if isinstance(data, dict):
        data = json.dumps(data, separators=(',', ':'))

    if isinstance(data, str):
        data = data.encode('utf-8')

    key = secret_key.encode('utf-8')

    if algorithm.lower() == "sha256":
        signature = hmac.new(key, data, hashlib.sha256).hexdigest()
    elif algorithm.lower() == "sha512":
        signature = hmac.new(key, data, hashlib.sha512).hexdigest()
    elif algorithm.lower() == "md5":
        signature = hmac.new(key, data, hashlib.md5).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    return signature


def generate_basic_auth(username: str, password: str) -> str:
    """
    Generate Basic Authentication header value.

    Args:
        username: Username
        password: Password

    Returns:
        Basic Authentication header value
    """
    auth_str = f"{username}:{password}"
    auth_bytes = auth_str.encode('utf-8')
    encoded = base64.b64encode(auth_bytes).decode('utf-8')
    return f"Basic {encoded}"

def handle_exceptions(func):
    """
    Decorator to handle exceptions and convert them to payment exceptions.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """
    from .exceptions import (
        InternalServiceError,
        exception_whitelist
    )

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exception_whitelist as exc:
            # No need to wrap exceptions that are already payment exceptions
            raise exc
        except Exception as exc:
            logger.exception(f"Unexpected error in {func.__name__}: {exc}")
            raise InternalServiceError(str(exc))

    return wrapper


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> Optional[str]:
    """
    Validate that all required fields are present in the data.

    Args:
        data: Data to validate
        required_fields: List of required field names

    Returns:
        Error message if validation fails, None otherwise
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        return f"Missing required fields: {', '.join(missing_fields)}"
    return None
