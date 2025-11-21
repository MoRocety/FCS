from bs4 import BeautifulSoup
import json
import sys
import os
from pathlib import Path

# If ACTIVE_TERM is specified, use that. Otherwise, parse all available JSON files.
def get_datasets_to_parse():
    """
    Get the active term to parse.
    Only parses the term specified in ACTIVE_TERM file.
    """
    # Read active term from ACTIVE_TERM file (one level up from scraper/)
    active_term_file = Path(__file__).parent.parent / 'ACTIVE_TERM'
    
    if active_term_file.exists():
        term_code = active_term_file.read_text().strip()
        print(f"Active term from ACTIVE_TERM file: {term_code}")
        return [term_code]
    
    # Fallback: check environment variable
    term_code = os.environ.get('ACTIVE_TERM')
    if term_code:
        print(f"Active term from environment: {term_code}")
        return [term_code]
    
    # Last resort: fail with clear error
    print("ERROR: No ACTIVE_TERM file or environment variable found!")
    print("The scraper should have created ACTIVE_TERM file.")
    sys.exit(1)

datasets = get_datasets_to_parse()

for ds in datasets:
    with open(f"{ds}.json", "r") as f:
        jsondata= json.load(f)
    
    # Check if we got valid data
    if "html" not in jsondata:
        print(f"✗ Error: {ds}.json does not contain 'html' field")
        print(f"  JSON keys found: {list(jsondata.keys())}")
        print(f"  Content preview: {str(jsondata)[:200]}")
        continue

    soup = BeautifulSoup(jsondata["html"], "html.parser")

    courses = soup.find_all("div",class_='ui-grid-row')

    outfile = open(f"{ds}data.txt", "w", encoding="UTF-8")

    for course in courses[2:]:
        attr=course.find_all("div")

        try:

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

                try:
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
                except (IndexError, ValueError) as e:
                    print(f"\n❌ Error parsing schedule column (col4):")
                    print(f"Error type: {type(e).__name__}: {e}")
                    print(f"Raw div content (attr[4]):")
                    print(f"{attr[4]}")
                    print(f"Split col4 content: {col4}")
                    print(f"Course context: {dept} {course_code}-{section} {name}")
                    raise

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

        except Exception as e:
            print(f"\n❌ Error parsing course:")
            print(f"  Error: {e}")
            print(f"  len(attr): {len(attr)}")
            print(f"  Full div content:")
            print(f"  {course.prettify()}")
            print("\n")
            continue

    outfile.close()
    print(f"✓ Parsed {ds}.json -> {ds}data.txt")

print(f"\n✓ Successfully parsed {len(datasets)} dataset(s)")
