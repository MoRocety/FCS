"""
Configuration management for FCS Course Scheduler.
Handles environment variables and term configuration.
"""

import os
from pathlib import Path

# Load from environment variables or use defaults
ACTIVE_TERM = os.getenv('ACTIVE_TERM', '2025FA')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'change_this_in_production')

# Base directory
BASE_DIR = Path(__file__).parent

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
    """Get the currently active term code."""
    return ACTIVE_TERM

def get_active_term_human():
    """Get the currently active term in human-readable format."""
    return decode_term_code(ACTIVE_TERM)

def set_active_term(term_code):
    """
    Set the active term (in memory only).
    To persist, update the .env file or environment variable.
    """
    global ACTIVE_TERM
    ACTIVE_TERM = term_code

