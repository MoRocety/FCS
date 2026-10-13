"""Pure scheduling rules, independent of HTTP and storage."""
from itertools import combinations


def conflicts(a, b):
    return any(set(x['days']) & set(y['days']) and x['start'] < y['end'] and y['start'] < x['end']
               for x in a['meetings'] for y in b['meetings'])


def conflict_pairs(sections):
    return [[a['id'], b['id']] for a, b in combinations(sections, 2) if conflicts(a, b)]


def generate(sections, minimum, maximum, required, limit=50, budget=100000):
    """Backtracking with duplicate-course and conflict pruning, plus hard work limits."""
    groups = {}
    for section in sections:
        groups.setdefault(section['course_key'], []).append(section)
    keys = sorted(groups, key=lambda key: (key not in required, len(groups[key]), key))
    results, visited = [], 0
    remaining = [0.0] * (len(keys) + 1)
    for i in range(len(keys) - 1, -1, -1):
        remaining[i] = remaining[i + 1] + max(s['credits'] for s in groups[keys[i]])

    def visit(index, chosen, credits):
        nonlocal visited
        if visited >= budget or len(results) >= limit:
            return
        visited += 1
        if credits > maximum or credits + remaining[index] < minimum:
            return
        if index == len(keys):
            if chosen and minimum <= credits <= maximum:
                results.append([s['id'] for s in chosen])
            return
        key = keys[index]
        for section in groups[key]:
            if not any(conflicts(section, existing) for existing in chosen):
                visit(index + 1, chosen + [section], credits + section['credits'])
        if key not in required:
            visit(index + 1, chosen, credits)

    visit(0, [], 0)
    return {'schedules': results, 'limited': visited >= budget or len(results) >= limit, 'visited': visited}
