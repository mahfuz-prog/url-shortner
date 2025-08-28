# FastAPI URL Shortener

## High-Level Architecture



## Overview

The design is inspired by real-world production systems like Bitly, but simplified to demonstrate low latency distributed system concepts and scalable backend engineering skills.

* Create short links.
* Track clicks in real-time.
* Handle high concurrency without compromising performance.


### Backend (FastAPI)

* **FastAPI** for building high-performance async APIs.
* **BASE62 Encoding** 62^10 combination with 62 symbols (0–9, a–z, A–Z), a 10-character code space.
* **PyJWT** - Authentication via JSON Web Tokens.
* **Passlib + Bcrypt** – Password hashing & security.
* **SQLAlchemy** – ORM
* **PostgreSQL** as the persistent data store.
* **Redis** for in-memory caching, click tracking.
* **Background Workers** for syncing click from Redis to the database.
* **Nginx + Uvicorn** for production-grade API serving.


### Testing

* **Pytest** – Unit and end-to-end testing.

### Scalability

* **Read-heavy workload optimization** → Shortcode lookups are cached in Redis.
* **Write-heavy workload optimization** → Analytics (clicks) stored in Redis and synced in batches..
* **Asynchronous I/O** → FastAPI handles thousands of concurrent requests.
* **Horizontal Scaling** → Stateless API servers behind load balancers.

### Export config variable .env
```sh
DATABASE_URL=sqlite:///./project.db
SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1000
SERVER_ADDRESS=http://localhost:8000
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
SHORTCODE_EXPIRE_SECONDS=86400
CLICKS_EXPIRE_SECONDS=86400
```