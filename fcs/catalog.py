"""Validated catalog adapter for the scraper's legacy text format."""
import ast
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from config import BASE_DIR, get_active_term, decode_term_code

TERM = re.compile(r'(?:\d{4}|PH\d{2}|IE\d{2})(?:FA|SP)\Z')
DAYS = 'MTWRFSU'


def data_path(term):
    if not isinstance(term, str) or not TERM.fullmatch(term):
        raise ValueError('Invalid term code')
    for folder in (BASE_DIR, BASE_DIR / 'scraper'):
        path = folder / f'{term}data.txt'
        if path.is_file():
            return path
    raise FileNotFoundError(f'No course data available for {term}')


def meeting(days, start, end, room):
    if start in ('None', '', None) or end in ('None', '', None):
        return None
    day_list = ast.literal_eval(days)
    if not isinstance(day_list, list) or any(d not in DAYS for d in day_list):
        raise ValueError('Invalid meeting days')
    for value in (start, end):
        if not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', value):
            raise ValueError('Time must be HH:MM')
    if start >= end:
        raise ValueError('Meeting must end after it starts')
    return {'days': day_list, 'start': start, 'end': end, 'room': room}


def parse_rows(content):
    result = []
    seen = set()
    for number, line in enumerate(content.splitlines(), 1):
        if not line.strip():
            continue
        row = line.split('!!')
        try:
            if len(row) != 16:
                raise ValueError('Expected 16 columns')
            course_number = re.fullmatch(r'(\d+)[A-Za-z]?', row[1])
            if not course_number:
                # Comprehensive exams are outside the undergraduate catalog.
                if row[1] == 'COMP':
                    continue
                raise ValueError('Invalid course number')
            if int(course_number[1]) >= 500:
                continue
            credits = float(row[4])
            if not 0 <= credits <= 30:
                raise ValueError('Invalid credits')
            meetings = [m for m in (meeting(row[5], row[6], row[7], row[9]),
                        meeting(row[11], row[12], row[13], row[10])) if m]
            identity = ':'.join(row[:3])
            if identity in seen:
                continue
            seen.add(identity)
            result.append({'id': identity, 'course_key': ':'.join(row[:2]),
                'department': row[0], 'number': row[1], 'section': row[2],
                'name': row[3], 'credits': credits, 'instructor': row[8] if row[8] == 'TBD' else row[8].title(),
                'meetings': meetings, 'total_seats': int(row[14]), 'available_seats': int(row[15])})
        except (ValueError, SyntaxError, TypeError) as exc:
            raise ValueError(f'Invalid catalog row {number}: {exc}') from exc
    if not result:
        raise ValueError('Catalog has no undergraduate sections')
    return result


class CatalogRepository:
    def __init__(self):
        self._signature = None
        self._catalog = None

    def load(self):
        term = get_active_term()
        path = data_path(term)
        stat = path.stat()
        signature = (term, str(path), stat.st_mtime_ns, stat.st_size)
        if signature != self._signature:
            content = path.read_text(encoding='utf-8')
            sections = parse_rows(content)
            self._catalog = {'term': term, 'term_name': decode_term_code(term),
                'file_modified_at': datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                'revision': hashlib.sha256(content.encode('utf-8')).hexdigest(),
                'departments': sorted({s['department'] for s in sections}), 'sections': sections}
            self._signature = signature
        return self._catalog
