#!/usr/bin/env python3
"""
Script to test retrieving and extracting content from X (Twitter) accounts
"""

import requests
import json
import time
import sys
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API base URL - adjust if your server is running on a different port
BASE_URL = "http://localhost:8080"


def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))


def test_x_account_retrieval(name):
    """Test retrieving X account for a person"""
    print(f"\n--- Testing X Account Retrieval for '{name}' ---")
    
    data = {
        "name": name,
        "focus_x_account": True,
        "max_results": 3  # Using 3 results to increase chances of finding the X account
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/search", json=data)
    duration = time.time() - start_time
    
    print(f"Status code: {response.status_code}")
    print(f"Response time: {duration:.2f} seconds")
    
    if response.status_code == 200:
        result = response.json()
        
        # Print social links
        social_links = result.get('social_links', {})
        print("\nSocial Links:")
        x_account = social_links.get('x_twitter')
        print(f"X/Twitter: {x_account or 'Not found'}")
        print(f"Instagram: {social_links.get('instagram') or 'Not found'}")
        print(f"Facebook: {social_links.get('facebook') or 'Not found'}")
        
        # Return the X account URL if found
        return x_account
    else:
        print(f"Error: {response.text}")
        return None


def extract_username_from_url(url):
    """Extract Twitter/X username from a URL"""
    if not url:
        return None
    
    # Look for patterns like twitter.com/username or x.com/username
    patterns = [
        r'twitter\.com/([a-zA-Z0-9_]+)',
        r'x\.com/([a-zA-Z0-9_]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            username = match.group(1)
            # Remove any trailing segments like /status or /highlights
            if '/' in username:
                username = username.split('/')[0]
            return username
    
    return None


def scrape_x_profile(url):
    """Directly scrape an X profile using RAG Web Browser"""
    print(f"\n--- Scraping X Profile: {url} ---")
    
    # Clean the URL to get just the profile
    username = extract_username_from_url(url)
    if not username:
        print(f"Could not extract username from URL: {url}")
        return None
    
    # Create a clean profile URL
    clean_url = f"https://twitter.com/{username}"
    print(f"Clean profile URL: {clean_url}")
    
    # Use the raw-search endpoint to directly scrape the profile
    data = {
        "query": clean_url,
        "max_results": 1,
        "scraping_tool": "browser-playwright",  # Need to use browser for dynamic X content
        "dynamic_content_wait_secs": 5.0,  # Increase wait time for X to load more content
        "request_timeout_secs": 60,  # Increase timeout for X (it can be slow)
        "output_format": "markdown"
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/raw-search", json=data)
    duration = time.time() - start_time
    
    print(f"Status code: {response.status_code}")
    print(f"Response time: {duration:.2f} seconds")
    
    if response.status_code == 200:
        results = response.json()
        
        # Check if we got any results
        if not results or len(results) == 0:
            print("No content returned from X profile")
            return None
        
        # Get the first result
        profile_data = results[0]
        
        # Try to extract profile info
        # This is a simplistic approach - we're just looking for patterns in the markdown
        markdown = profile_data.get('markdown', '')
        
        # Print the first 1000 characters to see what we got
        print("\nProfile Content Preview:")
        print(markdown[:1000] + "..." if len(markdown) > 1000 else markdown)
        
        # Try to extract basic profile information using regex
        profile_info = {
            "username": username,
            "display_name": None,
            "bio": None,
            "followers_count": None,
            "following_count": None,
            "tweets": []
        }
        
        # Look for display name (often at the beginning)
        display_name_match = re.search(r'# ([^\n]+)', markdown)
        if display_name_match:
            profile_info["display_name"] = display_name_match.group(1).strip()
        
        # Look for bio
        bio_match = re.search(r'Bio:?\s*([^\n]+)', markdown, re.IGNORECASE)
        if bio_match:
            profile_info["bio"] = bio_match.group(1).strip()
        
        # Look for followers/following counts
        followers_match = re.search(r'(\d+[.,]?\d*[KkMm]?)\s*[Ff]ollowers', markdown)
        if followers_match:
            profile_info["followers_count"] = followers_match.group(1)
        
        following_match = re.search(r'(\d+[.,]?\d*[KkMm]?)\s*[Ff]ollowing', markdown)
        if following_match:
            profile_info["following_count"] = following_match.group(1)
        
        # Try to extract tweets (basic approach)
        tweets = re.findall(r'@' + username + r'[:\s]+([^\n]+)', markdown)
        profile_info["tweets"] = tweets[:5]  # Just get the first 5 tweets
        
        print("\nExtracted Profile Information:")
        print_json(profile_info)
        
        return profile_info
    else:
        print(f"Error: {response.text}")
        return None


def main():
    """Run tests for different people"""
    people = sys.argv[1:] if len(sys.argv) > 1 else [
        "Barack Obama",
        "Elon Musk",
        "Taylor Swift"
    ]
    
    results = {}
    for person in people:
        # First get their X account
        x_url = test_x_account_retrieval(person)
        
        if x_url:
            # Then try to scrape the profile
            profile_info = scrape_x_profile(x_url)
            results[person] = profile_info is not None
        else:
            results[person] = False
    
    # Print summary
    print("\n--- Test Summary ---")
    for person, success in results.items():
        print(f"{person}: {'Success' if success else 'Failed'}")


if __name__ == "__main__":
    main()