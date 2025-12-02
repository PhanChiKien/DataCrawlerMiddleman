# Crawler Middleware API

A simple FastAPI middleware service for web crawlers to check for duplicate URLs and deposit crawled data.

## Features

- **Check URL**: Verify if a URL has already been crawled
- **Deposit Data**: Store crawled data for a URL
- **Stats**: Get statistics about total crawled URLs
- **Auto Documentation**: Swagger UI available at `/docs`

## Setup

1. **Install dependencies**:
```powershell
pip install -r requirements.txt
```

2. **Configure database**:
   - Copy `.env.example` to `.env`
   - Update the `DATABASE_URL` with your PostgreSQL credentials:
```
DATABASE_URL=postgresql://username:password@localhost:5432/your_database
```

3. **Run the application**:
```powershell
python main.py
```

Or with uvicorn:
```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Check if URL is crawled
```
POST /check
Body: {"url": "https://example.com"}
Response: {"url": "...", "is_crawled": true/false, "crawled_at": "..."}
```

### Deposit crawled data
```
POST /deposit
Body: {"url": "https://example.com", "data": "{json_data}", "crawler_id": "crawler_1"}
Response: {"url": "...", "success": true, "message": "...", "crawled_at": "..."}
```

### Get statistics
```
GET /stats
Response: {"total_crawled_urls": 123}
```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Schema

**Table: `crawled_urls`**
- `id`: Primary key
- `url`: Unique URL (indexed)
- `crawled_at`: Timestamp
- `data`: Crawled data (stored as text/JSON)
- `crawler_id`: Identifier for the crawler
