# ifinder

ifinder is an image search engine powered by OpenAI's CLIP model and PostgreSQL with pgvector extension. It allows you to index images, search for relevant images using text queries, and record user feedback.

## Features

- FastAPI web API
- CLIP embedding via HuggingFace transformers
- PostgreSQL + pgvector for vector search
- Dockerized deployment
- Static image serving

## Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/yachuntsai/ifinder.git
cd ifinder
```

### 2. Prepare your image dataset

- Place your images in `./data/dataset/` (jpg/png/webp/bmp/gif).

### 3. Run with Docker Compose

```bash
cd docker
docker compose up --build
```

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Adminer (DB UI): http://localhost:8080

### 4. Migrate the database

Database migrations are run automatically on container startup. To run manually:

```bash
alembic upgrade head
```

Disable automatic migrations by setting the environment variable `ENABLE_MIGRATION` to "false" in the `docker-compose.yaml`.

```
environment:
  ENABLE_MIGRATION: "false"
```

### 5. Index images

**From a folder** (mounted into the container at `/data/dataset`):

```bash
curl -X POST http://localhost:8000/images/ingestions \
     -H "Content-Type: application/json" \
     -d '{"folder": "/data/dataset"}'
```

### 6. Search for images

```bash
curl -X 'GET' \
  'http://localhost:8000/images/search?query=a%20cat&top_k=1' \
  -H 'accept: application/json'
```

Response:

```json
{
  "query": "a cat",
  "results": [
    {"id": 1, "filename": "cat.jpg", "url": "http://localhost:8000/static/image/cat.jpg", "score": 0.28},
    ...
  ]
}
```

### 7. Record feedback

```bash
curl -X POST http://localhost:8000/feedbacks \
     -H "Content-Type: application/json" \
     -d '{"query_text":"a cat","image_id":1,"is_good":true,"score":0.28}'
```

### 8. View images and feedbacks

- List images:  
  `GET http://localhost:8000/images`
- List feedbacks:  
  `GET http://localhost:8000/feedbacks`

## API Endpoints

- `POST /images/ingestions` — Index images from a folder
- `GET /images/search` — Search images by text query
- `POST /feedbacks` — Submit feedback
- `GET /images` — List all images
- `GET /feedbacks` — List feedbacks

## License

MIT