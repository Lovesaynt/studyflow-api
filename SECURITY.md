# Security Policy

## Supported Versions

Currently, security updates are provided for the latest release branch.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in StudyFlow, please report it responsibly.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them by emailing the project maintainers at:

**[Insert security contact email here]**

Include the following information in your report:

1. **Description**: A clear description of the vulnerability
2. **Impact**: The potential impact of the vulnerability
3. **Reproduction Steps**: Steps to reproduce the vulnerability
4. **Proof of Concept**: If applicable, a proof of concept or exploit code
5. **Suggested Fix**: If you have a suggested fix, please include it

### What to Expect

- We will acknowledge receipt of your report within 48 hours
- We will provide a preliminary assessment within 5 business days
- We will work with you to understand and validate the vulnerability
- We will coordinate a fix and disclosure timeline

## Security Considerations

### Authentication & Authorization

- Passwords are hashed using Argon2 (via passlib)
- JWT tokens use HS256 algorithm with configurable expiration (default: 30 minutes)
- All endpoints require authentication except `/health`, `/`, `/docs`, `/redoc`, `/openapi.json`
- User data isolation is enforced at the database level (all queries filter by `user_id`)

### Input Validation

- All inputs validated using Pydantic v2 schemas
- SQL injection prevention via SQLAlchemy ORM (no raw SQL in application code)
- Request size limits enforced by the web server

### Rate Limiting

- Global rate limit: 100 requests/minute per IP
- Authentication endpoints have stricter limits:
  - Registration: 5 requests/minute
  - Login: 10 requests/minute

### Security Headers

The following security headers are applied to all responses:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (production only)

### CORS

CORS is disabled by default. Configure allowed origins via the `CORS_ORIGINS` environment variable.

### Secrets Management

- Never commit `.env` files or secrets to version control
- Use `.env.example` as a template for configuration
- Production JWT secrets must be strong random values (minimum 32 characters)
- Rotate secrets periodically

### Docker Security

- Container runs as non-root user
- Minimal base image (python:3.12-slim)
- Only necessary system dependencies installed
- Health checks configured for database and API

## Best Practices for Users

1. **Use strong, unique passwords**
2. **Keep your JWT secret secure** - rotate periodically
3. **Enable HTTPS in production** - use a reverse proxy (nginx, Traefik) with TLS
4. **Configure CORS origins explicitly** - avoid wildcards
5. **Monitor logs** for suspicious activity
6. **Keep dependencies updated** - run `pip-audit` periodically
7. **Use environment-specific configurations** - separate dev/staging/prod

## Security Audit

The codebase has been reviewed for:

- [x] Password hashing (Argon2)
- [x] JWT token handling (HS256, expiration, validation)
- [x] SQL injection prevention (SQLAlchemy ORM)
- [x] Input validation (Pydantic v2)
- [x] User data isolation
- [x] Rate limiting
- [x] Security headers
- [x] CORS configuration
- [x] Secret management
- [x] Docker security practices

## Disclosure Policy

When a security vulnerability is confirmed:

1. We will develop a fix
2. We will release a patch version
3. We will disclose the vulnerability publicly after the fix is available
4. We will credit the reporter (unless anonymity is requested)

## Contact

For security-related questions or concerns, contact the maintainers at:

**[Insert security contact email here]**

---

*This security policy is inspired by GitHub's security policy template.*