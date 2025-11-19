from itertools import combinations
from datetime import datetime
import ast

def credit_check(courses, LL_credit_hours, UL_credit_hours):
    # If there are no courses, return an empty list
    if not courses:
        return []

    # Sort the list in descending order by credits
    courses = sorted(courses, key=lambda x: x[4], reverse=True)

    # Iterate through it to find the minimum value for the lower limit
    temp_lower = 0
    temp_LL = 0
    LL = 0

    for course in courses:
        temp_lower += course[4]
        temp_LL += 1

        # if greater than or equal to lower credit hours, break
        if (temp_lower >= LL_credit_hours):
            LL = temp_LL
            break

    if LL == 0:
        return []

    # Iterate through it in reverse order to find the minimum value for the upper limit
    temp_upper = 0
    UL = 0

    for course in courses[::-1]:
        temp_upper += course[4]

        if temp_upper <= UL_credit_hours:
            UL += 1
        else:
            break

    combinations_list = []

    # Iterate over different numbers of courses
    for r in range(LL, UL+1):
        # Generate combinations of courses for the current number of courses
        for combination in combinations(courses, r):
            total_credit_hours = sum(course[4] for course in combination)

            # Check if the total credit hours fall within the desired range
            if LL_credit_hours <= total_credit_hours <= UL_credit_hours:
                combinations_list.append(combination)

    return combinations_list


def duplicate_checker(comb):
    dic = {x[0] + x[1]: 0 for x in comb}

    for course in comb:
        course_code = course[0] + course[1]
        if dic[course_code] == 0:
            dic[course_code] += 1

        else:
            return True

    return False

def clash_check(courses):
    processed_courses = list(courses)
    additional_courses = []

    for course in processed_courses:
        if course[-3] != "None":
            to_append = course[0:5] + course[11:]
            additional_courses.append(to_append)

    processed_courses.extend(additional_courses)
    processed_courses = [x for x in processed_courses if x[6] != "None"]

    for i in range(len(processed_courses) - 1):
        course1 = processed_courses[i]
        course1_days = set(ast.literal_eval(course1[5]))

        course1_start = datetime.strptime(course1[6], "%H:%M").time()
        course1_end = datetime.strptime(course1[7], "%H:%M").time()

        for j in range(i + 1, len(processed_courses)):
            course2 = processed_courses[j]
            course2_days = set(ast.literal_eval(course2[5]))

            course2_start = datetime.strptime(course2[6], "%H:%M").time()
            course2_end = datetime.strptime(course2[7], "%H:%M").time()

            if course1_days.intersection(course2_days):
                
                if (course1_start <= course2_start <= course1_end)\
                    or (course1_start <= course2_end <= course1_end)\
                    or (course2_start <= course1_start <= course2_end)\
                    or (course2_start <= course1_end <= course2_end):
                        
                        return True

    return False

def crucial(comb, courses):
    courses_in_comb = [x[0]+x[1] for x in comb]

    for course in courses:
        if course not in courses_in_comb:
            return False
        
    return True

