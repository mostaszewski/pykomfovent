# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2026-01-22

### Changed

- Improved documentation with comprehensive API reference and examples

## [1.0.1] - 2026-01-21

### Added

- Initial release
- `KomfoventClient` for communicating with Komfovent C6 units
- `KomfoventDiscovery` for auto-discovering devices on local network
- `KomfoventState` data model with all sensor values
- State properties: `is_on`, `heating_active`, `eco_mode`
- Control methods: `set_mode()`, `set_supply_temp()`, `set_register()`
- Schedule management: `get_schedule()`, `set_schedule()`
- Retry logic with exponential backoff
- Async/await API using aiohttp
- Python 3.11+ support
