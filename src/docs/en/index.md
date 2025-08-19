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

## Basic Usage

1. Install the library
2. Configure your settings
3. Create webhook handlers
4. Set up URL endpoints
5. Implement payment event handlers

For detailed instructions, see the framework-specific integration guides.
