# Web Search API

A simple API that uses Apify's RAG Web Browser Actor to search the web and extract content for use in LLM applications.

## Features

- Search for information about people, topics, or URLs
- Extract content from web pages in Markdown, plain text, or HTML format
- Configurable parameters for search depth, scraping tool, and more
- Easy integration with LLM applications

## Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/web-search-api.git
cd web-search-api
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file with your Apify API token:
```
APIFY_API_TOKEN=your_apify_api_token
```

4. Run the API:
```bash
python app.py
```

The API will be available at http://localhost:5000.

## API Endpoints

### Health Check

```
GET /health
```

Returns a simple status message to confirm the API is running.

### Person Search

```
POST /search
```

Search for information about a person.

**Request Body:**

```json
{
  "name": "Person Name",
  "context": "Additional context or questions (optional)",
  "max_results": 3
}
```

**Response:**

```json
{
  "query": "Person Name Additional context",
  "person_name": "Person Name",
  "sources": [
    {
      "url": "https://example.com/page1",
      "title": "Page Title 1"
    },
    ...
  ],
  "content": [
    "# Markdown content from source 1...",
    ...
  ]
}
```

### Raw Search

```
POST /raw-search
```

Perform a raw search with full control over parameters.

**Request Body:**

```json
{
  "query": "Search query or URL",
  "max_results": 3,
  "scraping_tool": "browser-playwright",
  "output_format": "markdown",
  "request_timeout_secs": 40,
  "dynamic_content_wait_secs": 1.0,
  "remove_cookie_warnings": true,
  "debug_mode": false
}
```

**Response:**
```json
[
  {
    "searchResult": {
      "title": "Result Title",
      "description": "Result Description",
      "url": "https://example.com/page"
    },
    "metadata": {
      "title": "Page Title",
      "url": "https://example.com/page"
    },
    "markdown": "# Page Content in Markdown"
  },
  ...
]
```

## Testing with cURL

### Person Search:
```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"name": "Elon Musk", "context": "SpaceX"}'
```

### Raw Search:
```bash
curl -X POST http://localhost:5000/raw-search \
  -H "Content-Type: application/json" \
  -d '{"query": "openai.com", "max_results": 1}'
```

## License

MIT