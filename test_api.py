#!/usr/bin/env python3
"""
Simple test script to verify the API functionality
"""

import requests
import json
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API base URL - adjust if your server is running on a different port
BASE_URL = "http://localhost:5000"


def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))


def test_health():
    """Test the health check endpoint"""
    print("\n--- Testing Health Check Endpoint ---")
    response = requests.get(f"{BASE_URL}/health")
    
    print(f"Status code: {response.status_code}")
    print_json(response.json())
    
    assert response.status_code == 200
    assert response.json().get("status") == "ok"
    
    return True


def test_person_search(name, context=""):
    """Test the person search endpoint"""
    print(f"\n--- Testing Person Search for '{name}' ---")
    
    data = {
        "name": name,
        "context": context,
        "max_results": 2  # Limit to 2 results for faster testing
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/search", json=data)
    duration = time.time() - start_time
    
    print(f"Status code: {response.status_code}")
    print(f"Response time: {duration:.2f} seconds")
    
    if response.status_code == 200:
        result = response.json()
        
        # Print summary of the results
        print(f"\nQuery: {result.get('query')}")
        print(f"Sources found: {len(result.get('sources', []))}")
        
        # Print titles of sources
        if result.get('sources'):
            print("\nSource titles:")
            for i, source in enumerate(result.get('sources'), 1):
                print(f"  {i}. {source.get('title')}")
        
        # Print content summary (first 150 chars of first content item)
        if result.get('content'):
            first_content = result.get('content')[0]
            print("\nFirst content snippet:")
            print(f"  {first_content[:150]}...")
        
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_raw_search(query):
    """Test the raw search endpoint"""
    print(f"\n--- Testing Raw Search for '{query}' ---")
    
    data = {
        "query": query,
        "max_results": 2,  # Limit to 2 results for faster testing
        "scraping_tool": "raw-http"  # Use raw-http for faster response
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/raw-search", json=data)
    duration = time.time() - start_time
    
    print(f"Status code: {response.status_code}")
    print(f"Response time: {duration:.2f} seconds")
    
    if response.status_code == 200:
        results = response.json()
        
        # Print summary of the results
        print(f"\nResults found: {len(results)}")
        
        # Print titles of results
        if results:
            print("\nResult titles:")
            for i, result in enumerate(results, 1):
                title = (result.get('metadata', {}).get('title') or 
                         result.get('searchResult', {}).get('title') or 
                         "No title")
                print(f"  {i}. {title}")
        
        return True
    else:
        print(f"Error: {response.text}")
        return False


def main():
    """Run all tests"""
    tests_passed = 0
    tests_failed = 0
    
    # Test health check
    if test_health():
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test person search
    if test_person_search("Barack Obama", "achievements"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test raw search with a URL
    if test_raw_search("https://openai.com"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test raw search with a query
    if test_raw_search("latest AI developments"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Print summary
    print("\n--- Test Summary ---")
    print(f"Tests passed: {tests_passed}")
    print(f"Tests failed: {tests_failed}")
    
    return 0 if tests_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())