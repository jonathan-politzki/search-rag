import os
import json
import re
import requests
from typing import List, Dict, Any, Optional, Union

class ApifyRagWebBrowserClient:
    """
    A client for interacting with Apify's RAG Web Browser Actor to search the web
    and extract content for use in LLM applications.
    """
    
    def __init__(self, api_token: str = None):
        """
        Initialize the API client with your Apify API token.
        
        Args:
            api_token (str, optional): Your Apify API token. If not provided,
                                      will try to read from APIFY_API_TOKEN env variable.
        """
        self.api_token = api_token or os.environ.get("APIFY_API_TOKEN")
        if not self.api_token:
            raise ValueError("API token must be provided or set as APIFY_API_TOKEN environment variable")
        
        # Base URL for the RAG Web Browser Actor in standby mode
        self.base_url = "https://rag-web-browser.apify.actor"
    
    def search(self, 
               query: str,
               max_results: int = 3,
               scraping_tool: str = "browser-playwright",
               output_format: str = "markdown",
               request_timeout_secs: int = 40,
               dynamic_content_wait_secs: float = 1.0,
               remove_cookie_warnings: bool = True,
               debug_mode: bool = False) -> List[Dict[str, Any]]:
        """
        Search the web for information about a given query.
        
        Args:
            query (str): The search query or a specific URL to scrape
            max_results (int, optional): Maximum number of search results to process. Defaults to 3.
            scraping_tool (str, optional): Tool used for scraping, either 'browser-playwright' or 'raw-http'. 
                                         Defaults to 'browser-playwright'.
            output_format (str, optional): Format of the extracted content. Options: 'markdown', 'text', 'html'. 
                                         Defaults to 'markdown'.
            request_timeout_secs (int, optional): Request timeout in seconds. Defaults to 40.
            dynamic_content_wait_secs (float, optional): Wait time for dynamic content to load. Defaults to 1.0.
            remove_cookie_warnings (bool, optional): Whether to remove cookie warnings. Defaults to True.
            debug_mode (bool, optional): Enable debug mode to see performance metrics. Defaults to False.
        
        Returns:
            List[Dict[str, Any]]: A list of extracted content from web pages
        """
        params = {
            'token': self.api_token,
            'query': query,
            'maxResults': max_results,
            'scrapingTool': scraping_tool,
            'outputFormat': output_format,
            'requestTimeoutSecs': request_timeout_secs,
            'dynamicContentWaitSecs': dynamic_content_wait_secs,
            'removeCookieWarnings': str(remove_cookie_warnings).lower(),
            'debugMode': str(debug_mode).lower()
        }
        
        response = requests.get(f"{self.base_url}/search", params=params)
        
        # Handle response
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"Error {response.status_code}: {response.text}"
            raise Exception(error_msg)
    
    def search_for_person(self, 
                          name: str, 
                          additional_context: str = "",
                          max_results: int = 3,
                          focus_x_account: bool = False) -> Dict[str, Any]:
        """
        Search for information about a person and format the results.
        
        Args:
            name (str): The name of the person to search for
            additional_context (str, optional): Additional context or specific questions about the person
            max_results (int, optional): Maximum number of search results to process. Defaults to 3.
            focus_x_account (bool, optional): If True, focuses on finding the person's X (Twitter) account
        
        Returns:
            Dict[str, Any]: Formatted results about the person
        """
        # Construct a search query that includes the name and any additional context
        if focus_x_account:
            query = f"{name} X twitter account @"
        elif additional_context:
            query = f"{name} {additional_context}"
        else:
            query = name
        
        # Perform the search
        search_results = self.search(
            query=query,
            max_results=max_results,
            scraping_tool="browser-playwright",  # Use browser for better results with person searches
            output_format="markdown",
            dynamic_content_wait_secs=3.0  # Increase wait time for dynamic content like X
        )
        
        # Extract and format the results
        formatted_results = {
            "query": query,
            "person_name": name,
            "sources": [],
            "content": [],
            "social_links": {
                "x_twitter": None,
                "instagram": None,
                "facebook": None
            }
        }
        
        for result in search_results:
            # Add source information
            if "metadata" in result and "url" in result["metadata"]:
                url = result["metadata"].get("url", "")
                title = result["metadata"].get("title", "")
                
                source = {
                    "url": url,
                    "title": title
                }
                formatted_results["sources"].append(source)
                
                # Try to extract social media links
                if "twitter.com/" in url or "x.com/" in url:
                    formatted_results["social_links"]["x_twitter"] = url
                elif "instagram.com/" in url:
                    formatted_results["social_links"]["instagram"] = url
                elif "facebook.com/" in url:
                    formatted_results["social_links"]["facebook"] = url
            
            # Add content
            if "markdown" in result:
                content = result["markdown"]
                formatted_results["content"].append(content)
                
                # Try to find social links in content
                if not formatted_results["social_links"]["x_twitter"]:
                    x_matches = re.findall(r'https?://(?:www\.)?(twitter\.com|x\.com)/([a-zA-Z0-9_]+)', content)
                    if x_matches:
                        formatted_results["social_links"]["x_twitter"] = f"https://{x_matches[0][0]}/{x_matches[0][1]}"
                
                if not formatted_results["social_links"]["instagram"]:
                    ig_matches = re.findall(r'https?://(?:www\.)?instagram\.com/([a-zA-Z0-9_\.]+)', content)
                    if ig_matches:
                        formatted_results["social_links"]["instagram"] = f"https://instagram.com/{ig_matches[0]}"
                
                if not formatted_results["social_links"]["facebook"]:
                    fb_matches = re.findall(r'https?://(?:www\.)?facebook\.com/([a-zA-Z0-9\.]+)', content)
                    if fb_matches:
                        formatted_results["social_links"]["facebook"] = f"https://facebook.com/{fb_matches[0]}"
        
        return formatted_results