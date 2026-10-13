import itertools
import unittest
from fcs.rules import evaluate, validate_rule
from fcs.scheduling import generate
from test_scheduler import section
from app import create_app


def course(key, present=True):
    return {'op':'course','course_key':key,'present':present}


def group(op,*children):
    return {'op':op,'children':list(children)}


class RuleTests(unittest.TestCase):
    def test_nested_and_or_not_and_absence(self):
        rule=group('and',group('or',course('CS:101'),course('CS:102')),group('not',group('and',course('CS:103'),course('CS:104'))))
        for bits in itertools.product((False,True),repeat=4):
            chosen={f'CS:{101+i}' for i,value in enumerate(bits) if value}
            self.assertEqual(evaluate(rule,chosen),(bits[0] or bits[1]) and not(bits[2] and bits[3]))
        self.assertTrue(evaluate(course('CS:101',False),set()))
        self.assertFalse(evaluate(course('CS:101',False),{'CS:101'}))

    def test_partial_evaluation_does_not_prune_possible_solutions(self):
        rule=group('and',group('or',course('CS:101'),course('CS:102')),course('CS:103',False))
        self.assertIsNone(evaluate(rule,set(),{'CS:101','CS:102','CS:103'}))
        self.assertTrue(evaluate(rule,{'CS:101'},{'CS:102'}))
        self.assertFalse(evaluate(rule,{'CS:103'},{'CS:101','CS:102'}))

    def test_generation_matches_reference_for_nested_exclusive_choices(self):
        sections=[section('CS:101:A'),section('CS:101:B','10:00','11:00'),section('CS:102:A','11:00','12:00'),section('CS:103:A','12:00','13:00'),section('CS:104:A','13:00','14:00')]
        # Exactly one of 101/102, plus 103 or 104, but not both.
        rule=group('and',group('or',course('CS:101'),course('CS:102')),group('not',group('and',course('CS:101'),course('CS:102'))),group('or',course('CS:103'),course('CS:104')),group('not',group('and',course('CS:103'),course('CS:104'))))
        expected=set()
        for subset in itertools.combinations(sections,2):
            keys={s['course_key'] for s in subset}
            if len(keys)==2 and evaluate(rule,keys):expected.add(frozenset(s['id'] for s in subset))
        actual=generate(sections,6,6,rules=rule)
        self.assertEqual(expected,{frozenset(ids) for ids in actual['schedules']})
        self.assertFalse(actual['limited'])

    def test_validation_rejects_bad_shapes_and_limits(self):
        deep=course('CS:101')
        for _ in range(8):deep=group('not',deep)
        cases=[group('or'),group('not'),group('not',course('CS:101'),course('CS:101')),course('missing'),{'op':'eval','code':'anything'},deep,group('and',*[course('CS:101')]*80),{**course('CS:101'),'present':'yes'}]
        for rule in cases:
            with self.subTest(rule=rule):
                with self.assertRaises(ValueError):validate_rule(rule,{'CS:101'})
        self.assertEqual(validate_rule(group('and'),set()),group('and'))

    def test_api_enforces_rule_in_generation(self):
        app=create_app({'TESTING':True});client=app.test_client();catalog=app.extensions['catalog'].load()
        sections=catalog['sections'][:3];keys=[s['course_key'] for s in sections]
        data={'term':catalog['term'],'catalog_revision':catalog['revision'],'section_ids':[s['id'] for s in sections],'min_credits':0,'max_credits':9,'rules':group('and',course(keys[0]),course(keys[1],False))}
        response=client.post('/api/v1/schedules/generate',json=data)
        self.assertEqual(response.status_code,200)
        self.assertTrue(response.json['schedules'])
        for schedule in response.json['schedules']:
            self.assertIn(sections[0]['id'],schedule)
            self.assertNotIn(sections[1]['id'],schedule)
        data['rules']=course('NOT:100')
        self.assertEqual(client.post('/api/v1/schedules/generate',json=data).status_code,400)
