from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from apify_rag import ApifyRagWebBrowserClient

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize the Apify RAG Web Browser client
apify_client = ApifyRagWebBrowserClient()

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "ok", "message": "API is running"})

@app.route('/search', methods=['POST'])
def search_person():
    """
    Search for information about a person
    
    Request body:
    {
        "name": "Person Name",
        "context": "Additional context or questions (optional)",
        "max_results": 3 (optional, default is 3)
    }
    """
    data = request.json
    if not data or 'name' not in data:
        return jsonify({"error": "Please provide a 'name' in the request body"}), 400
    
    name = data['name']
    additional_context = data.get('context', '')
    max_results = data.get('max_results', 3)
    
    try:
        result = apify_client.search_for_person(name, additional_context, max_results)
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Error searching for person: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/raw-search', methods=['POST'])
def raw_search():
    """
    Perform a raw search with full control over parameters
    
    Request body:
    {
        "query": "Search query or URL",
        "max_results": 3 (optional),
        "scraping_tool": "browser-playwright" or "raw-http" (optional),
        "output_format": "markdown", "text", or "html" (optional),
        "request_timeout_secs": 40 (optional),
        "dynamic_content_wait_secs": 1.0 (optional),
        "remove_cookie_warnings": true (optional),
        "debug_mode": false (optional)
    }
    """
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Please provide a 'query' in the request body"}), 400
    
    query = data['query']
    max_results = data.get('max_results', 3)
    scraping_tool = data.get('scraping_tool', 'browser-playwright')
    output_format = data.get('output_format', 'markdown')
    request_timeout_secs = data.get('request_timeout_secs', 40)
    dynamic_content_wait_secs = data.get('dynamic_content_wait_secs', 1.0)
    remove_cookie_warnings = data.get('remove_cookie_warnings', True)
    debug_mode = data.get('debug_mode', False)
    
    try:
        result = apify_client.search(
            query=query,
            max_results=max_results,
            scraping_tool=scraping_tool,
            output_format=output_format,
            request_timeout_secs=request_timeout_secs,
            dynamic_content_wait_secs=dynamic_content_wait_secs,
            remove_cookie_warnings=remove_cookie_warnings,
            debug_mode=debug_mode
        )
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Error performing raw search: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)