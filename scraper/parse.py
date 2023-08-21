from bs4 import BeautifulSoup
import json

datasets = ['2023FA', 'PH23FA']

for ds in datasets:
    with open(f"{ds}.json", "r") as f:
        jsondata= json.load(f)

    soup = BeautifulSoup(jsondata["html"], "html.parser")

    courses = soup.find_all("div",class_='ui-grid-row')

    outfile = open(f"{ds}data.txt", "w", encoding="UTF-8")

    for course in courses[2:]:
        attr=course.find_all("div")

        # Whole course in one row, these are courses without multiple schedules
        if len(attr) == 9:
            # Dealing with Col 1
            col1 = attr[1].text.strip().split()

            dept = col1[0].strip()
            course_code = col1[1].strip()
            section = col1[2].strip()

            # Processing name
            unprocessed_name = col1[3:]
            name = ""
            for n in unprocessed_name:
                name += n
                name += " "

            name = name.strip().strip("*") 

            # Col 2 with just the credits
            credits = attr[2].text.strip()

            # Col 3 with classroom
            classroom = attr[3].text.strip()

            # Col 4 with the schedule
            col4 = attr[4].text.strip().split("\n")

            start = col4[0].strip().split(":")[1]
            days = []

            for d in col4[1].strip().replace(" ", ""):
                days.append(d)

            days = [d for d in days if d != " "]

            if len(col4) == 3:
                time = col4[2].strip().split("-")
                start_time = time[0].strip()
                end_time = time[1].strip()

            else:
                start_time = None
                end_time = None

            # Col 5 with just instructor
            instructor = ' '.join(attr[5].text.strip().split())

            # Col 6 with total seats
            total_seats = attr[6].text.strip()

            # Col 7 with available seats
            available_seats = attr[7].text.strip()

            # Values not present
            alternate_classroom = None
            alternate_days = None
            alternate_start_time = None
            alternate_end_time = None

            print(dept, course_code, section, name, credits, days, start_time, end_time, instructor, classroom, alternate_classroom, alternate_days, alternate_start_time, alternate_end_time, total_seats, available_seats, file=outfile, sep="!!")


        # If two liner then partially one line, partially another
        elif len(attr) == 6:
            # Dealing with Col 1
            col1 = attr[1].text.strip().split()
            
            dept = col1[0].strip()
            course_code = col1[1].strip()
            section = col1[2].strip()

            # Processing name
            unprocessed_name = col1[3:]
            name = ""
            for n in unprocessed_name:
                name += n
                name += " "

            name = name.strip().strip("*") 

            # Col 2 with just the credits
            credits = attr[2].text.strip()

            # Col 3 with classroom
            classroom = attr[3].text.strip()

            # Col 4 with the schedule
            col4 = attr[4].text.strip().split("\n")

            start = col4[0].strip().split(":")[1]
            days = []

            for d in col4[1].strip().replace(" ", ""):
                days.append(d)
            
            days = [d for d in days if d != " "]

            if len(col4) == 3:
                time = col4[2].strip().split("-")
                start_time = time[0].strip()
                end_time = time[1].strip()
            
            else:
                start_time = None
                end_time = None

            # Col 5 with just instructor
            instructor = ' '.join(attr[5].text.strip().split())

        # The second partially, seats here
        elif len(attr) == 7:
            # Col 1 with alternate classroom
            alternate_classroom = attr[1].text.strip()

            # Col 2 with alternate schedule
            col2 = attr[2].text.strip().split("\n")

            alternate_start = col2[0].strip().split(":")[1]

            alternate_days = []
            for d in "".join(col2[1].strip()):
                alternate_days.append(d)        

            alternate_days = [d for d in alternate_days if d != " "]

            if len(col2) == 3:
                time = col2[2].strip().split("-")
                alternate_start_time = time[0].strip()
                alternate_end_time = time[1].strip()
            
            else:
                alternate_start_time = None
                alternate_end_time = None

            # Skipping Col 3 cos we have the instructor already, moving to col 4 for total seats
            total_seats = attr[4].text.strip()

            # Col 5 for available seats
            available_seats = attr[5].text.strip()

            print(dept, course_code, section, name, credits, days, start_time, end_time, instructor, classroom, alternate_classroom, alternate_days, alternate_start_time, alternate_end_time, total_seats, available_seats, file=outfile, sep="!!")


    outfile.close()
