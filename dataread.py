import os
from pathlib import Path

# Import config module for term decoding
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import decode_term_code, get_data_filename, get_active_term


def fileread(term=None):
    """
    Read course data from file.
    
    Args:
        term (str): Term in human-readable format like "2025 Fall" or term code like "2025FA"
                   If None, uses the active term from ACTIVE_TERM file or environment variable
    
    Returns:
        tuple: (course_data, departments, courses, sections)
    """
    # If no term specified, use the active term
    if term is None:
        # Try to read from ACTIVE_TERM file first
        active_term_file = Path(__file__).parent / 'ACTIVE_TERM'
        if active_term_file.exists():
            term_code = active_term_file.read_text().strip()
        else:
            # Fall back to environment variable or config default
            term_code = get_active_term()
        
        # Convert to human-readable format for backwards compatibility
        term = decode_term_code(term_code)
    
    # Try to detect if we got a term code instead of human-readable
    # Term codes are like "2025FA", "PH23FA" - short and alphanumeric
    if term and len(term) <= 7 and not ' ' in term:
        # It's a term code, convert to human readable
        term_code = term
        term = decode_term_code(term)
        filename = get_data_filename(term_code)
    else:
        # Try to guess from the term string
        parts = term.upper().split()
        if len(parts) >= 2:
            year = parts[-1]  # Last part is usually the year
            season = parts[-2]  # Second to last is the season
            season_code = 'FA' if 'FALL' in season else 'SP' if 'SPRING' in season else 'SU' if 'SUMMER' in season else 'WN'
            filename = f"{year}{season_code}data.txt"
        else:
            raise ValueError(f"Unknown term format: {term}")
    
    try:
        infile = open(filename, "r", encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file not found for term: {term} (looking for {filename})")
    
    course_data = infile.read().split("\n")

    infile.close()

    filtered_course_data = [x.split("!!") for x in course_data[:-1]]
    course_data = []

    for x in filtered_course_data:
        if x[1].isdigit():
            if int(x[1]) < 500:
                course_data.append(x)

        elif alplusnum(x[1]):
            if int(x[1][:-1]) < 500:
                course_data.append(x)

    # Taking care of table 1
    departments = list(set([x[0] for x in course_data]))

    # Getting to table 2
    # DEPT, ID, NAME, CREDITS
    courses = list(set((x[0], x[1], cap_first_preserve_case(x[3]), x[4]) for x in course_data))
    courses = sorted(courses, key=lambda x: (x[0], x[1]))

    # Getting to table 3
    # DEPT, ID, SECTION, DAYS, START, END, INSTRUCTOR, CLASSROOM, ALT CLASSROOM, ALT DAYS, ALT START, ALT END, T SEATS, A SEATS 
    sections = []
    for x in course_data:
        result = x[5]
        start = x[6]
        end = x[7]

        if start == "None":
            start = None
        
        if end == "None":
            end = None

        instructor = x[8]

        if instructor != "TBD":
            instructor = instructor.title()

        filtered_data = [x[0], x[1], x[2], result, start, end, instructor, x[9], None, None, None, None]

        if x[10] != "None":
            alt_result = x[11]
            filtered_data[8], filtered_data[9], filtered_data[10], filtered_data[11] = x[10], alt_result, x[12], x[13]

        sections.append(tuple(filtered_data))

    return course_data, departments, courses, sections
        

def cap_first_preserve_case(s):
    if len(s) == 0:
        return s
    return s[:1].upper() + s[1:]

def alplusnum(input_string):
    has_numbers = any(char.isdigit() for char in input_string)
    has_alphabets = any(char.isalpha() for char in input_string)
    
    return has_numbers and has_alphabets
