# Behalysis API

REST API backend for a computer-vision startup that evaluates students' attention during lessons.

## Tech Stack

- **Python 3.11+** / **FastAPI** / **Pydantic v2**
- **SQLAlchemy 2.0** (async) + **asyncpg** + **PostgreSQL**
- **Alembic** migrations
- **Docker** + **docker-compose**

## Quick Start (Docker)

```bash
# Copy env template
cp .env.example .env

# Build & start (runs Alembic migrations automatically)
docker-compose up --build

# API available at http://localhost:8000
# OpenAPI docs at http://localhost:8000/docs
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL (or use docker-compose up db)
docker-compose up -d db

# Copy env
cp .env.example .env

# Run migrations
alembic upgrade head

# Start dev server
uvicorn app.main:app --reload
```

## Run Tests

Tests use an in-memory SQLite database, no PostgreSQL required:

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## API Endpoints

### Schools
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/schools` | Create school |
| GET | `/schools` | List schools |
| GET | `/schools/{school_id}` | Get school |
| PUT | `/schools/{school_id}` | Update school |
| DELETE | `/schools/{school_id}` | Delete school |

### Classes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/classes` | Create class |
| GET | `/classes?school_id=` | List classes |
| GET | `/classes/{class_id}` | Get class |
| PUT | `/classes/{class_id}` | Update class |
| DELETE | `/classes/{class_id}` | Delete class |

### Students
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/students` | Create student |
| GET | `/students?class_id=` | List students |
| GET | `/students/{student_id}` | Get student |
| PUT | `/students/{student_id}` | Update student |
| DELETE | `/students/{student_id}` | Delete student |

### Lesson Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/lesson-reports` | Create report (CV payload) |
| GET | `/lesson-reports?school_id=&class_id=&date_from=&date_to=&limit=&offset=` | List reports |
| GET | `/lesson-reports/{report_id}` | Get full report |
| PUT | `/lesson-reports/{report_id}` | Update report |
| DELETE | `/lesson-reports/{report_id}` | Delete report |
| GET | `/classes/{class_id}/lesson-reports/latest` | Latest report for class |

### Images
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/images/{report_id}/{filename}` | Download student image |

## Example: Post Lesson Report

```bash
curl -X POST http://localhost:8000/lesson-reports \
  -H "Content-Type: application/json" \
  -d '{
    "class_id": 12345678,
    "school_id": 87654321,
    "class_index": "8-E",
    "lesson_time": "09:30:00",
    "lesson_date": "2026-02-15",
    "students_count": 2,
    "students": [
      {
        "student_id": 11112222,
        "name": "Alice",
        "image": "<base64-encoded-image>",
        "attention": 85
      }
    ],
    "unrecognized_students": [
      {
        "image": "<base64-encoded-image>",
        "attention": 60
      }
    ]
  }'
```

## Project Structure

```
app/
  main.py                     # FastAPI app entrypoint
  core/
    config.py                 # Settings (pydantic-settings)
    logging.py                # Logging configuration
  db/
    session.py                # Async engine + session
    base.py                   # Declarative base
  models/                     # SQLAlchemy ORM models
  schemas/                    # Pydantic v2 schemas
  services/                   # Business logic layer
  api/
    deps.py                   # FastAPI dependencies
    routers/                  # API route handlers
  utils/
    images.py                 # Image handling utilities
migrations/                   # Alembic migrations
tests/                        # Pytest test suite
```

## Domain Rules

- **IDs**: School, class, and student IDs must be 8-digit integers (10000000–99999999).
- **Attention**: Score from 1–100. Inattention = 100 − attention.
- **students_count** must equal `len(students) + len(unrecognized_students)`.
- **Images**: Base64-encoded, max 2 MB decoded. Stored on disk, served via `/images/` endpoint.
- **Auto-upsert**: Posting a lesson report auto-creates School/ClassRoom/Student records if they don't exist.
