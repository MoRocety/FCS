def fileread(term):
    if term == "2023 FALL":
        infile = open("falldata.txt", "r")

    elif term == "PHARMACY PROGRAM FALL 2023":
        infile = open("pharmdata.txt", "r")

    course_data = infile.read().split("\n")

    infile.close()

    filtered_course_data = [x.split("!!") for x in course_data[:-1]]
    course_data = []

    for x in filtered_course_data:
        if x[1].isdigit():
            if int(x[1]) < 500:
                course_data.append(x)

        elif alplusnum(x[1]):
            if int(x[1][:-1]) < 500:
                course_data.append(x)

        else:
            # Do nothing for non-numeric and non-alphanumeric values
            pass


    # Taking care of table 1
    departments = list(set([x[0] for x in course_data]))

    # Getting to table 2
    # DEPT, ID, NAME, CREDITS
    courses = list(set((x[0], x[1], cap_first_preserve_case(x[3]), x[4]) for x in course_data))
    courses = sorted(courses, key=lambda x: (x[0], x[1]))

    # Getting to table 3
    # DEPT, ID, SECTION, DAYS, START, END, INSTRUCTOR, CLASSROOM, ALT CLASSROOM, ALT DAYS, ALT START, ALT END
    sections = []
    for x in course_data:
        result = x[5]
        start = x[6]
        end = x[7]

        if start == "None":
            start = None
        
        if end == "None":
            end = None

        instructor = x[8]

        if instructor != "TBD":
            instructor = instructor.title()

        filtered_data = [x[0], x[1], x[2], result, start, end, instructor, x[9], None, None, None, None]

        if x[10] != "None":
            alt_result = x[11]
            filtered_data[8], filtered_data[9], filtered_data[10], filtered_data[11] = x[10], alt_result, x[12], x[13]

        sections.append(tuple(filtered_data))

    return course_data, departments, courses, sections
        

def cap_first_preserve_case(s):
    if len(s) == 0:
        return s
    return s[:1].upper() + s[1:]

def alplusnum(input_string):
    has_numbers = any(char.isdigit() for char in input_string)
    has_alphabets = any(char.isalpha() for char in input_string)
    
    return has_numbers and has_alphabets
