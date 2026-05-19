# Project Irigasi

## Production Deployment With Docker

This repository now includes a production-oriented Docker setup for:

- `frontend`: React app built with Vite and served by Nginx
- `backend`: Django API served by Gunicorn
- `db`: MariaDB/MySQL initialized from `backend/database.sql`
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
make deploy ENV_FILE=.env
```

The application will be available on `http://localhost:8081` by default.

### Makefile Commands

The project includes a `Makefile` so you can run deployment commands more consistently.

```bash
make deploy
make up
make down
make logs
make clean
```

By default the `Makefile` uses `.env`. To use another env file:

```bash
make deploy ENV_FILE=.env.example
```

### Notes

- Frontend API calls now use a configurable base URL and default to `/api`, which is proxied by Nginx to Django.
- The stack is mapped to host port `8081` by default so it does not compete with another project already using port `80`. Change `APP_PORT` in `.env` if needed.
- The database runtime defaults to MySQL/MariaDB.
- The MariaDB container creates the application database user from `.env` via `DB_USER` and `DB_PASSWORD`, with access to `DB_NAME`.
- On backend startup, `ensure_mysql_access.py` re-checks that user during deploy and re-deploy, recreates it if missing, and reapplies grants on `DB_NAME`.
- Update `.env` before real production deployment, especially:
  - `DJANGO_SECRET_KEY`
  - `DJANGO_ALLOWED_HOSTS`
  - `CORS_ALLOWED_ORIGINS`
  - `CSRF_TRUSTED_ORIGINS`
  - `DB_PASSWORD` and `DB_ROOT_PASSWORD`
- The MQTT consumer runs in a separate container to avoid duplicate subscriptions under Gunicorn workers.
