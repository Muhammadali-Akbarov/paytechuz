
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

# create receipt
result = payme.receipts.create(
    amount=10000,
    account={"account_id": "12345"}
)

token = "689dba89b0dfe8aeb6911fbb_OxRg6ys6ayepAiKtv17m7og8yT201NzSDesrZJicGDomuuFrm4vvAdTcTwvKtxUEUJB1TjGBednS2XCUSk7MR4jecQ7pvuOs9CNTS7pcwtk8Qb1149EbJiqUYKbdcwFxMmFh9MPiFSbvHt99C5m7cfpj7WP8T3oBYtQ0zMqEUuAytcXtIiqV1m4vWPXdJtp5drhId8Ym7zRdRKWM36XD4aRNFRTwhHCxJz7TvQUvrv5gAGX0HxSDBP4cQTwkHBpzyOTF16mvsYy8b80XmXgEIFRgXkNzSEOhot3z61sPfxNcM0rWtD2AfCbdAygS2q4SwKKhOaSTkP1GWCXwaWikEadmCPDoujC8sxFNuj8HjoKe8Ky2TatwBQ2ySzagFVuFduDKxb"

receipt_id = result.get("result", {}).get("receipt", {}).get("_id")
# pay receipt
result = payme.receipts.pay(
    receipt_id=receipt_id,
    token=token
)

print(result)

# cancel receipt
result = payme.receipts.cancel(
    receipt_id=receipt_id
)

print(result)
