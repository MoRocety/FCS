#!/usr/bin/env python3
"""
Send scraped course data to PythonAnywhere webhook.
Called by GitHub Actions after scraping and parsing.
"""

import os
import sys
import json
import requests
from pathlib import Path


def main():
    # Read environment variables (strip any whitespace/newlines)
    webhook_url = os.environ.get('WEBHOOK_URL', '').strip()
    webhook_secret = os.environ.get('WEBHOOK_SECRET', '').strip()
    
    # Check if secrets are set
    if not webhook_url or not webhook_secret:
        print("⚠️  Warning: WEBHOOK_URL or WEBHOOK_SECRET not set")
        print("⚠️  Skipping webhook update. Set these secrets in GitHub Settings → Secrets → Actions")
        print("⚠️  For now, manually upload the generated files to PythonAnywhere")
        return 0
    
    # Read ACTIVE_TERM (one level up from scraper/)
    active_term_file = Path(__file__).parent.parent / 'ACTIVE_TERM'
    if not active_term_file.exists():
        print("✗ Error: ACTIVE_TERM file not found")
        return 1
    
    active_term = active_term_file.read_text().strip()
    print(f"📤 Sending {active_term} data to webhook...")
    
    # Read data file
    data_file = Path(__file__).parent / f'{active_term}data.txt'
    if not data_file.exists():
        print(f"✗ Error: {data_file} not found")
        return 1
    
    content = data_file.read_text(encoding='utf-8')
    print(f"✓ Read {len(content)} bytes from {data_file.name}")
    
    # Prepare payload
    payload = {
        'term_code': active_term,
        'content': content
    }
    
    # Send request
    print(f"📡 Sending POST request to {webhook_url}")
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'X-Webhook-Token': webhook_secret
            },
            timeout=30
        )
        
        print(f"\n📥 HTTP Response Code: {response.status_code}")
        print("Response Body:")
        try:
            response_data = response.json()
            print(json.dumps(response_data, indent=2))
        except:
            print(response.text[:500])  # First 500 chars if not JSON
        
        if response.status_code == 200:
            print("\n✅ Successfully sent data to webhook!")
            return 0
        else:
            print(f"\n❌ Webhook request failed with HTTP {response.status_code}")
            return 1
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out after 30 seconds")
        return 1
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection failed: {e}")
        return 1
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

