# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.17] - 2025-01-31

### Fixed
- **Package**: Fixed __version__ attribute in __init__.py to match package version

## [0.2.16] - 2025-01-31

### Fixed
- **Click Gateway**: Fixed merchant_user_id parameter not being added to payment URL
- **Click Gateway**: Fixed description parameter being incorrectly assigned to merchant_user_id field
- **Click Gateway**: Improved parameter handling in create_payment method

### Changed
- **Click Gateway**: Updated create_payment method to properly handle both description and merchant_user_id parameters
- **Tests**: Updated test cases to reflect the corrected return type (dict instead of string)

### Technical Details
- Fixed bug in `src/paytechuz/gateways/click/client.py` where `merchant_user_id` was being set to `description` value
- Now correctly adds `merchant_user_id` parameter to payment URL when provided
- Properly handles cases where `merchant_user_id` is not provided (omits from URL)
- Description parameter now correctly appears as `description=...` in payment URL

## [0.2.15] - Previous Release
- Previous version with the merchant_user_id bug
