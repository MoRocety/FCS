from flask import render_template, Blueprint, request, jsonify
from flask_cors import CORS
import json
import os
from pathlib import Path
from dataread import fileread, cap_first_preserve_case
from combcheck import *
from datetime import datetime, timedelta, timezone
from config import get_active_term, decode_term_code, get_active_term_human, set_active_term

cached_sections = []

my_blueprint = Blueprint('my_blueprint', __name__)
CORS(my_blueprint)

# Load data for the active term (defaults to ACTIVE_TERM file or env variable)
course_data, departments, courses, sections = fileread()

@my_blueprint.route('/old', methods=['GET', 'POST'])
def indexOld():
    return render_template("New_index.html")


@my_blueprint.route('/test', methods=['GET', 'POST'])
def indexOld2():
    return render_template("tester.html")

@my_blueprint.route('/paginationClick', methods=['POST'])
def paginator():
    page = int(request.form['page'])
    items_per_page = 20
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page

    global cached_sections
    filtered_sections = cached_sections

    sections_json = []

    for section in filtered_sections[start_index:end_index]:
        
        if section[8] != "TBD":
            instructor = section[8].title()
        
        else:
            instructor = section[8]

        sections_json.append({
            'department_id': section[0],
            'course_id': section[1],
            'section': section[2],
            'name': cap_first_preserve_case(section[3]),
            'credits': section[4],
            'days': "".join(filter(str.isalpha, section[5])),
            'start_time': section[6],
            'end_time': section[7],
            'instructor_name': instructor,
            'classroom': section[9],
            'alternate_classroom': section[10],
            'alternate_days': "".join(filter(str.isalpha, section[11])),
            'alternate_start_time': section[12],
            'alternate_end_time': section[13],
            #'total_seats': section[14],
            #'available_seats': section[15]
        })
    return json.dumps(sections_json, indent=2)


@my_blueprint.route('/', methods=['GET', 'POST'])
def index():
    
    if request.method == 'POST':
        dropdown_value = request.form['dropdown'].upper()
        dropdown2_value = request.form['dropdown2'].upper()
        dropdown3_value = request.form['dropdown3'].upper()

        filtered_sections = []

        for x in course_data:
            if dropdown_value == "ALL" or dropdown_value == "" or x[0].upper() == dropdown_value:
                if dropdown2_value == "ALL" or dropdown2_value == "" or x[3].upper() == dropdown2_value:
                    if dropdown3_value == "ALL" or dropdown3_value == "" or x[8].upper() == dropdown3_value:
                        filtered_sections.append(x)


        global cached_sections
        cached_sections = filtered_sections

        # Convert sections to JSON format
        sections_json = []

        # Showing simon else
        for section in filtered_sections[0:20]:
        
            if section[8] != "TBD":
                instructor = section[8].title()
            
            else:
                instructor = section[8]

            sections_json.append({
                'department_id': section[0],
                'course_id': section[1],
                'section': section[2],
                'name': cap_first_preserve_case(section[3]),
                'credits': section[4],
                'days': "".join(filter(str.isalpha, section[5])),
                'start_time': section[6],
                'end_time': section[7],
                'instructor_name': instructor,
                'classroom': section[9],
                'alternate_classroom': section[10],
                'alternate_days': "".join(filter(str.isalpha, section[11])),
                'alternate_start_time': section[12],
                'alternate_end_time': section[13],
                #'total_seats': section[14],
                #'available_seats': section[15]
            })

        return json.dumps({"data" : sections_json, "size": len(filtered_sections)}, indent=2)
    
    # Get current time in UTC
    current_time_utc = datetime.utcnow()

    # Set the timezone to Pakistan Standard Time (Asia/Karachi)
    pst_timezone = timezone(timedelta(hours=5))
    current_time_pst = current_time_utc.replace(tzinfo=timezone.utc).astimezone(pst_timezone)

    # Format the times in 12-hour format
    formatted_current_time = current_time_pst.strftime("%I:%M %p")
    
    # Get active term info
    active_term_code = get_active_term()
    active_term_name = get_active_term_human()
    
    return render_template('trying.html', 
                         current_time=formatted_current_time,
                         active_term=active_term_name,
                         active_term_code=active_term_code)


@my_blueprint.route('/updateTerm', methods=['POST'])
def update_term():
    global course_data, departments, courses, sections

    selected_value = request.json.get('selectedValue').upper()
    course_data, departments, courses, sections = fileread(selected_value)

    return "Data updated successfully"


@my_blueprint.route('/departments', methods=['GET'])
def get_departments():
    departments.sort()
    departments_ = [{'label': department, 'value': department} for department in departments]
    return json.dumps(departments_)


@my_blueprint.route('/courses', methods=['GET'])
def get_courses():
    courses_ = list(set([course[2] for course in courses]))
    courses_.sort()
    courses_ = [{'label': cap_first_preserve_case(course), 'value': cap_first_preserve_case(course)} for course in courses_]
    return json.dumps(courses_)


@my_blueprint.route('/instructors', methods=['GET'])
def get_instructors():
    instructors = list(set([x[6] for x in sections]))
    instructors.sort()
    unique_instructors = [{'label': instructor, 'value': instructor} for instructor in instructors]
    return json.dumps(unique_instructors)


@my_blueprint.route('/updateDepartment', methods=['POST'])
def update_department():
    data = request.get_json()['data'].upper()  # Extract 'data' from the request JSON
    instructors_ = list(set([x[6] for x in sections if x[0] == data]))
    courses_ = list(set(course[2] for course in courses if course[0] == data))
    
    instructors_ = [
    {'label': instructor.title(), 'value': instructor.title()} if instructor != 'TBD'
      else {'label': instructor.upper(), 'value': instructor.upper()}
    for instructor in instructors_
    ]

    courses_.sort()
    courses_ = [{'label': cap_first_preserve_case(course), 'value': cap_first_preserve_case(course)} for course in courses_]

    response_data = {
        'courses': courses_,
        'instructors': instructors_
    }

    return json.dumps(response_data)


