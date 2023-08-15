from flask import render_template, Blueprint, request
from flask_cors import CORS
import json
from dataread import fileread, cap_first_preserve_case
from combcheck import *

my_blueprint = Blueprint('my_blueprint', __name__)
CORS(my_blueprint)

course_data, departments, courses, sections = fileread("2023 FALL")

@my_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        dropdown_value = request.form['dropdown'].upper()
        dropdown2_value = request.form['dropdown2'].upper()
        dropdown3_value = request.form['dropdown3'].upper()

        print(dropdown_value, dropdown2_value, dropdown3_value)
        filtered_sections = course_data

        if not (dropdown_value == "ALL" or dropdown_value == ""):
            filtered_sections = [x for x in filtered_sections if x[0].upper() == dropdown_value]

        if not (dropdown2_value == "ALL" or dropdown2_value == ""):
            filtered_sections = [x for x in filtered_sections if x[3].upper() == dropdown2_value]

        if not (dropdown3_value == "ALL" or dropdown3_value == ""):
            filtered_sections = [x for x in filtered_sections if x[8].upper() == dropdown3_value]
        
        # Convert sections to JSON format
        sections_json = []
        for section in filtered_sections:
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
                'alternate_end_time': section[13]
            })

        return json.dumps(sections_json, indent=2)
    
    return render_template('trying.html')


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

# Will look into it later
'''
@my_blueprint.route('/updateCourse', methods=['POST'])
def update_course():
    data = request.get_json()['data'].upper()
    instructors_ = list(set([x[8] for x in course_data if x[3].upper() == data]))
    
    instructors_.sort()

    instructors_ = [
    {'label': instructor.title(), 'value': instructor.title()} if instructor != 'TBD'
      else {'label': instructor.upper(), 'value': instructor.upper()}
    for instructor in instructors_
    ]

    response_data = {
        'instructors': instructors_
    }

    return json.dumps(response_data)'''


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

    combinations_dict = {}
    for i, combination in enumerate(filtered_combinations, start=1):
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
                'alternate_end_time': section[13] 
            }
            combination_data.append(course_data_)

        combinations_dict[f'Combination {i}'] = combination_data
 
    # Return a response
    return json.dumps(combinations_dict)


