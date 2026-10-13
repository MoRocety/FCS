import itertools
import unittest
from fcs.scheduling import conflicts, generate
from fcs.catalog import parse_rows, CatalogRepository
from app import create_app
from unittest.mock import patch
import tempfile
from pathlib import Path


def section(identity, start='09:00', end='10:00', days=('M',), credits=3, alternate=None):
    dept, number, sec = identity.split(':')
    return {'id': identity, 'course_key': f'{dept}:{number}', 'department': dept, 'number': number,
            'section': sec, 'name': 'Test course', 'credits': credits, 'instructor': 'Test Teacher',
            'total_seats': 30, 'available_seats': 5,
            'meetings': [{'start': start, 'end': end, 'days': list(days), 'room': 'A1'}] + ([alternate] if alternate else [])}


class SchedulingTests(unittest.TestCase):
    def test_back_to_back_is_allowed(self):
        self.assertFalse(conflicts(section('CS:101:A'), section('CS:102:A', '10:00', '11:00')))

    def test_contained_meeting_is_conflict(self):
        self.assertTrue(conflicts(section('CS:101:A'), section('CS:102:A', '09:15', '09:45')))

    def test_alternate_meeting_is_checked(self):
        lab = {'start': '14:00', 'end': '16:00', 'days': ['F'], 'room': 'Lab'}
        self.assertTrue(conflicts(section('CS:101:A', alternate=lab), section('CS:102:A', '15:00', '17:00', ('F',))))

    def test_different_days_are_allowed(self):
        self.assertFalse(conflicts(section('CS:101:A'), section('CS:102:A', days=('T',))))

    def test_matches_exhaustive_reference_with_decimal_and_zero_credits(self):
        sections = [section('CS:101:A'), section('CS:101:B','11:00','12:00'),
                    section('CS:102:A','09:30','10:30',credits=1.5),
                    section('CS:103:A','12:00','13:00',credits=0),
                    section('CS:104:A','10:00','11:00',credits=2.5)]
        expected = set()
        for count in range(1, len(sections)+1):
            for subset in itertools.combinations(sections,count):
                keys = [s['course_key'] for s in subset]
                if len(set(keys)) != len(keys) or 'CS:101' not in keys:
                    continue
                if any(conflicts(a,b) for a,b in itertools.combinations(subset,2)):
                    continue
                if 3 <= sum(s['credits'] for s in subset) <= 7:
                    expected.add(frozenset(s['id'] for s in subset))
        result = generate(sections,3,7,{'CS:101'})
        self.assertEqual(expected,{frozenset(ids) for ids in result['schedules']})
        self.assertFalse(result['limited'])

    def test_result_and_work_limits(self):
        sections=[section(f'CS:{100+i}:A', days=('M',), start='09:00',end='10:00') for i in range(30)]
        result=generate(sections,0,30,set(),limit=3)
        self.assertEqual(len(result['schedules']),3)
        self.assertTrue(result['limited'])
        result=generate(sections,0,30,set(),budget=5)
        self.assertLessEqual(result['visited'],5)
        self.assertTrue(result['limited'])


