# KameArt Forms — Copilot Instructions

## Stack
- **Backend**: FastAPI + Python 3.12, Pydantic v2, sync services
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS

## Development Principles

### SOLID
- Each service has a single responsibility (`DriveService`, `PdfService`, `EmailService`, `MongoService`).
- Services are injected/used as module-level singletons — extend by adding methods, not by modifying callers.
- `ConsentService` orchestrates; it never directly calls external APIs.

### DRY
- Shared logic lives in helpers (`_safe_name`, `_generate_reference`) — never duplicate.
- Config values always come from `settings` (never hardcoded).
- Reuse `drive_service._upload_bytes` for any new file type.

### KISS
- Prefer stdlib over third-party where possible (e.g. `smtplib`, `ssl`, `uuid`).
- Each service method does one thing and returns a clear value.
- No abstract classes or interfaces for services with a single implementation.
- New features go into a dedicated service file — do not bloat existing ones.

## Coding Rules
- All new settings → `app/core/config.py` (`Settings` class).
- All new dependencies → `requirements.txt` with pinned versions.
- Services are sync; route handlers are async (FastAPI runs sync services in a thread pool).
- Secondary services (email, mongo) must fail silently — they must NOT break the main flow.
- Never log or expose credential values; log errors with context only.
- Validate at model level (Pydantic) — do not duplicate validation in service layer.

## File / Folder Conventions
```
app/
  api/routes/   — FastAPI routers only (no business logic)
  core/         — config, shared utilities
  models/       — Pydantic request/response models
  services/     — one file per integration (drive, pdf, email, mongo, consent)
```
