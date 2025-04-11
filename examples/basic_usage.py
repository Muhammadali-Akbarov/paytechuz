"""
Basic usage example for PayTechUZ.
"""
import os
import sys
import logging

# Add parent directory to path to import paytechuz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paytechuz import create_gateway

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Payme configuration
PAYME_ID = 'your-payme-id'
PAYME_KEY = 'your-payme-key'

# Click configuration
CLICK_SERVICE_ID = 'your-service-id'
CLICK_MERCHANT_ID = 'your-merchant-id'
CLICK_SECRET_KEY = 'your-secret-key'


def test_payme():
    """Test Payme gateway."""
    print("\n=== Testing Payme Gateway ===\n")
    
    # Create Payme gateway
    payme = create_gateway(
        'payme',
        payme_id=PAYME_ID,
        payme_key=PAYME_KEY,
        is_test_mode=True
    )
    
    # Create a payment
    payment = payme.create_payment(
        amount=100000,  # 100,000 som
        account_id="12345",
        description="Payment for order #12345",
        return_url="https://example.com/success",
        callback_url="https://example.com/callback"
    )
    
    print("Payment created:")
    print(f"Transaction ID: {payment['transaction_id']}")
    print(f"Payment URL: {payment['payment_url']}")
    print(f"Amount: {payment['amount']} som")
    print(f"Status: {payment['status']}")
    
    # Check payment status
    # Note: In a real scenario, you would check an existing transaction
    # This will likely fail since we just created a test payment
    try:
        status = payme.check_payment(payment['transaction_id'])
        print("\nPayment status:")
        print(f"Status: {status['status']}")
        print(f"Created at: {status['created_at']}")
        print(f"Paid at: {status['paid_at']}")
    except Exception as e:
        print(f"\nFailed to check payment status: {e}")
    
    # Cancel payment
    # Note: In a real scenario, you would cancel an existing transaction
    # This will likely fail since we just created a test payment
    try:
        cancel = payme.cancel_payment(
            payment['transaction_id'],
            reason="Customer request"
        )
        print("\nPayment cancelled:")
        print(f"Status: {cancel['status']}")
        print(f"Cancelled at: {cancel['cancelled_at']}")
    except Exception as e:
        print(f"\nFailed to cancel payment: {e}")


def test_click():
    """Test Click gateway."""
    print("\n=== Testing Click Gateway ===\n")
    
    # Create Click gateway
    click = create_gateway(
        'click',
        service_id=CLICK_SERVICE_ID,
        merchant_id=CLICK_MERCHANT_ID,
        secret_key=CLICK_SECRET_KEY,
        is_test_mode=True
    )
    
    # Create a payment
    payment = click.create_payment(
        amount=100000,  # 100,000 som
        account_id="12345",
        description="Payment for order #12345",
        return_url="https://example.com/success",
        callback_url="https://example.com/callback"
    )
    
    print("Payment created:")
    print(f"Transaction ID: {payment['transaction_id']}")
    print(f"Payment URL: {payment['payment_url']}")
    print(f"Amount: {payment['amount']} som")
    print(f"Status: {payment['status']}")
    
    # Check payment status
    # Note: In a real scenario, you would check an existing transaction
    # This will likely fail since we just created a test payment
    try:
        status = click.check_payment(payment['transaction_id'])
        print("\nPayment status:")
        print(f"Status: {status['status']}")
        print(f"Created at: {status['created_at']}")
        print(f"Paid at: {status['paid_at']}")
    except Exception as e:
        print(f"\nFailed to check payment status: {e}")
    
    # Cancel payment
    # Note: In a real scenario, you would cancel an existing transaction
    # This will likely fail since we just created a test payment
    try:
        cancel = click.cancel_payment(
            payment['transaction_id'],
            reason="Customer request"
        )
        print("\nPayment cancelled:")
        print(f"Status: {cancel['status']}")
        print(f"Cancelled at: {cancel['cancelled_at']}")
    except Exception as e:
        print(f"\nFailed to cancel payment: {e}")


if __name__ == "__main__":
    # Test Payme gateway
    test_payme()
    
    # Test Click gateway
    test_click()