class CatalogTests(unittest.TestCase):
    def test_real_catalog_and_scraper_path(self):
        catalog=CatalogRepository().load()
        self.assertGreater(len(catalog['sections']),500)
        self.assertEqual(len({s['id'] for s in catalog['sections']}),len(catalog['sections']))

    def test_parser_accepts_decimal_credits_and_lab(self):
        content="CS!!101!!A!!Programming!!4.00!!['M']!!09:00!!10:00!!TBD!!Room!!Lab!!['F']!!14:00!!16:00!!30!!2"
        parsed=parse_rows(content)[0]
        self.assertEqual(parsed['credits'],4)
        self.assertEqual(len(parsed['meetings']),2)

    def test_bad_catalog_rejected(self):
        for content in ['', 'broken', "CS!!101!!A!!X!!3!!['M']!!11:00!!10:00!!TBD!!R!!None!!None!!None!!None!!30!!3"]:
            with self.assertRaises(ValueError):parse_rows(content)


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.app=create_app({'TESTING':True})
        self.client=self.app.test_client()
        self.catalog=self.app.extensions['catalog'].load()
        self.identity=self.catalog['sections'][0]['id']

    def post(self, **extra):
        data={'term':self.catalog['term'],'catalog_revision':self.catalog['revision'],'section_ids':[self.identity], 'min_credits':0,'max_credits':22}
        data.update(extra)
        return self.client.post('/api/v1/schedules/generate',json=data)

    def test_home_assets_and_catalog(self):
        self.assertEqual(self.client.get('/').status_code,200)
        with self.client.get('/static/planner.js') as response:
            self.assertEqual(response.status_code,200)
        self.assertEqual(self.client.get('/api/v1/catalog').status_code,200)

    def test_valid_schedule(self):
        result=self.post()
        self.assertEqual(result.status_code,200)
        self.assertEqual(result.json['schedules'],[[self.identity]])

    def test_invalid_requests(self):
        for extra in [{'catalog_revision':'outdated'},{'term':'2020FA'},{'section_ids':['missing']},{'section_ids':[]},
                      {'section_ids':[self.identity]*61},{'min_credits':23,'max_credits':20},
                      {'min_credits':float('nan')},{'max_credits':float('inf')},
                      {'required_course_keys':['missing']},{'section_ids':[{}]}, {'min_credits':None}]:
            with self.subTest(extra=extra):self.assertEqual(self.post(**extra).status_code,400)
        self.assertEqual(self.client.post('/api/v1/schedules/generate',json=[]).status_code,400)

    def test_legacy_filter_and_generate(self):
        s=self.catalog['sections'][0]
        response=self.client.post('/',data={'dropdown':s['department'],'dropdown2':'all','dropdown3':'all'})
        self.assertGreater(response.json['size'],0)
        result=self.client.post('/submit',json={'selectedCourses':[{'department_id':s['department'],'course_id':s['number'],'section':s['section']}], 'checkedCrucials':[], 'minCredit':0,'maxCredit':22})
        self.assertEqual(result.status_code,200)
        self.assertEqual(len(result.json['schedules']),1)

    def test_webhook_denies_unconfigured_secret(self):
        with patch.dict('os.environ',{},clear=True):
            self.assertEqual(self.client.post('/webhook/update-courses',headers={'X-Webhook-Token':'change_this_in_production'},json={}).status_code,401)

    def test_webhook_rejects_path_traversal_and_bad_data(self):
        with patch.dict('os.environ',{'WEBHOOK_SECRET':'test-secret'}):
            for data in [{'term_code':'../bad','content':'x'},{'term_code':'2027SP','content':'broken'}]:
                self.assertEqual(self.client.post('/webhook/update-courses',headers={'X-Webhook-Token':'test-secret'},json=data).status_code,400)

    def test_webhook_success_and_catalog_cache_refresh(self):
        content="CS!!101!!A!!Programming!!3.00!!['M']!!09:00!!10:00!!TBD!!Room!!None!!None!!None!!None!!30!!2"
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'ACTIVE_TERM').write_text('2027SP')
            (root/'2027SPdata.txt').write_text(content)
            with patch('config.BASE_DIR',root), patch('fcs.catalog.BASE_DIR',root), patch('views.BASE_DIR',root), patch.dict('os.environ',{'WEBHOOK_SECRET':'test-secret'}):
                before=self.client.get('/api/v1/catalog').json
                response=self.client.post('/webhook/update-courses',headers={'X-Webhook-Token':'test-secret'},json={'term_code':'2027SP','content':content.replace('!!30!!2','!!30!!5')})
                self.assertEqual(response.status_code,200)
                after=self.client.get('/api/v1/catalog').json
                self.assertEqual(after['sections'][0]['available_seats'],5)
                self.assertNotEqual(before['revision'],after['revision'])
                self.assertEqual(len(list(root.iterdir())),2)

    def test_unavailable_catalog_does_not_break_home(self):
        with patch.object(self.app.extensions['catalog'],'load',side_effect=FileNotFoundError('Missing catalog')):
            self.assertEqual(self.client.get('/').status_code,200)
            self.assertEqual(self.client.get('/api/v1/catalog').status_code,503)

if __name__=='__main__':unittest.main()
