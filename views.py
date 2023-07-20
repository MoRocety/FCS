from flask import render_template, Blueprint, request
from flask_cors import CORS
import json
from dataread import *
from combcheck import *

my_blueprint = Blueprint('my_blueprint', __name__)
CORS(my_blueprint)

department_id = 'COMP'  # Replace with the specific department ID
course_id = '200'  # Replace with the specific course ID


@my_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        dropdown_value = request.form['dropdown']
        dropdown2_value = request.form['dropdown2']
        dropdown3_value = request.form['dropdown3']

        filtered_sections = course_data

        
        if dropdown_value != "all":
            filtered_sections = [x for x in filtered_sections if x[0] == dropdown_value]

        if dropdown2_value != "all":
            filtered_sections = [x for x in filtered_sections if x[3] == dropdown2_value]

        if dropdown3_value != "all":
            filtered_sections = [x for x in filtered_sections if x[8] == dropdown3_value]
        
        # Convert sections to JSON format
        sections_json = []
        for section in filtered_sections:
            sections_json.append({
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
            })

        return json.dumps(sections_json, indent=2)
    
    return render_template('New_index.html')


@my_blueprint.route('/departments', methods=['GET'])
def get_departments():
    departments.sort()
    departments_ = [{'label': department, 'value': department} for department in departments]
    return json.dumps(departments_)

@my_blueprint.route('/courses', methods=['GET'])
def get_courses():
    courses_ = [{'label': course[2], 'value': course[2]} for course in courses]
    return json.dumps(courses_)

@my_blueprint.route('/instructors', methods=['GET'])
def get_instructors():
    instructors = list(set([x[6] for x in sections]))
    instructors.sort()
    unique_instructors = [{'label': instructor, 'value': instructor} for instructor in instructors]
    return json.dumps(unique_instructors)

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


