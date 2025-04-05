#!/usr/bin/env python3
"""
Search RAG MCP Server

A Model Context Protocol server that provides web search capabilities using Apify's
RAG Web Browser Actor. This server enables Claude for Desktop and other MCP clients 
to search for information about people, topics, or specific URLs.
"""
import os
import sys
import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Check for required environment variables
api_token = os.environ.get("APIFY_API_TOKEN")
if not api_token:
    logger.error("APIFY_API_TOKEN environment variable is not set. Please set it in .env file or export it.")
    logger.info("Example: export APIFY_API_TOKEN=your_apify_api_token")
    sys.exit(1)

# Import client after checking for API token
from apify_rag import ApifyRagWebBrowserClient

# Initialize FastMCP server
mcp = FastMCP("search-rag")

# Initialize the Apify RAG Web Browser client
try:
    logger.info("Initializing Apify RAG Web Browser client...")
    apify_client = ApifyRagWebBrowserClient(api_token=api_token)
    logger.info("Client initialized successfully!")
except Exception as e:
    logger.error(f"Error initializing Apify client: {str(e)}")
    sys.exit(1)

@mcp.tool()
async def person_search(
    name: str, 
    context: str = "", 
    max_results: int = 3, 
    focus_x_account: bool = False
) -> str:
    """
    Search for information about a person and their social media profiles.
    
    Args:
        name: Name of the person to search for
        context: Additional context or specific questions about the person
        max_results: Maximum number of search results to process (default: 3)
        focus_x_account: If True, focuses on finding the person's X/Twitter account (default: False)
        
    Returns:
        Formatted information about the person including content and social media links
    """
    logger.info(f"MCP person search request: name='{name}', context='{context}', max_results={max_results}, focus_x_account={focus_x_account}")
    
    try:
        # Call the Apify client to search for the person
        result = apify_client.search_for_person(
            name=name, 
            additional_context=context, 
            max_results=max_results,
            focus_x_account=focus_x_account
        )
        
        logger.info(f"Search completed successfully. Found {len(result.get('sources', []))} sources.")
        if result.get('social_links', {}).get('x_twitter'):
            logger.info(f"Found X/Twitter account: {result['social_links']['x_twitter']}")
        
        # Format the result as a readable string
        formatted_output = f"# Information about {name}\n\n"
        
        # Add social media links if available
        social_links = result.get('social_links', {})
        if any(social_links.values()):
            formatted_output += "## Social Media\n"
            if social_links.get('x_twitter'):
                formatted_output += f"- X/Twitter: {social_links['x_twitter']}\n"
            if social_links.get('instagram'):
                formatted_output += f"- Instagram: {social_links['instagram']}\n"
            if social_links.get('facebook'):
                formatted_output += f"- Facebook: {social_links['facebook']}\n"
            formatted_output += "\n"
        
        # Add sources
        if result.get('sources'):
            formatted_output += "## Sources\n"
            for i, source in enumerate(result['sources'], 1):
                formatted_output += f"{i}. [{source.get('title', 'Untitled')}]({source.get('url', '#')})\n"
            formatted_output += "\n"
        
        # Add content
        if result.get('content'):
            formatted_output += "## Content\n"
            for i, content in enumerate(result['content'], 1):
                # Add a source reference if available
                source_ref = f" (Source: {i})" if i <= len(result.get('sources', [])) else ""
                formatted_output += f"### Content {i}{source_ref}\n\n{content}\n\n"
        
        return formatted_output
    
    except Exception as e:
        error_msg = f"Error searching for person: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"

@mcp.tool()
async def raw_search(
    query: str,
    max_results: int = 3,
    scraping_tool: str = "browser-playwright",
    output_format: str = "markdown"
) -> str:
    """
    Perform a raw search with full control over parameters.
    
    Args:
        query: Search query or URL to scrape
        max_results: Maximum number of search results to process (default: 3)
        scraping_tool: Tool used for scraping, either 'browser-playwright' or 'raw-http' (default: 'browser-playwright')
        output_format: Format of the extracted content - 'markdown', 'text', or 'html' (default: 'markdown')
        
    Returns:
        Formatted search results from the web
    """
    logger.info(f"MCP raw search request: query='{query}', max_results={max_results}, tool={scraping_tool}")
    
    # Validate parameters
    if scraping_tool not in ["browser-playwright", "raw-http"]:
        return "Error: scraping_tool must be either 'browser-playwright' or 'raw-http'"
    
    if output_format not in ["markdown", "text", "html"]:
        return "Error: output_format must be either 'markdown', 'text', or 'html'"
    
    try:
        # Call the Apify client to perform the search
        results = apify_client.search(
            query=query,
            max_results=max_results,
            scraping_tool=scraping_tool,
            output_format=output_format,
            request_timeout_secs=40,
            dynamic_content_wait_secs=1.0,
            remove_cookie_warnings=True,
            debug_mode=False
        )
        
        logger.info(f"Search completed successfully. Found {len(results)} results.")
        
        # Format the results as a readable string
        formatted_output = f"# Search Results for '{query}'\n\n"
        
        for i, result in enumerate(results, 1):
            # Get the title and URL from the result
            title = (result.get('metadata', {}).get('title') or 
                    result.get('searchResult', {}).get('title') or 
                    f"Result {i}")
            
            url = (result.get('metadata', {}).get('url') or 
                  result.get('searchResult', {}).get('url') or 
                  "No URL available")
            
            formatted_output += f"## {i}. {title}\n"
            formatted_output += f"Source: {url}\n\n"
            
            # Add the content based on the selected output format
            if output_format == "markdown" and "markdown" in result:
                formatted_output += f"{result['markdown']}\n\n"
            elif output_format == "text" and "text" in result:
                formatted_output += f"```\n{result['text']}\n```\n\n"
            elif output_format == "html" and "html" in result:
                formatted_output += f"HTML content available but not displayed in this view.\n\n"
            else:
                description = result.get('searchResult', {}).get('description', "No description available")
                formatted_output += f"{description}\n\n"
                
            formatted_output += "---\n\n"
        
        if not results:
            formatted_output += "No results found for this query.\n"
            
        return formatted_output
    
    except Exception as e:
        error_msg = f"Error performing raw search: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"

if __name__ == "__main__":
    # Initialize and run the MCP server
    logger.info("Starting Search RAG MCP Server...")
    mcp.run(transport='stdio') 