#!/usr/bin/env python3
"""
Real Payme API test with actual card operations and receipts.
"""
import asyncio
import sys
import os
import time
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from paytechuz.gateways.payme import PaymeGateway


payme = PaymeGateway(
    payme_id="5feb5dd783c40aed047fe655",
    payme_key="rwAAUFwRSFI5&eYtuq5Q7jd7u@Y6kRcRw44g",
    is_test_mode=True
)

result = payme.cards.create(
    card_number="8600495473316478",
    expire_date="0399",
    save=True
)

# get token
token = result.get("result", {}).get("card").get("token")

result = payme.cards.get_verify_code(
    token=token
)

print(result)

# confirm and activate token
result = payme.cards.verify(
    token=token,
    code="666666"
)

print(result)

# check card
result = payme.cards.check(
    token=token
)

print(result)
result = payme.receipts.create(
    amount=10000,
    account={"account_id": "12345"}
)
print(result)

receipt_id = result.get("result", {}).get("receipt", {}).get("_id")

# pay receipt
result = payme.receipts.pay(
    receipt_id=receipt_id,
    token=token
)

print(result)
