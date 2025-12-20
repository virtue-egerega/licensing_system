# License Service - Multi-Brand WordPress Ecosystem

A centralized, multi-tenant license management service for managing software licenses across multiple brands in a WordPress ecosystem.

## Features

- **Multi-Brand Support**: Manage licenses for multiple brands (WP Rocket, RankMath, Imagify, etc.) in a single system
- **License Lifecycle Management**: Create, activate, suspend, and cancel licenses
- **Seat Management**: Track and enforce seat limits for license activations
- **Cross-Brand Queries**: Brand-level API to query licenses across all brands by customer email
- **RESTful API**: Clean, well-documented REST API with Django REST Framework
- **Production-Ready**: Includes logging, audit trails, error handling, and monitoring hooks

## Tech Stack

- **Framework**: Django 5.1.4
- **API**: Django REST Framework 3.15.2
- **Database**: PostgreSQL 16
- **Testing**: pytest with 40 unit and integration tests
- **Linting**: pylint, black, isort
- **Containerization**: Docker & docker-compose
- **CI/CD**: GitHub Actions

## Quick Start

### Prerequisites

- Docker and docker-compose installed
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd saas_virtue_interview_assessment
```

### 2. Build and Start Services

```bash
docker-compose build
docker-compose up
```

The API will be available at `http://localhost:8000`

### 3. Create Test Data (Optional)

```bash
# Access the Django shell
docker-compose exec app python manage.py shell

# Create a brand and product
from core.models import Brand, Product
import hashlib

api_key = "test-api-key-rankmath"
api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

brand = Brand.objects.create(
    name="RankMath",
    slug="rankmath",
    api_key_hash=api_key_hash
)

product = Product.objects.create(
    brand=brand,
    name="RankMath Pro",
    slug="rankmath-pro",
    default_seat_limit=5
)
```

## API Documentation

### Base URL

```
http://localhost:8000/api/v1
```

### Authentication

Brand-facing endpoints require authentication via `X-API-Key` header:

```bash
curl -H "X-API-Key: test-api-key-rankmath" http://localhost:8000/api/v1/brands/licenses
```

### Endpoints

#### 1. Create License Key (US1)

```bash
POST /api/v1/brands/license-keys
X-API-Key: <brand-api-key>

{
  "customer_email": "customer@example.com"
}
```

#### 2. Create License (US1)

```bash
POST /api/v1/brands/licenses
X-API-Key: <brand-api-key>

{
  "customer_email": "customer@example.com",
  "product_slug": "rankmath-pro",
  "expires_at": "2025-12-31T23:59:59Z",  # optional
  "seat_limit": 5  # optional
}
```

#### 3. Update License (US2)

```bash
PATCH /api/v1/brands/licenses/{license_id}
X-API-Key: <brand-api-key>

{
  "status": "suspended",
  "expires_at": "2026-12-31T23:59:59Z"
}
```

#### 4. List Licenses by Email (US6)

```bash
GET /api/v1/brands/licenses/search?customer_email=customer@example.com
X-API-Key: <brand-api-key>
```

#### 5. Activate License (US3)

```bash
POST /api/v1/products/activations

{
  "license_key": "RANKMATH-uuid",
  "instance_identifier": "https://mysite.com",
  "metadata": {"plugin_version": "1.2.3"}
}
```

#### 6. Deactivate Activation (US5)

```bash
DELETE /api/v1/products/activations/{activation_id}
```

#### 7. Check License Status (US4)

```bash
GET /api/v1/licenses/{license_key}/status
```

## Development

### Running Tests

```bash
# Run all tests
docker-compose run --rm app pytest

# Run with coverage
docker-compose run --rm app pytest --cov=. --cov-report=term

# Run specific test file
docker-compose run --rm app pytest tests/test_models.py
```

### Code Quality

```bash
# Format code
docker-compose run --rm app black .

# Sort imports
docker-compose run --rm app isort .

# Run linter
docker-compose run --rm app pylint --recursive=y .
```

### Database Migrations

```bash
# Create migrations
docker-compose run --rm app python manage.py makemigrations

# Apply migrations
docker-compose run --rm app python manage.py migrate
```

## Project Structure

```
license_service/
├── api/                    # API application
│   ├── authentication.py   # API key authentication
│   ├── v1/
│   │   ├── serializers/   # DRF serializers
│   │   ├── views/         # API views
│   │   └── urls.py        # URL routing
├── core/                  # Core business logic
│   ├── models/           # Database models
│   ├── services/         # Business logic layer
│   ├── exceptions.py     # Custom exceptions
│   └── admin.py          # Django admin config
├── tests/                # Test suite
│   ├── conftest.py       # pytest fixtures
│   ├── test_models.py
│   ├── test_services.py
│   └── test_api/
├── requirements/         # Python dependencies
│   ├── base.txt
│   ├── ci.txt
│   ├── dev.txt
│   └── prod.txt
├── docker/              # Docker configuration
├── .github/workflows/   # GitHub Actions CI/CD
└── manage.py
```

## Testing

The project includes comprehensive test coverage:

- **40 tests total**
- Unit tests for models and business logic
- Integration tests for API endpoints
- Test coverage for all core user stories (US1, US3, US4, US6)
- Test coverage for optional features (US2, US5)

All tests pass successfully:

```
========== 40 passed, 1 warning in 2.14s ==========
```

## CI/CD

GitHub Actions workflow runs on every push and pull request:

1. **Lint Job**: Runs black, isort, and pylint
2. **Test Job**: Runs full test suite with PostgreSQL service
3. **Coverage**: Generates coverage reports

## License

This is a technical assessment project.

## Documentation

For detailed architectural decisions, design trade-offs, and scaling considerations, see [Explanation.md](./Explanation.md).
