"""Pure scheduling rules, independent of HTTP and storage."""
from itertools import combinations
from .rules import evaluate, referenced_courses


def conflicts(a, b):
    return any(set(x['days']) & set(y['days']) and x['start'] < y['end'] and y['start'] < x['end']
               for x in a['meetings'] for y in b['meetings'])


def conflict_pairs(sections):
    return [[a['id'], b['id']] for a, b in combinations(sections, 2) if conflicts(a, b)]


def internally_conflicting(section):
    return any(set(a['days']) & set(b['days']) and a['start'] < b['end'] and b['start'] < a['end']
               for a, b in combinations(section['meetings'], 2))


def generate(sections, minimum, maximum, required=None, limit=50, budget=100000, rules=None, continuation=None):
    """Depth-first search with pruning and a resumable frontier, never a top-N ranking.

    Only trusted internal state may be passed as continuation. The HTTP boundary
    binds it to the original inputs and signs it before sending it to a client.
    """
    required = required or set()
    rules = rules or {"op": "and", "children": []}
    if required:
        rules = {"op": "and", "children": [rules] + [
            {"op": "course", "course_key": key, "present": True} for key in sorted(required)]}
    referenced = referenced_courses(rules)
    groups = {}
    for section in sections:
        if not internally_conflicting(section):
            groups.setdefault(section['course_key'], []).append(section)
    keys = sorted(groups, key=lambda key: (key not in referenced, len(groups[key]), key))
    lookup = {s['id']: s for s in sections}
    remaining = [0.0] * (len(keys) + 1)
    for i in range(len(keys) - 1, -1, -1):
        remaining[i] = remaining[i + 1] + max(s['credits'] for s in groups[keys[i]])
    frontier = [(index, [lookup[identity] for identity in chosen]) for index, chosen in continuation] if continuation is not None else [(0, [])]
    results, visited = [], 0
    while frontier and visited < budget and len(results) < limit:
        index, chosen = frontier.pop()
        visited += 1
        credits = sum(s['credits'] for s in chosen)
        if evaluate(rules, {s['course_key'] for s in chosen}, set(keys[index:])) is False:
            continue
        if credits > maximum or credits + remaining[index] < minimum:
            continue
        if index == len(keys):
            if chosen and minimum <= credits <= maximum:
                results.append([s['id'] for s in chosen])
            continue
        key = keys[index]
        # A LIFO frontier visits section choices before the skip branch, matching
        # the previous traversal while retaining every unvisited branch at a pause.
        if key not in required:
            frontier.append((index + 1, chosen))
        for section in reversed(groups[key]):
            if not any(conflicts(section, existing) for existing in chosen):
                frontier.append((index + 1, chosen + [section]))
    cursor = [[index, [s['id'] for s in chosen]] for index, chosen in frontier] or None
    return {'schedules': results, 'limited': bool(frontier), 'visited': visited, 'continuation': cursor}
