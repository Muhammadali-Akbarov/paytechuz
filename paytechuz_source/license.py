import os
from typing import Optional

import requests

from paytechuz.core.exceptions import UnknownPartnerError


API_KEY_ENV_NAME = "PAYTECH_API_KEY"


def _get_api_key(explicit_key: Optional[str]) -> str:
    api_key = explicit_key or os.environ.get(API_KEY_ENV_NAME)
    if not api_key:
        raise UnknownPartnerError(
            "Missing api_key for paytechuz. To get a valid api_key please contact @muhammadali_me on Telegram."
        )
    return api_key


def validate_api_key(api_key: Optional[str] = None) -> None:
    key = _get_api_key(api_key)

    try:
        license_url = "https://paytechuz.demo-projects.uz/api/v1/license/validate"
        response = requests.post(
            license_url,
            json={"api_key": key},
            timeout=5,
        )
    except requests.RequestException as exc:
        raise UnknownPartnerError(
            "Unable to validate api_key. Please contact @muhammadali_me on Telegram."
        ) from exc

    if response.status_code != 200:
        raise UnknownPartnerError(
            "Invalid api_key for paytechuz. Please contact @muhammadali_me on Telegram."
        )
