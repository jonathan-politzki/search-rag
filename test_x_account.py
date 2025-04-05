#!/usr/bin/env python3
"""
Script to test retrieving X (Twitter) accounts using the API
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
        print(f"X/Twitter: {social_links.get('x_twitter') or 'Not found'}")
        print(f"Instagram: {social_links.get('instagram') or 'Not found'}")
        print(f"Facebook: {social_links.get('facebook') or 'Not found'}")
        
        # Print source URLs
        if result.get('sources'):
            print("\nSource URLs:")
            for i, source in enumerate(result.get('sources'), 1):
                print(f"  {i}. {source.get('url')}")
        
        return True
    else:
        print(f"Error: {response.text}")
        return False


def main():
    """Run tests for different people"""
    people = sys.argv[1:] if len(sys.argv) > 1 else [
        "Barack Obama",
        "Elon Musk",
        "Taylor Swift"
    ]
    
    results = {}
    for person in people:
        results[person] = test_x_account_retrieval(person)
    
    # Print summary
    print("\n--- Test Summary ---")
    for person, success in results.items():
        print(f"{person}: {'Success' if success else 'Failed'}")


if __name__ == "__main__":
    main()