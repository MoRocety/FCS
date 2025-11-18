"""
Configuration management for FCS Course Scheduler.
Handles environment variables and term configuration.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Load WEBHOOK_SECRET from environment
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'change_this_in_production')

# ACTIVE_TERM is always read from file, never cached

# Term code to human-readable mapping
TERM_DECODE = {
    'FA': 'Fall',
    'SP': 'Spring',
}

def decode_term_code(term_code):
    """
    Convert term code like '2025FA' to '2025 Fall'
    
    Args:
        term_code (str): Term code like '2025FA', 'PH25SP', etc.
    
    Returns:
        str: Human readable term like '2025 Fall'
    """
    # Handle pharmacy program codes (PH25FA -> Pharmacy Program Fall 2025)
    if term_code.startswith('PH'):
        year = '20' + term_code[2:4]
        season_code = term_code[4:]
        season = TERM_DECODE.get(season_code, season_code)
        return f'Pharmacy Program {season} {year}'
    
    # Handle intensive English codes (IE25FA -> Intensive English 2025 Fall)
    if term_code.startswith('IE'):
        year = '20' + term_code[2:4]
        season_code = term_code[4:]
        season = TERM_DECODE.get(season_code, season_code)
        return f'Intensive English {year} {season}'
    
    # Handle standard term codes (2025FA -> 2025 Fall)
    if len(term_code) >= 6:
        year = term_code[:4]
        season_code = term_code[4:]
        season = TERM_DECODE.get(season_code, season_code)
        return f'{year} {season}'
    
    # Fallback for unknown formats
    return term_code

def get_data_filename(term_code):
    """
    Get the data filename for a given term code.
    
    Args:
        term_code (str): Term code like '2025FA'
    
    Returns:
        str: Filename like '2025FAdata.txt'
    """
    return f'{term_code}data.txt'

def get_active_term():
    """Get the currently active term code from ACTIVE_TERM file."""
    active_term_file = BASE_DIR / 'ACTIVE_TERM'
    if not active_term_file.exists():
        raise FileNotFoundError(
            f"ACTIVE_TERM file not found at {active_term_file}. "
            "Please create it with a term code like '2026SP'"
        )
    return active_term_file.read_text().strip()

def get_active_term_human():
    """Get the currently active term in human-readable format."""
    return decode_term_code(get_active_term())

def set_active_term(term_code):
    """
    Set the active term by writing to ACTIVE_TERM file.
    
    Args:
        term_code (str): Term code like '2026SP'
    """
    active_term_file = BASE_DIR / 'ACTIVE_TERM'
    active_term_file.write_text(term_code)

