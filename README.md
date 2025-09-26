# 🗄️ Digital Safe API

Digital Safe — backend-service for keeping documents with limited time life or count downloads.
The files will delete automaticly after expiring storage conditions.

## API

### AUTH

    - POST /auth/register
        - json:
        {
            "email": "email@gmail.com", *required
            "password": "password123" *required
        }
    - POST /auth/login
        - json:
        {
            "email": "email@gmail.com", *required
            "password": "password123" *required
        }

### DOCUMENTS

    - POST /documents/upload
        - form-data:
        {
            "file": "file",
            "metadata": "{
                "max_downloads": count,
                "expires_at": timestamp,
                "password": "password for document"
            }"
        }
    - POST /documents/{id}/download
        - json:
        {
            "password": "password for document"
        }
    - GET /documents
    - GET /documents/{id}
    - DELETE /documents/{id}

## ✨ Functional

    - 🔐 Authorization (JWT).

    - 📤 Upload documents to MinIO with password (optional).

    - ⏳ Limitation on lifetime or number of downloads.

    - 📝 Logging access to documents.

    - 🗑️ Automatically cleaning of expired files (APScheduler).

## 🏗️ Technologies

- FastAPI - REST API
- PostgreSQL - Database
- SQLAlchemy - ORM
- MiniO - object file storage
- APScheduler - background tasks
- Docker - containerization

## 🔑 Env

```env
MODE=development

BACKEND_PORT=8000

STORAGE_HOST=minio
STORAGE_PORT=9000
STORAGE_CONSOLE_PORT=9001
STORAGE_PORT_EXTERNAL=9000
STORAGE_CONSOLE_PORT_EXTERNAL=9001
STORAGE_ACCESS_KEY=minioadmin
STORAGE_SECRET_KEY=minioadmin123

DB_USER=postgres
DB_PASS=password
DB_HOST=postgres
DB_PORT=5432
DB_PORT_EXTERNAL=5432
DB_NAME=expiresin

JWT_TOKEN=token
JWT_ACCESS_EXPIRES_IN=15 // minutes
JWT_REFRESH_EXPIRES_IN=7 // days

```

## 🔋 Start project (without Docker)

### Install project

```bash
git clone https://github.com/rashupkinbackend/ExpiresIn.git
```

### Change directory and install dependencies

```bash
cd ExpiresIn/ && pip install -r requirements.txt
```

### Start Server

```bash
uvicorn src.main:app
```

## 💡 Start project (with Docker)

### Install project

```bash
git clone https://github.com/rashupkinbackend/ExpiresIn.git
```

### Change directory and start containers

```bash
docker compose up --build
```
