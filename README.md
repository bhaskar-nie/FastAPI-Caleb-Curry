# FastAPI Campaign CRUD API

A simple CRUD API built using FastAPI, SQLModel, and SQLite.

## Features

* Create campaigns
* Read campaigns
* Update campaigns
* Delete campaigns
* SQLite database integration
* Auto-generated Swagger docs

## Tech Stack

* Python
* FastAPI
* SQLModel
* SQLite
* Pydantic

## Run the Project

Install dependencies:

```bash
pip install fastapi uvicorn sqlmodel
```

Start the server:

```bash
uvicorn main:app --reload
```

## API Docs

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## Database

SQLite database file:

```text
database.db
```

Tables are automatically created during application startup.

## Available Endpoints

```http
GET    /campaigns
GET    /campaigns/{id}
POST   /campaigns
PUT    /campaigns/{campaign_id}
DELETE /campaigns/{id}
```

## Notes

* Uses SQLModel ORM for database operations.
* Uses FastAPI dependency injection for database sessions.
* Uses lifespan events to initialize database tables and seed data.
* `created_at` is automatically generated server-side.
