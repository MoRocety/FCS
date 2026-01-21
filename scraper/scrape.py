#!/usr/bin/env python3
"""
Dynamic course scraper for FCC College course catalog.
Automatically extracts fresh session tokens and security keys.
Also detects the active term from the website.
"""

from requests import Session
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
        # Debug: Show what selects we DID find
        all_selects = soup.find_all('select')
        if all_selects:
            print(f"  Found {len(all_selects)} select elements:")
            for sel in all_selects[:3]:  # Show first 3
                name = sel.get('name', 'no-name')
                id_attr = sel.get('id', 'no-id')
                print(f"    - name='{name}', id='{id_attr}'")
        else:
            print("  No select elements found at all")
            print(f"  Page title: {soup.title.string if soup.title else 'No title'}")
            print(f"  Page length: {len(str(soup))} chars")
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
        terms (list): List of term IDs to scrape (e.g., ['2026SP'])
                     If None and auto_detect=True, scrapes the active term only
        auto_detect (bool): If True, auto-detect and scrape only the active term
    
    Returns:
        dict: Dictionary mapping term IDs to their JSON data
    """
    results = {}
    
    # Create a session to maintain cookies across requests
    sess = Session()
    sess.verify = False
    print("Step 1: Fetching initial page to get session and security tokens...")
    
    # Step 1: Get the initial page to establish session and extract tokens
    initial_url = 'https://mysis-fccollege.empower-xl.com/fusebox.cfm?fuseaction=CourseCatalog&rpt=1'
    
    try:
        page = sess.get(initial_url).content
    except Exception as e:
        print(f"Error fetching initial page: {e}")
        return results
    
    # Parse the HTML to extract security tokens
    soup = BeautifulSoup(page, 'html.parser')
    
    # Auto-detect the active term if requested
    detected_term = None
    if auto_detect:
        detected_term = detect_active_term(soup)
        if detected_term:
            save_active_term(detected_term)
            # If no terms specified, use the detected term
            if terms is None:
                terms = [detected_term]
    
    # If still no terms, fail - don't use defaults
    if terms is None:
        print("Error: No terms specified and auto-detect failed")
        return results
    
    # Extract tokens using the simple working method
    data = soup.find('div', id='center_col').find_all('script')[1].get_text().replace('\r', '').replace('\n', '').replace(' ', '').split(';')
    
    jsonkey = data[0].replace('"', '').split('=')[1]
    utoken = data[1].replace('"', '').split('=')[1]
    
    print(f"✓ Extracted tokens successfully")
    print(f"  Session ID: {sess.cookies.get('JSESSIONID', 'Active')}")
    print(f"  Security token (utoken): {utoken[:20]}...")
    print(f"  JSON key: {jsonkey[:20]}...")
    
    # Step 2: For each term, fetch the course data
    for term in terms:
        print(f"\nStep 2: Fetching course data for term {term}...")
        
        params = {
            'method': 'GetList',
        }
        
        data = {
            'fuseaction': 'CourseCatalog',
            'screen_width': '1920',
            'token': jsonkey,  # Token goes in POST body, not URL params!
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
        
        # Send the POST request using the session
        re = sess.post('https://mysis-fccollege.empower-xl.com/cfcs/courseCatalog.cfc', params=params, data=data)
        content = json.loads(re.content)
        
        results[term] = content
        
        # Write the JSON content to a file
        with open(f"{term}.json", "w", encoding="utf-8") as f:
            json.dump(content, f, indent=4)
        
        print(f"✓ Successfully scraped {term}")
        print(f"  Saved to: {term}.json")
        
        # Check if we got data
        if 'html' in content:
            course_count = content.get('html', '').count('ui-grid-row')
            print(f"  Courses found: ~{course_count}")
        else:
            print(f"  Warning: No 'html' field in response")
    
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