@my_blueprint.route('/updateInstructor', methods=['POST'])
def update_instructor():
    data = request.get_json()['data'].upper()
    department = request.get_json()['department'].upper()

    filtered_courses = []

    for x in course_data:
        if (department == "ALL" or department == "" or x[0].upper() == department) and \
        (data == "ALL" or data == "" or x[8].upper() == data):
            filtered_courses.append(x[3])

    courses_ = list(set(filtered_courses))    
    courses_.sort()

    courses_ = [
    {'label': course.title(), 'value': course.title()} if course != 'TBD'
      else {'label': course.upper(), 'value': course.upper()}
    for course in courses_
    ]

    response_data = {
        'courses': courses_
    }

    return json.dumps(response_data)


@my_blueprint.route('/updateCourse', methods=['POST'])
def update_course():
    data = request.get_json()['data'].upper()
    department = request.get_json()['department'].upper()

    filtered_instructors = []

    for x in course_data:
        if (department == "ALL" or department == "" or x[0].upper() == department) and \
        (data == "ALL" or data == "" or x[3].upper() == data):
            filtered_instructors.append(x[8])

    instructors_ = list(set(filtered_instructors))    
    instructors_.sort()

    instructors_ = [
    {'label': instructor.title(), 'value': instructor.title()} if instructor != 'TBD'
      else {'label': instructor.upper(), 'value': instructor.upper()}
    for instructor in instructors_
    ]

    response_data = {
        'instructors': instructors_
    }

    return json.dumps(response_data)


@my_blueprint.route('/submit', methods=['POST'])
def submit_selected_courses():
    data = request.json
    selected_courses = data['selectedCourses']
    crucial_courses = data['checkedCrucials']
    # Your code to process the selected courses on the backend

    shortlist = [course for short_course in selected_courses for course in course_data
                 if (short_course['department_id'] == course[0])
                 and (short_course['course_id'] == course[1])
                 and (short_course['section'] == course[2])]

    shortlist = [[*sublist[:4], int(sublist[4]), *sublist[5:]] for sublist in shortlist]

    min_credit = int(data['minCredit'])
    max_credit = int(data['maxCredit'])

    credit_filtered_combinations = credit_check(shortlist, min_credit, max_credit)
    
    filtered_combinations = [filtered_comb for filtered_comb in credit_filtered_combinations
                             if duplicate_checker(filtered_comb) is False
                             and clash_check(filtered_comb) is False]

    filtered_combinations = [filtered_comb for filtered_comb in filtered_combinations
                          if crucial(filtered_comb, [course["department_id"] + course["course_id"] for course in crucial_courses])]

    combinations_lst = []
    for combination in filtered_combinations:
        combination_data = []
        for section in combination:
            course_data_ = {
                'department_id': section[0],
                'course_id': section[1],
                'section': section[2],
                'name': section[3],
                'credits': section[4],
                'days': "".join(filter(str.isalpha, section[5])),
                'start_time': section[6],
                'end_time': section[7],
                'instructor_name': section[8],
                'classroom': section[9],
                'alternate_classroom': section[10],
                'alternate_days': "".join(filter(str.isalpha, section[11])),
                'alternate_start_time': section[12],
                'alternate_end_time': section[13],
                #'total_seats': section[14],
                #'available_seats': section[15]
            }
            combination_data.append(course_data_)

        combinations_lst.append(combination_data)
 
    # Return a response
    return json.dumps(combinations_lst)


@my_blueprint.route('/webhook/update-courses', methods=['POST'])
def update_courses_webhook():
    """
    Webhook endpoint for GitHub Actions to push updated course data.
    
    Expected JSON payload:
    {
        "term_code": "2025FA",
        "content": "... course data file content ..."
    }
    
    Headers:
    X-Webhook-Token: secret token for authentication
    """
    # Auth check
    auth_token = request.headers.get('X-Webhook-Token')
    webhook_secret = os.environ.get('WEBHOOK_SECRET', 'change_this_in_production')
    
    if auth_token != webhook_secret:
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid webhook token'}), 401
    
    try:
        data = request.json
        term_code = data.get('term_code')
        content = data.get('content')
        
        if not term_code or not content:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Missing term_code or content in request body'
            }), 400
        
        # Save the data file
        filename = f"{term_code}data.txt"
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Saved course data to {filepath}")
        
        # Update the ACTIVE_TERM file
        active_term_file = Path(__file__).parent / 'ACTIVE_TERM'
        with open(active_term_file, 'w') as f:
            f.write(term_code)
        
        print(f"Updated ACTIVE_TERM to {term_code}")
        
        # Reload the course data globally
        global course_data, departments, courses, sections
        course_data, departments, courses, sections = fileread(term_code)
        
        # Clear cached sections
        global cached_sections
        cached_sections = []
        
        human_readable = decode_term_code(term_code)
        
        return jsonify({
            'success': True,
            'message': f'Successfully updated course data for {human_readable}',
            'term_code': term_code,
            'term_name': human_readable,
            'courses_loaded': len(course_data),
            'departments_count': len(departments)
        }), 200
        
    except Exception as e:
        print(f"Error in webhook: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@my_blueprint.route('/api/active-term', methods=['GET'])
def get_active_term_info():
    """
    Get information about the currently active term.
    """
    term_code = get_active_term()
    term_human = get_active_term_human()
    
    return jsonify({
        'term_code': term_code,
        'term_name': term_human,
        'courses_count': len(course_data),
        'departments_count': len(departments)
    })
