from itertools import combinations
from datetime import datetime
import ast

def credit_check(courses, LL_credit_hours, UL_credit_hours):
    # If there are no courses, return an empty list
    if not courses:
        return []

    # Find the maximum and minimum credit hours among the courses
    max_credit_hours = max(course[4] for course in courses)
    min_credit_hours = min(course[4] for course in courses if course[4] != 0)

    # If the maximum credit hours is 0, handle special cases
    if max_credit_hours == 0:
        # If the lower limit credit hours is also 0, return all combinations of courses
        if LL_credit_hours == 0:
            return [combination for r in range(1, len(courses)+1) for combination in combinations(courses, r)]
        else:
            # Otherwise, there are no valid combinations, return an empty list
            return []

    combinations_list = []

    # Calculate the lower and upper limit number of courses based on credit hours
    LL = (LL_credit_hours // max_credit_hours)
    UL = (min(len(courses), (UL_credit_hours // min_credit_hours))) + 1
                             
    # Iterate over different numbers of courses
    for r in range(LL, UL):
        # Generate combinations of courses for the current number of courses
        for combination in combinations(courses, r):
            total_credit_hours = sum(course[4] for course in combination)

            # Check if the total credit hours fall within the desired range
            if LL_credit_hours <= total_credit_hours <= UL_credit_hours:
                combinations_list.append(combination)

    return [combination for combination in combinations_list if combination]


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

