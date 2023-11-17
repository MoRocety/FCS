from requests import Session
from bs4 import BeautifulSoup
import json

sess = Session()
terms = ['2023FA', 'PH23FA']

for term in terms:

    page = sess.get('https://empower.fccollege.edu.pk/fusebox.cfm?fuseaction=CourseCatalog&rpt=1').content
    soup = BeautifulSoup(page, 'html.parser')
    data = soup.find('div',id='center_col').find_all('script')[1].get_text().replace('\r', '').replace('\n', '').replace(' ', '').split(';')

    jsonkey = data[0].replace('"', '').split('=')[1]
    utoken = data[1].replace('"', '').split('=')[1]


    params = {
        'fuseaction': 'CourseCatalog',
        'screen_width': '1920',
        'empower_global_term_id': term,
        'cs_descr': "",
        'empower_global_dept_id': '',
        'empower_global_course_id': '',
        'cs_sess_id': '',
        'cs_loca_id': '',
        'cs_inst_id': '',
        'cs_emph_id': '',
        'CS_time_start': '',
        'CS_time_end': '',
        'status': '1',
        utoken: jsonkey,
    }

    # Send the POST request using the session
    re = sess.post(f'https://empower.fccollege.edu.pk/cfcs/courseCatalog.cfc?method=GetList&returnformat=json&', params=params)
    content = json.loads(re.content)

    # Write the JSON content to a file
    with open(f"{term}.json", "w", encoding="utf-8") as f:
        json.dump(content, f, indent=4)

    print("JSON content written to 'output.json' file.")

