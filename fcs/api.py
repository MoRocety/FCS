from flask import Blueprint, jsonify, request, current_app
from .scheduling import generate
from .rules import validate_rule

api = Blueprint('planner_api', __name__, url_prefix='/api/v1')


@api.get('/catalog')
def catalog():
    try:
        return jsonify(current_app.extensions['catalog'].load())
    except (ValueError, FileNotFoundError) as exc:
        return jsonify(error=str(exc)), 503


@api.post('/schedules/generate')
def schedules():
    data = request.get_json(silent=True)
    try:
        if not isinstance(data, dict):
            raise ValueError('Expected a JSON object')
        ids, required = data.get('section_ids'), data.get('required_course_keys', [])
        if not isinstance(ids, list) or not ids or len(ids) > 60 or any(not isinstance(s, str) for s in ids):
            raise ValueError('Select between 1 and 60 sections')
        if not isinstance(required, list) or any(not isinstance(s, str) for s in required):
            raise ValueError('Invalid required courses')
        minimum, maximum = float(data.get('min_credits', 0)), float(data.get('max_credits', 22))
        if not 0 <= minimum <= maximum <= 30:
            raise ValueError('Credits must satisfy 0 ≤ minimum ≤ maximum ≤ 30')
        catalog = current_app.extensions['catalog'].load()
        if data.get('term') != catalog['term']:
            raise ValueError('The term has changed. Reload the catalog before generating.')
        if data.get('catalog_revision') != catalog['revision']:
            raise ValueError('The course data has changed. Reload before generating schedules.')
        lookup = {s['id']: s for s in catalog['sections']}
        if any(identity not in lookup for identity in ids):
            raise ValueError('Some selected sections are no longer in the catalog')
        sections = [lookup[identity] for identity in dict.fromkeys(ids)]
        if not set(required) <= {s['course_key'] for s in sections}:
            raise ValueError('Required courses must be in your shortlist')
        rules = validate_rule(data.get("rules", {"op": "and", "children": []}),
                              {s["course_key"] for s in sections})
        return jsonify(generate(sections, minimum, maximum, set(required), rules=rules))
    except (ValueError, TypeError) as exc:
        return jsonify(error=str(exc)), 400
    except FileNotFoundError as exc:
        return jsonify(error=str(exc)), 503
