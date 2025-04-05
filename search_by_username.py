#!/usr/bin/env python3
"""
Script to find information about a person starting from their X/Twitter username
"""

import requests
import json
import time
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API base URL - adjust if your server is running on a different port
BASE_URL = "http://localhost:8080"


def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))


def find_info_by_username(username):
    """Find information about a person by their X/Twitter username"""
    print(f"\n--- Searching for info about X user: @{username} ---")
    
    # Step 1: Try to find who this person is from their username
    # Search for the username with phrases that might reveal their identity
    identity_queries = [
        f"@{username} twitter who is this person real name",
        f"@{username} real name person behind twitter account",
        f"who is @{username} on twitter personal information"
    ]
    
    found_info = {
        "username": username,
        "potential_names": [],
        "potential_info": [],
        "related_links": []
    }
    
    # Try each query and collect results
    for query in identity_queries:
        print(f"\nTrying search query: '{query}'")
        data = {
            "query": query,
            "max_results": 3,
            "scraping_tool": "browser-playwright",  # Need more powerful scraping for this task
            "output_format": "markdown"
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/raw-search", json=data)
        duration = time.time() - start_time
        
        print(f"Status code: {response.status_code}")
        print(f"Response time: {duration:.2f} seconds")
        
        if response.status_code == 200:
            results = response.json()
            
            # Process each result
            for result in results:
                markdown = result.get('markdown', '')
                url = result.get('metadata', {}).get('url', '')
                title = result.get('metadata', {}).get('title', '')
                
                # Add the URL to related links
                if url and url not in found_info["related_links"]:
                    found_info["related_links"].append(url)
                
                # Extract potential names - look for patterns that suggest real names
                name_patterns = [
                    f"@{username} is ([A-Z][a-z]+ [A-Z][a-z]+)",
                    f"([A-Z][a-z]+ [A-Z][a-z]+) known as @{username}",
                    f"([A-Z][a-z]+ [A-Z][a-zA-Z-]+), @{username}",
                    f"name is ([A-Z][a-z]+ [A-Z][a-z]+)",
                    f"real name is ([A-Z][a-z]+ [A-Z][a-z]+)",
                    f"([A-Z][a-z]+ [A-Z][a-z]+) \(@{username}\)"
                ]
                
                import re
                for pattern in name_patterns:
                    matches = re.findall(pattern, markdown)
                    for match in matches:
                        if match and match not in found_info["potential_names"]:
                            found_info["potential_names"].append(match)
                
                # Extract context paragraphs around username mentions
                username_mentions = re.finditer(f"@?{username}", markdown, re.IGNORECASE)
                for match in username_mentions:
                    start_pos = max(0, match.start() - 100)
                    end_pos = min(len(markdown), match.end() + 100)
                    context = markdown[start_pos:end_pos].strip()
                    if context and len(context) > 50:  # Only add substantial context
                        # Clean up context to get complete sentences/paragraphs
                        context = re.sub(r'^\S+\s', '', context)  # Remove partial word at start
                        context = re.sub(r'\s\S+$', '', context)  # Remove partial word at end
                        
                        # Add to potential info if not too similar to existing items
                        if not any(is_similar_text(context, info) for info in found_info["potential_info"]):
                            found_info["potential_info"].append(context)
        else:
            print(f"Error: {response.text}")
    
    # Step 2: If we found potential names, search for more information about them
    if found_info["potential_names"]:
        # Use the first (most likely) name we found
        potential_name = found_info["potential_names"][0]
        print(f"\nSearching for more information about: {potential_name}")
        
        data = {
            "name": potential_name,
            "context": f"related to twitter @{username}",
            "max_results": 3
        }
        
        response = requests.post(f"{BASE_URL}/search", json=data)
        
        if response.status_code == 200:
            result = response.json()
            # Add content to potential_info
            for content in result.get('content', []):
                if content and not any(is_similar_text(content, info) for info in found_info["potential_info"]):
                    found_info["potential_info"].append(content[:500])  # Limit length
    
    # Print the findings
    print("\n--- Information Found ---")
    print(f"Username: @{username}")
    
    if found_info["potential_names"]:
        print("\nPotential real name(s):")
        for name in found_info["potential_names"]:
            print(f"- {name}")
    else:
        print("\nNo potential real names found.")
    
    if found_info["potential_info"]:
        print("\nInformation about this person:")
        for i, info in enumerate(found_info["potential_info"][:3], 1):  # Show top 3 info pieces
            print(f"\n{i}. {info[:300]}..." if len(info) > 300 else f"\n{i}. {info}")
    else:
        print("\nNo detailed information found.")
    
    if found_info["related_links"]:
        print("\nRelated links:")
        for link in found_info["related_links"][:5]:  # Show top 5 links
            print(f"- {link}")
    
    return found_info


def is_similar_text(text1, text2, threshold=0.7):
    """Check if two text snippets are similar to avoid duplicates"""
    # Simple implementation based on common words
    if not text1 or not text2:
        return False
        
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return False
        
    common_words = words1.intersection(words2)
    similarity = len(common_words) / min(len(words1), len(words2))
    
    return similarity > threshold


def main():
    """Main function to search by username"""
    if len(sys.argv) < 2:
        print("Usage: python search_by_username.py <x_username> [<x_username2> ...]")
        print("Example: python search_by_username.py ITNAmatter")
        sys.exit(1)
    
    usernames = sys.argv[1:]
    
    for username in usernames:
        # Remove @ if present
        if username.startswith('@'):
            username = username[1:]
            
        find_info_by_username(username)


if __name__ == "__main__":
    main()