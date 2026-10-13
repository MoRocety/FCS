"""Boolean course predicates, validated once and evaluated during search."""
MAX_DEPTH = 8
MAX_NODES = 80


def validate_rule(rule, course_keys):
    count = 0

    def visit(node, depth, root=False):
        nonlocal count
        count += 1
        if depth > MAX_DEPTH or count > MAX_NODES:
            raise ValueError('Rules allow at most 8 levels and 80 blocks')
        if not isinstance(node, dict):
            raise ValueError('Each rule must be a block')
        op = node.get('op')
        if op == 'course':
            if set(node) != {'op', 'course_key', 'present'} or not isinstance(node['course_key'], str) or type(node['present']) is not bool:
                raise ValueError('Invalid course predicate')
            if node['course_key'] not in course_keys:
                raise ValueError('Every rule course must have a section in your shortlist')
            return dict(node)
        if op not in ('and', 'or', 'not') or set(node) != {'op', 'children'} or not isinstance(node['children'], list):
            raise ValueError('Use AND, OR, NOT, or a course predicate')
        children = node['children']
        if op == 'not' and len(children) != 1:
            raise ValueError('NOT must contain exactly one expression')
        if not children and not (root and op == 'and'):
            raise ValueError('Add a rule to each group, or remove the empty group')
        return {'op': op, 'children': [visit(child, depth + 1) for child in children]}

    return visit(rule, 1, True)


def evaluate(rule, chosen, pending=frozenset()):
    """True/False/None: None means undecided while course choices remain."""
    op = rule['op']
    if op == 'course':
        key = rule['course_key']
        value = True if key in chosen else None if key in pending else False
        return value if rule['present'] or value is None else not value
    values = [evaluate(child, chosen, pending) for child in rule['children']]
    if op == 'not':
        return None if values[0] is None else not values[0]
    if op == 'and':
        return False if False in values else None if None in values else True
    return True if True in values else None if None in values else False


def referenced_courses(rule):
    if rule['op'] == 'course':
        return {rule['course_key']}
    return set().union(*(referenced_courses(child) for child in rule['children']))
