"""Page routes and compatibility adapters for the original FCS interface."""
import hmac
import os
import tempfile
from pathlib import Path
from flask import Blueprint, current_app, jsonify, render_template, request
from config import BASE_DIR, decode_term_code, set_active_term
from fcs.catalog import TERM, parse_rows
from fcs.scheduling import generate

my_blueprint = Blueprint('my_blueprint', __name__)


def catalog():
    return current_app.extensions['catalog'].load()


def legacy(s):
    meetings = s['meetings']
    primary = meetings[0] if meetings else {}
    alternate = meetings[1] if len(meetings) > 1 else {}
    return {'department_id': s['department'], 'course_id': s['number'], 'section': s['section'],
        'name': s['name'], 'credits': s['credits'], 'instructor_name': s['instructor'],
        'days': ''.join(primary.get('days', [])), 'start_time': primary.get('start', 'None'),
        'end_time': primary.get('end', 'None'), 'classroom': primary.get('room', 'TBD'),
        'alternate_days': ''.join(alternate.get('days', [])),
        'alternate_start_time': alternate.get('start', 'None'),
        'alternate_end_time': alternate.get('end', 'None'), 'alternate_classroom': alternate.get('room', 'None'),
        'total_seats': s['total_seats'], 'available_seats': s['available_seats']}


def filtered(department='', course='', instructor=''):
    return [s for s in catalog()['sections'] if all(
        not value or value.upper() == 'ALL' or s[field].upper() == value.upper()
        for field, value in [('department', department), ('name', course), ('instructor', instructor)])]


def options(values):
    return [{'label': value, 'value': value} for value in sorted(set(values))]


@my_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sections = filtered(request.form.get('dropdown', ''), request.form.get('dropdown2', ''), request.form.get('dropdown3', ''))
        return jsonify(data=[legacy(s) for s in sections[:20]], size=len(sections))
    try:
        data = catalog()
    except (ValueError, FileNotFoundError):
        data = {'term_name': 'Catalog unavailable'}
    return render_template('planner.html', active_term=data['term_name'])


@my_blueprint.get('/old')
def index_old():
    return render_template('New_index.html')


@my_blueprint.get('/test')
def index_test():
    return render_template('tester.html')


@my_blueprint.post('/paginationClick')
def paginator():
    try:
        page = int(request.form.get('page', 1))
        if page < 1:
            raise ValueError()
    except ValueError:
        return jsonify(error='Invalid page'), 400
    sections = filtered(request.form.get('dropdown', ''), request.form.get('dropdown2', ''), request.form.get('dropdown3', ''))
    return jsonify([legacy(s) for s in sections[(page - 1) * 20:page * 20]])


@my_blueprint.post('/updateTerm')
def update_term():
    catalog()
    return 'Data updated successfully'


@my_blueprint.get('/departments')
def departments():
    return jsonify(options(catalog()['departments']))


@my_blueprint.get('/courses')
def courses():
    return jsonify(options(s['name'] for s in catalog()['sections']))


@my_blueprint.get('/instructors')
def instructors():
    return jsonify(options(s['instructor'] for s in catalog()['sections']))


@my_blueprint.post('/updateDepartment')
@my_blueprint.post('/updateInstructor')
@my_blueprint.post('/updateCourse')
def update_filters():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict) or any(not isinstance(v, str) for v in data.values()):
        return jsonify(error='Invalid filter'), 400
    department = data.get('data', '') if request.path == '/updateDepartment' else data.get('department', '')
    course = data.get('data', '') if request.path == '/updateCourse' else ''
    instructor = data.get('data', '') if request.path == '/updateInstructor' else ''
    sections = filtered(department, course, instructor)
    return jsonify(courses=options(s['name'] for s in sections), instructors=options(s['instructor'] for s in sections))


@my_blueprint.post('/submit')
def submit():
    """Bounded adapter for older clients; all values are resolved against the catalog."""
    data = request.get_json(silent=True)
    try:
        if not isinstance(data, dict):
            raise ValueError('Expected a JSON object')
        selected = data.get('selectedCourses', [])
        crucial = data.get('checkedCrucials', [])
        if not isinstance(selected, list) or not 1 <= len(selected) <= 60 or not isinstance(crucial, list) or len(crucial) > 60:
            raise ValueError('Select between 1 and 60 sections')
        def identity(s):
            return ':'.join(str(s[k]) for k in ('department_id', 'course_id', 'section'))
        lookup = {s['id']: s for s in catalog()['sections']}
        ids = list(dict.fromkeys(identity(s) for s in selected))
        missing = [s for s in selected if identity(s) not in lookup]
        sections = [lookup[s] for s in ids if s in lookup]
        required = {f"{s['department_id']}:{s['course_id']}" for s in crucial}
        if not required <= {s['course_key'] for s in sections}:
            raise ValueError('A required course is missing from the catalog')
        minimum, maximum = float(data.get('minCredit', 0)), float(data.get('maxCredit', 22))
        if not 0 <= minimum <= maximum <= 30:
            raise ValueError('Invalid credit range')
        result = generate(sections, minimum, maximum, required)
        return jsonify(schedules=[[legacy(lookup[s]) for s in schedule] for schedule in result['schedules']],
                       missing_courses=missing, limited=result['limited'])
    except (ValueError, TypeError, KeyError) as exc:
        return jsonify(error=str(exc)), 400


@my_blueprint.post('/webhook/update-courses')
def update_courses_webhook():
    secret = os.environ.get('WEBHOOK_SECRET')
    token = request.headers.get('X-Webhook-Token')
    if not secret or not token or not hmac.compare_digest(token.encode("utf-8"), secret.encode("utf-8")):
        return jsonify(error='Unauthorized'), 401
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error='Expected a JSON object'), 400
    term, content = data.get('term_code'), data.get('content')
    if not isinstance(term, str) or not TERM.fullmatch(term) or not isinstance(content, str) or not content:
        return jsonify(error='Invalid term_code or content'), 400
    try:
        sections = parse_rows(content)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    destination = BASE_DIR / f'{term}data.txt'
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=BASE_DIR, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        temporary.replace(destination)
        temporary = None
        set_active_term(term)
        from fcs.availability import observe_catalog
        observe_catalog(catalog())
        return jsonify(success=True, term_code=term, term_name=decode_term_code(term),
                       courses_loaded=len(sections), departments_count=len({s['department'] for s in sections}))
    except OSError:
        current_app.logger.exception('Could not persist catalog update')
        return jsonify(error='Could not persist catalog update'), 500
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


@my_blueprint.get('/api/active-term')
def active_term():
    data = catalog()
    return jsonify(term_code=data['term'], term_name=data['term_name'],
                   courses_count=len(data['sections']), departments_count=len(data['departments']))
