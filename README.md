# PayTechUZ

A unified Python package for Uzbekistan payment gateways (Payme, Click) with easy integration for Django, Flask, and FastAPI.

## Installation

```bash
pip install paytechuz
```

For Django integration:
```bash
pip install paytechuz[django]
```

For FastAPI integration:
```bash
pip install paytechuz[fastapi]
```

For Flask integration:
```bash
pip install paytechuz[flask]
```

## Usage

### Basic Usage

```python
from paytechuz import create_gateway

# Create a Payme gateway
payme = create_gateway('payme',
                      payme_id='your-payme-id',
                      payme_key='your-payme-key',
                      is_test_mode=True)

# Create a Click gateway
click = create_gateway('click',
                      service_id='your-service-id',
                      merchant_id='your-merchant-id',
                      secret_key='your-secret-key',
                      is_test_mode=True)

# Create a payment with Payme
payment = payme.create_payment(
    amount=100000,  # 100,000 som
    account_id="12345",
    description="Payment for order #12345",
    return_url="https://example.com/success",
    callback_url="https://example.com/callback"
)

# Get payment URL
payment_url = payment['payment_url']

# Check payment status
status = payme.check_payment(payment['transaction_id'])

# Cancel payment
cancel = payme.cancel_payment(payment['transaction_id'], reason="Customer request")
```

### Django Integration

Add to your settings.py:
```python
INSTALLED_APPS = [
    # ...
    'paytechuz.integrations.django',
]

# Payme configuration
PAYME_ID = 'your-payme-id'
PAYME_KEY = 'your-payme-key'
PAYME_ACCOUNT_MODEL = 'your_app.YourAccountModel'
PAYME_ACCOUNT_FIELD = 'id'
PAYME_AMOUNT_FIELD = 'amount'
PAYME_ONE_TIME_PAYMENT = True

# Click configuration
CLICK_SERVICE_ID = 'your-service-id'
CLICK_MERCHANT_ID = 'your-merchant-id'
CLICK_SECRET_KEY = 'your-secret-key'
CLICK_ACCOUNT_MODEL = 'your_app.YourAccountModel'
```

Add to your urls.py:
```python
from django.urls import path, include

urlpatterns = [
    # ...
    path('payments/', include('paytechuz.integrations.django.urls')),
]
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from paytechuz.integrations.fastapi import routes, models
from your_app.database import engine, get_db

app = FastAPI()

# Create tables
models.Base.metadata.create_all(bind=engine)

# Include payment routes
app.include_router(
    routes.router,
    prefix="/payments",
    tags=["payments"],
    dependencies=[Depends(get_db)]
)
```

### Flask Integration

```python
from flask import Flask
from paytechuz.integrations.flask import routes, models

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payments.db'

# Initialize database
models.db.init_app(app)

# Register payment routes
app.register_blueprint(routes.blueprint, url_prefix='/payments')

with app.app_context():
    models.db.create_all()
```

## Features

- **Unified API**: Consistent interface for both Payme and Click payment systems
- **Framework Support**: Ready-to-use integrations for Django, Flask, and FastAPI
- **Type Hints**: Full type annotation for better IDE support
- **Comprehensive Documentation**: Detailed documentation with examples
- **Error Handling**: Robust error handling with descriptive exceptions
- **Webhook Support**: Built-in webhook handlers for payment notifications

## Payment Gateways

### Payme

- Create payments
- Check payment status
- Cancel payments
- Card operations (create, verify, check, remove)
- Receipt operations (create, pay, send, check, cancel, get)
- Webhook handling

### Click

- Create payments
- Check payment status
- Cancel payments
- Merchant API operations
- Webhook handling

## Contributing

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Muhammadali-Akbarov/paytechuz.git
   cd paytechuz
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

### Running Tests

```bash
python -m unittest discover tests
```

### Creating a New Release

We provide a script to help with creating new releases:

```bash
./create_release.sh
```

This script will:
1. Ask for a new version number
2. Update the version in setup.py
3. Create a new branch and commit the changes
4. Create a git tag for the release
5. Push the branch and tag to GitHub (optional)

### Publishing to PyPI

To build and publish the package to PyPI, use the provided script:

```bash
./upload_to_pypi.sh
```

Alternatively, you can create a release on GitHub, and the GitHub Actions workflow will automatically publish the package to PyPI.

For more details, see [PYPI_UPLOAD.md](PYPI_UPLOAD.md).

## License

MIT
