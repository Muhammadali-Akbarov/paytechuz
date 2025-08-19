# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2024-01-20

### Added
- **Atmos Payment Gateway Support** - Full integration with Atmos payment system
  - `AtmosGateway` class for payment operations
  - `AtmosWebhookHandler` for webhook processing
  - Complete Django integration with `BaseAtmosWebhookView`
  - FastAPI integration examples
  - Atmos constants and configuration options

### Enhanced
- **Documentation** - Comprehensive documentation for Atmos integration
  - English and Uzbek documentation for Atmos
  - Updated README.md with Atmos examples
  - Complete integration guides for Django and FastAPI
  - Standalone Atmos example (`examples/atmos_example.py`)

### Updated
- **Examples** - All examples updated to include Atmos support
  - Django example with Atmos payment type and webhook
  - FastAPI example with Atmos endpoint and webhook handler
  - Updated configuration examples in all frameworks

### Configuration
- **Settings** - New Atmos configuration options
  - `CONSUMER_KEY` - Atmos consumer key
  - `CONSUMER_SECRET` - Atmos consumer secret  
  - `STORE_ID` - Atmos store ID
  - `TERMINAL_ID` - Atmos terminal ID (optional)
  - `API_KEY` - API key for webhook signature verification
  - `IS_TEST_MODE` - Test/production mode toggle

### Constants
- **PaymentGateway.ATMOS** - New payment gateway type
- **AtmosEndpoints** - API endpoint constants
- **AtmosNetworks** - Network URL constants
- **AtmosTransactionStatus** - Transaction status constants

### Features
- **Payment Operations**
  - Create payment with account ID and amount
  - Check payment status by transaction ID
  - Cancel payment with optional reason
  - Automatic payment URL generation

- **Webhook Support**
  - Signature verification for security
  - Automatic webhook data processing
  - Django and FastAPI integration
  - Error handling and response formatting

- **Framework Integration**
  - Django: `BaseAtmosWebhookView` class
  - FastAPI: Webhook endpoint examples
  - Configuration through settings/environment variables

### Examples
- **Standalone Example** (`examples/atmos_example.py`)
  - Complete Atmos integration demonstration
  - Payment creation, status checking, cancellation
  - Webhook processing and signature verification
  - Error handling examples

- **Django Example** (`examples/paytechuz_django/`)
  - Updated models with Atmos payment type
  - Atmos webhook view implementation
  - URL routing for Atmos webhooks
  - Complete configuration examples

- **FastAPI Example** (`examples/paytechuz_fastapi/`)
  - Atmos gateway initialization
  - Payment creation endpoint
  - Webhook processing endpoint
  - Environment variable configuration

### Documentation
- **Atmos Integration Guide** - Complete integration documentation
  - Basic usage and configuration
  - Payment operations (create, check, cancel)
  - Webhook handling and security
  - Error handling and best practices
  - Available in both English and Uzbek

- **Framework Guides** - Updated integration guides
  - Django integration with Atmos examples
  - FastAPI integration with Atmos examples
  - Configuration and setup instructions

### Breaking Changes
None. This release is fully backward compatible.

### Migration Guide
No migration required. Existing Payme and Click integrations will continue to work without changes.

To add Atmos support:
1. Update to version 0.3.0
2. Add Atmos configuration to your settings
3. Import and use `AtmosGateway` class
4. Set up webhook handlers if needed

## [0.2.24] - Previous Release

### Features
- Payme payment gateway integration
- Click payment gateway integration
- Django and FastAPI framework support
- Webhook handling for Payme and Click
- Comprehensive documentation and examples

---

For more information about each release, see the [GitHub releases page](https://github.com/PayTechUz/paytechuz/releases).
