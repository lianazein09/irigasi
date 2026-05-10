# Project Irigasi

## Production Deployment With Docker

This repository now includes a production-oriented Docker setup for:

- `frontend`: React app built with Vite and served by Nginx
- `backend`: Django API served by Gunicorn
- `db`: MariaDB initialized from `backend/database.sql`
- `mqtt-worker`: dedicated MQTT consumer process

### Files Added

- `docker-compose.yml`
- `Dockerfile`
- `docker/nginx/default.conf`
- `backend/Dockerfile`
- `backend/entrypoint.sh`
- `backend/requirements.txt`
- `.env.example`

### First Run

```bash
cp .env.example .env
docker compose up --build
```

The application will be available on `http://localhost` by default.

### Notes

- Frontend API calls now use a configurable base URL and default to `/api`, which is proxied by Nginx to Django.
- Update `.env` before real production deployment, especially:
  - `DJANGO_SECRET_KEY`
  - `DJANGO_ALLOWED_HOSTS`
  - `CORS_ALLOWED_ORIGINS`
  - `CSRF_TRUSTED_ORIGINS`
  - database passwords
- The MQTT consumer runs in a separate container to avoid duplicate subscriptions under Gunicorn workers.
