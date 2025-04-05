# Search RAG MCP Server

A powerful Model Context Protocol (MCP) server that leverages Apify's RAG Web Browser Actor to search the web and extract content for use with LLMs. This server enables Claude for Desktop and other MCP clients to search for information about people, topics, or specific URLs, making it ideal for retrieval-augmented generation workflows.

## Features

- **Person Search Tool**: Search for detailed information about a person
- **Social Media Discovery**: Find and extract X/Twitter, Instagram, and Facebook accounts
- **Raw Search Tool**: Direct web search with customizable parameters
- **MCP Integration**: Works with Claude for Desktop and other MCP clients
- **Flexible Output Formats**: Get content in Markdown, plain text, or HTML

## Project Structure

```
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── .gitignore              # Git ignore rules
├── search_rag.py           # Main MCP server implementation
├── app.py                  # Flask API implementation (non-MCP version)
├── test_api.py             # General API test script
├── test_x_account.py       # X/Twitter account retrieval tests
├── test_x_content.py       # X/Twitter content extraction tests
├── search_by_username.py   # Script to find info from X/Twitter usernames
└── apify_rag/              # Apify client module
    ├── __init__.py         # Package initialization
    └── client.py           # Apify client implementation
```

## Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/search-rag.git
cd search-rag
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

4. Run the MCP server:
```bash
python search_rag.py
```

## Using with Claude for Desktop

1. Install [Claude for Desktop](https://claude.ai/desktop)

2. Configure Claude for Desktop to use your Search RAG MCP server by editing the configuration file at:
   - MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

3. Add your server configuration:
```json
{
    "mcpServers": {
        "search-rag": {
            "command": "python",
            "args": [
                "/ABSOLUTE/PATH/TO/search-rag.py"
            ]
        }
    }
}
```

4. Restart Claude for Desktop. The Search RAG tools should appear in the tools menu (hammer icon).

## MCP Tools

### Person Search

Search for information about a person and their social media profiles.

**Parameters:**
- `name` (string): Person name to search for
- `context` (string, optional): Additional context or questions about the person
- `max_results` (integer, optional): Maximum number of search results (default: 3)
- `focus_x_account` (boolean, optional): Focus on finding the person's X/Twitter account (default: false)

### Raw Search

Perform a direct web search with full control over parameters.

**Parameters:**
- `query` (string): Search query or URL
- `max_results` (integer, optional): Maximum number of search results (default: 3)
- `scraping_tool` (string, optional): Tool to use for scraping, either 'browser-playwright' or 'raw-http' (default: 'browser-playwright')
- `output_format` (string, optional): Format for the extracted content - 'markdown', 'text', or 'html' (default: 'markdown')

## Traditional API Endpoints (Non-MCP)

If you prefer to use the traditional REST API rather than MCP, you can run the server with:

```bash
python app.py
```

The API will be available at http://localhost:8080.

### Health Check

```
GET /health
```

Returns a simple status message to confirm the API is running.

**Response:**
```json
{
  "status": "ok",
  "message": "API is running"
}
```

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
  "max_results": 3,
  "focus_x_account": false
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
  "output_format": "markdown"
}
```

## Utility Scripts

### API Testing

```bash
python test_api.py
```

### X/Twitter Account Discovery

```bash
python test_x_account.py "Person Name"
```

### X/Twitter Content Extraction

```bash
python test_x_content.py "Person Name"
```

### Search by X/Twitter Username

```bash
python search_by_username.py username
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| APIFY_API_TOKEN | Your Apify API token | Yes |

## Troubleshooting

### Claude for Desktop Integration Issues

- Ensure you've configured the `claude_desktop_config.json` file correctly
- Make sure the path to your `search_rag.py` file is correct and absolute
- Check that Claude for Desktop is restarted after configuration
- Look for the hammer icon in Claude for Desktop to access the tools

### API Issues

- Verify your Apify API token is correct
- Ensure you have an active internet connection
- Check that the request parameters are valid

## Next Steps

- Try more complex search queries
- Integrate with other MCP clients
- Customize the search behavior for specific use cases

## License

MIT