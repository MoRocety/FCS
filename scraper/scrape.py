import requests
from time import sleep

cookies = {
    'JSESSIONID': 'F8149F95A75CEB433114652C3342A292.cfusion',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'Cookie': 'JSESSIONID=F8149F95A75CEB433114652C3342A292.cfusion',
    'Origin': 'https://empower.fccollege.edu.pk',
    'Referer': 'https://empower.fccollege.edu.pk/fusebox.cfm?fuseaction=CourseCatalog&rpt=1',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params = {
    'method': 'GetList',
    'returnformat': 'json',
    'uEAD241C9EDDCED6F003745D78F1726ACC6AB32D8CA376D1C3528AC3334EE5DCC37CCB03EFAAA18B8DE6F9DFCDC2A13AF28ACBAF5A3002E2EFC12E08ABE6C262A': 'DB68DAF12AC39EB86B1F0DE905AB32AA56E51911EE63D6A5DA42775F07429541FABBF08F3564F4C94EBB0A0BC89D98C1',
}

data = {
    'fuseaction': 'CourseCatalog',
    'screen_width': '1536',
    'empower_global_term_id': '2023FA',
    'cs_descr': '',
    'empower_global_dept_id': '',
    'empower_global_course_id': '',
    'cs_sess_id': '',
    'cs_loca_id': '',
    'cs_inst_id': '',
    'cs_classroom': '',
    'cs_emph_id': '',
    'CS_time_start': '',
    'CS_time_end': '',
    'status': '1',
}

response = requests.post(
    'https://empower.fccollege.edu.pk/cfcs/courseCatalog.cfc',
    params=params,
    cookies=cookies,
    headers=headers,
    data=data,
)

with open("2023FA.json", "wb") as f:
    f.write(response.content)



cookies = {
    'JSESSIONID': 'F8149F95A75CEB433114652C3342A292.cfusion',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'Cookie': 'JSESSIONID=F8149F95A75CEB433114652C3342A292.cfusion',
    'Origin': 'https://empower.fccollege.edu.pk',
    'Referer': 'https://empower.fccollege.edu.pk/fusebox.cfm?fuseaction=CourseCatalog&rpt=1',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params = {
    'method': 'GetList',
    'returnformat': 'json',
    'uEAD241C9EDDCED6F003745D78F1726ACC6AB32D8CA376D1C3528AC3334EE5DCC37CCB03EFAAA18B8DE6F9DFCDC2A13AF28ACBAF5A3002E2EFC12E08ABE6C262A': 'DB68DAF12AC39EB86B1F0DE905AB32AA56E51911EE63D6A5DA42775F07429541FABBF08F3564F4C94EBB0A0BC89D98C1',
}

data = {
    'fuseaction': 'CourseCatalog',
    'screen_width': '1536',
    'empower_global_term_id': '2023FA',
    'cs_descr': '',
    'empower_global_dept_id': '',
    'empower_global_course_id': '',
    'cs_sess_id': '',
    'cs_loca_id': '',
    'cs_inst_id': '',
    'cs_classroom': '',
    'cs_emph_id': '',
    'CS_time_start': '',
    'CS_time_end': '',
    'status': '1',
}

response = requests.post(
    'https://empower.fccollege.edu.pk/cfcs/courseCatalog.cfc',
    params=params,
    cookies=cookies,
    headers=headers,
    data=data,
)

with open("PH23FA.json", "wb") as f:
    f.write(response.content)


