# Security checklist

Status of basic security controls in this project (backend: FastAPI, frontend: React).

## Implemented

### Authentication
- [x] Passwords hashed with Argon2 (`pwdlib`), per-user salt — `app/security.py`
- [x] JWT access tokens, HS256 pinned (no `alg: none`), `exp`/`sub` required, 30 min lifetime — `app/security.py`
- [x] `JWT_SECRET_KEY` must be ≥ 32 chars when `APP_ENV=prod` — `app/config.py`
- [x] No email/password in token payload; only `sub` (user id), `role`, `iat`, `exp`
- [x] Same error for unknown email / wrong password + dummy hash verify (no user enumeration by message or timing) — `app/services/auth_service.py`
- [x] Login rate limit: 5 attempts / minute per (client IP, email) → 429 + `Retry-After` — `app/rate_limit.py`, `app/dependencies.py`
- [x] Email ≤ 254 and password ≤ 128 chars checked before hashing (no hashing DoS)

### Authorization
- [x] Every `/orders` endpoint requires a valid token — `app/dependencies.get_current_user`
- [x] User and role re-read from the DB on every request (deactivated or demoted users lose access immediately)
- [x] `GET /orders` admin only (403 for customers) — `require_admin`
- [x] Customers see only their own orders (`orders.user_id`); someone else's order returns the same 404 as a missing one — `app/services/order_service.get_order_for`
- [x] Frontend route guard for `/admin` is UX only; the backend enforces access

### Input validation
- [x] Request/response shapes via Pydantic; responses filtered by `response_model` (no `hashed_password` leaks)
- [x] `order_id` path allowlist `^[A-Za-z0-9-]+$`, max 32 chars → 422 — `app/routers/orders.py`
- [x] DB constraints: unique email, role CHECK, foreign key `orders.user_id → users.id`
- [x] SQLAlchemy parameterised queries only (no string-built SQL)

### Errors and logging
- [x] One error shape `{detail, request_id}`; 500 returns a generic message, details only in server logs — `app/errors.py`, `app/main.py`
- [x] `X-Request-ID` validated (no log injection) and exposed to the frontend for support
- [x] No personal data in logs (user id / order id only)

### HTTP hardening
- [x] CORS: only `FRONTEND_ORIGIN`, methods `GET`/`POST`, headers `Authorization`/`Content-Type`/`X-Request-ID`
- [x] Security headers on every response: `nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `Cache-Control: no-store`
- [x] Swagger / ReDoc / OpenAPI disabled when `APP_ENV=prod`

### Secrets
- [x] Secrets only in `backend/.env` (git-ignored); `.env.example` has placeholders
- [x] Demo users seeded only outside prod, password from `SEED_DEMO_PASSWORD`

## Known gaps / next steps
- [ ] HTTPS + `Strict-Transport-Security` (with nginx in the Docker step)
- [ ] `Content-Security-Policy`
- [ ] Rate limiter is in-memory (per process) → move to Redis when running several workers
- [ ] JWT stored in `localStorage` (readable by XSS) → consider `httpOnly` cookie + CSRF protection
- [ ] No refresh tokens / token revocation list; logout only clears the client
- [ ] Chat agent guest order lookup must require order id **and** email, with rate limit (avoid IDOR)
- [ ] Frontend dev dependencies: Vite/esbuild dev-server advisories (needs Vite major upgrade)
- [ ] Automated dependency scanning (e.g. `pip-audit`, `npm audit` in CI)

## Reporting a vulnerability
This is a learning project. Please open a private security advisory on GitHub instead of a public issue.
