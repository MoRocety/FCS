#!/usr/bin/env python3
"""
Dynamic course scraper for FCC College course catalog.
Automatically extracts fresh session tokens and security keys.
Also detects the active term from the website.
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import os
from pathlib import Path


def detect_active_term(soup):
    """
    Detect the currently active term from the select dropdown.
    Finds the LATEST term that ends in FA (Fall) or SP (Spring).
    Ignores selected attribute - always picks the most recent regular term.
    
    Args:
        soup: BeautifulSoup object of the initial page
    
    Returns:
        str: Term code like '2025FA' or None if not found
    """
    # Find the term select dropdown
    term_select = soup.find('select', {'name': 'empower_global_term_id'})
    if not term_select:
        print("Warning: Could not find term selector dropdown")
        return None
    
    # Find all FA/SP terms (exclude PH, IE, and other special programs)
    # Options are already sorted latest to oldest on the website
    all_options = term_select.find_all('option')
    
    for option in all_options:
        value = option.get('value', '')
        # Match terms that are exactly 6 chars: 4 digits + FA or SP
        # Examples: 2025FA, 2026SP
        # Excludes: PH25FA, IE25SP, 125-26, PS2526, etc.
        if value and len(value) == 6 and value[:4].isdigit():
            if value.endswith('FA') or value.endswith('SP'):
                # Found the first (latest) valid FA/SP term
                print(f"  Detected latest active term: {value}")
                return value
    
    # No valid FA/SP term found
    print("  Warning: No valid FA/SP terms found")
    return None


def save_active_term(term_code):
    """
    Save the active term to a file for the application to read.
    Creates ACTIVE_TERM file in the project root.
    
    Args:
        term_code (str): Term code like '2025FA'
    """
    # Go up one directory from scraper/ to project root
    project_root = Path(__file__).parent.parent
    active_term_file = project_root / 'ACTIVE_TERM'
    
    try:
        with open(active_term_file, 'w') as f:
            f.write(term_code)
        print(f"  Saved active term to: {active_term_file}")
    except Exception as e:
        print(f"  Warning: Could not save active term: {e}")


def scrape_courses(terms=None, auto_detect=True):
    """
    Scrape course data for given terms.
    
    Args:
        terms (list): List of term IDs to scrape (e.g., ['2025FA', 'PH25FA'])
                     If None and auto_detect=True, scrapes the active term only
                     If None and auto_detect=False, defaults to ['2025FA', 'PH25FA']
        auto_detect (bool): If True, auto-detect and scrape only the active term
    
    Returns:
        dict: Dictionary mapping term IDs to their JSON data
    """
    detected_term = None
    
    results = {}
    
    # Create a session to maintain cookies across requests
    session = requests.Session()
    
    # Set a realistic user agent
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    
    print("Step 1: Fetching initial page to get session and security tokens...")
    
    # Step 1: Get the initial page to establish session and extract tokens
    initial_url = 'https://mysis-fccollege.empower-xl.com/fusebox.cfm?fuseaction=CourseCatalog&rpt=1'
    
    try:
        initial_response = session.get(initial_url)
        initial_response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching initial page: {e}")
        return results
    
    # Parse the HTML to extract security tokens
    soup = BeautifulSoup(initial_response.content, 'html.parser')
    
    # Auto-detect the active term if requested
    if auto_detect:
        detected_term = detect_active_term(soup)
        if detected_term:
            save_active_term(detected_term)
            # If no terms specified, use the detected term
            if terms is None:
                terms = [detected_term]
    
    # Fallback to defaults if still no terms
    if terms is None:
        terms = ['2025FA', 'PH25FA']
    
    # Find the center_col div and extract script tags
    center_col = soup.find('div', id='center_col')
    if not center_col:
        print("Error: Could not find 'center_col' div. Website structure may have changed.")
        return results
    
    scripts = center_col.find_all('script')
    if len(scripts) < 2:
        print("Error: Expected script tags not found. Website structure may have changed.")
        return results
    
    # Extract the security token and key from the second script tag
    script_content = scripts[1].get_text()
    
    # Parse the JavaScript to extract jsonkey and utoken
    # Format: var jsonkey = "..."; var utoken = "...";
    script_cleaned = script_content.replace('\r', '').replace('\n', '').replace(' ', '')
    parts = script_cleaned.split(';')
    
    jsonkey = None
    utoken = None
    
    for part in parts:
        if 'jsonkey=' in part:
            jsonkey = part.split('=')[1].replace('"', '').replace("'", '')
        elif 'utoken=' in part:
            utoken = part.split('=')[1].replace('"', '').replace("'", '')
    
    if not jsonkey or not utoken:
        print("Error: Could not extract security tokens from page.")
        print(f"Script content: {script_content[:200]}...")
        return results
    
    print(f"✓ Extracted tokens successfully")
    print(f"  Session ID: {session.cookies.get('JSESSIONID', 'Not found')}")
    print(f"  Security token (utoken): {utoken[:20]}...")
    print(f"  JSON key: {jsonkey[:20]}...")
    
    # Step 2: For each term, fetch the course data
    for term in terms:
        print(f"\nStep 2: Fetching course data for term {term}...")
        
        # Prepare the API request
        api_url = 'https://mysis-fccollege.empower-xl.com/cfcs/courseCatalog.cfc'
        
        params = {
            'method': 'GetList',
            'returnformat': 'json',
            utoken: jsonkey,  # Dynamic security token
        }
        
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://mysis-fccollege.empower-xl.com',
            'referer': 'https://mysis-fccollege.empower-xl.com/fusebox.cfm?fuseaction=CourseCatalog&rpt=1',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        data = {
            'fuseaction': 'CourseCatalog',
            'screen_width': '1920',
            'empower_global_term_id': term,
            'cs_descr': '',
            'empower_global_dept_id': '',
            'empower_global_course_id': '',
            'cs_sess_id': '',
            'cs_loca_id': '',
            'cs_inst_id': '',
            'cs_classroom': '',
            'cs_emph_id': '',
            'CS_time_start': '',
            'CS_time_end': '',
            'status': '1',
        }
        
        try:
            response = session.post(api_url, params=params, headers=headers, data=data)
            response.raise_for_status()
            
            course_data = response.json()
            results[term] = course_data
            
            # Save to file
            output_file = f'{term}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(course_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Successfully scraped {term}")
            print(f"  Saved to: {output_file}")
            
            # Check if we got data
            if 'html' in course_data:
                # Count courses roughly
                course_count = course_data.get('html', '').count('ui-grid-row')
                print(f"  Courses found: ~{course_count}")
            
        except requests.RequestException as e:
            print(f"✗ Error fetching data for {term}: {e}")
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing JSON for {term}: {e}")
    
    return results


if __name__ == '__main__':
    print("=" * 60)
    print("FCC Course Catalog Scraper")
    print("=" * 60)
    
    # Allow command line arguments for terms
    if len(sys.argv) > 1:
        terms_to_scrape = sys.argv[1:]
        print(f"Terms to scrape (manual): {', '.join(terms_to_scrape)}")
        print()
        # Use manual terms, disable auto-detect
        results = scrape_courses(terms_to_scrape, auto_detect=False)
    else:
        # Auto-detect and scrape only the active term
        print("Auto-detecting active term...")
        print()
        results = scrape_courses(None, auto_detect=True)
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    for term, data in results.items():
        if data:
            print(f"✓ {term}: Successfully scraped")
        else:
            print(f"✗ {term}: Failed")
    
    if not results:
        print("✗ No data scraped. Check errors above.")
        sys.exit(1)
    else:
        print(f"\n✓ Scraped {len(results)} term(s) successfully")
        sys.exit(0)
