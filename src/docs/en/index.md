# PayTechUZ Documentation

Welcome to the PayTechUZ documentation. PayTechUZ is a unified payment library for integration with popular payment systems in Uzbekistan (Payme, Click, and Atmos).

## Available Integrations

- [Django Integration](django_integration.md)
- [FastAPI Integration](fastapi_integration.md)
- [Atmos Integration](atmos_integration.md)

## Features

- Support for Payme, Click, and Atmos payment systems
- Easy integration with Django and FastAPI
- Customizable webhook handlers
- Automatic transaction management
- Secure authentication

## Installation

To install PayTechUZ with all dependencies:

```bash
pip install paytechuz
```

For specific framework support:

```bash
# For Django
pip install paytechuz[django]

# For FastAPI
pip install paytechuz[fastapi]
```

## API Key Configuration

**⚠️ Important**: An API key is required to use PayTechUZ.

### Getting Your API Key

To obtain an API key, contact **@muhammadali_me** on Telegram.

### Configuration Methods

#### Method 1: Environment Variable (Recommended)

```bash
# Linux/macOS
export PAYTECH_API_KEY="your-api-key-here"

# Windows
set PAYTECH_API_KEY=your-api-key-here

# In .env file
PAYTECH_API_KEY=your-api-key-here
```

#### Method 2: Explicit in Code

```python
from paytechuz.gateways.payme import PaymeGateway

gateway = PaymeGateway(
    payme_id="...",
    payme_key="...",
    api_key="your-api-key-here"  # Pass API key explicitly
)
```

### Troubleshooting

**Error**: "Missing api_key for paytechuz"
- **Solution**: Set `PAYTECH_API_KEY` environment variable or pass `api_key` parameter

**Error**: "Invalid api_key for paytechuz"
- **Solution**: Verify your API key is correct. If the issue persists, contact @muhammadali_me

For detailed information: [API_KEY_SETUP.md](../../API_KEY_SETUP.md)

## Basic Usage

1. Install the library
2. Configure your settings
3. Create webhook handlers
4. Set up URL endpoints
5. Implement payment event handlers

For detailed instructions, see the framework-specific integration guides.
