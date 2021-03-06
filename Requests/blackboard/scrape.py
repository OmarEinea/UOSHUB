from Requests import clean_course_name as __clean
from lxml.etree import fromstring as __parse_xml
from .values import __types, __events, __terms, __timestamp, __document_ids
from math import ceil
import re


# Scrapes useful data from updates JSON object
def updates(raw_updates, courses):
    # Dictionary to store updates data
    data = []
    # Loop through updates
    for update in raw_updates:
        # Keep a reference of used object indexes
        item = update["itemSpecificData"]
        details = item["notificationDetails"]
        # Extract Blackboard id and store its equivalent MyUDC id
        course_key = courses.get(details["courseId"][1:-2])
        # Skip non-student courses
        if not course_key: continue
        # Store update's event parts
        event = update["extraAttribs"]["event_type"].split(":")
        # Append the update as a dictionary to data
        data.append({
            # Store title, time, dismiss id & course key
            "course": course_key,
            "title": item["title"],
            "dismiss": details["actorId"],
            "time": __timestamp(update["se_timestamp"] / 1000).strftime("%Y-%m-%dT%H:%M:%S") + "+0400",
            # Store update message body content if present
            "body": details["announcementBody"] or item["contentExtract"],
            # Get meaningful equivalent of event type from stored values
            "event": __types[event[0]] + (
                # Add event type as long as it's not an announcement
                " " + __events.get(event[1].split("_")[-1], "") if event[0] != "AN" else ""
            )
        })
    return data


# Scrapes all courses' ids dictionary
def courses_dictionary(response):
    return {
        # Store courses ids in {Blackboard id: MyUDC id} pairs
        course.get("bbid")[1:-2]: course.get("courseid").split("_", 1)[0]
        # Loop through all courses in Blackboard in which the user is a student
        for course in __parse_xml(response).findall(".//course[@roleIdentifier='S']")
    }


# Scrapes student's list of all terms available in Blackboard
def terms_list(response):
    terms = {}
    # Loop through courses registered in Blackboard
    for course in __parse_xml(response).findall(".//course[@roleIdentifier='S']"):
        # Extract term's string from course id in "FALL2017" format
        term_string = course.get("courseid").rsplit("_", 1)[-1].split("-")[0]
        # Split term id to year and term semester
        year, semester = term_string[-4:], __terms[term_string[:3]]
        # Store term in terms in {"Fall 2017-2018": "201710"} pairs
        terms[f"{semester['name']} {year}-{int(year) + 1}"] = year + semester["code"]
    return terms


# Scrapes student's list of all courses categorized by term
def courses_list(response, url=lambda x: x):
    terms = {}
    # Loop through courses registered in Blackboard
    for course in __parse_xml(response).findall(".//course[@roleIdentifier='S']"):
        # Extract course key, crn and term string from course identifier
        course_key, crn, term_string = course.get("courseid").split("_")
        # Make sure that term id is of the following format "FALL2017"
        term_string = term_string.split("-")[0]
        # Split term id to year and semester
        year, semester = term_string[-4:], __terms[term_string[:3]]
        # Get term full name of the following format "Fall 2017-2018"
        term_name = f"{semester['name']} {year}-{int(year) + 1}"
        # If term hasn't been added yet
        if term_name not in terms:
            # Initialize it with an empty dictionary
            terms[term_name] = {}
        # Add course to the correspondent term
        terms[term_name][__clean(course.get("name"))] = {
            # Content links to Blackboard's documents and deadlines
            "Content": url(course_key + "/" + course.get("bbid")[1:-2]),
            # Details links to MyUDC's course details
            "Details": url(f"{course_key}/{crn}/{year + semester['code']}")
        }
    return terms


# Scrapes student's list of courses' ids by term
def courses_by_term(response, term_code):
    courses = {}
    # Get Blackboard term string in "FALL2017" format from term code
    term_string = re.compile("^" + __terms[term_code[4:]]["name"] + "[A-Z]*" + term_code[:4])
    # Loop through list of courses in parsed XML
    for course in __parse_xml(response).find("courses"):
        # Store course's MyUDC id, CRN and term name
        key, crn, full_term = course.get("courseid").split("_")
        # Only add courses in the requested term and in which the user is a student
        if term_string.match(full_term) and course.get("roleIdentifier") == "S":
            # Add course ids in {MyUDC id: Blackboard id} pairs
            courses[key] = {
                # Store course's Blackboard id
                "courseId": course.get("bbid")[1:-2],
                "crn": crn
            }
    return courses


# Scrapes student's specific course data
def course_data(response, course_key, course_id, data_type=None):
    # Store parsed course and returned object structure
    course = __parse_xml(response)
    data = {"deadlines": [], "documents": []}
    # If requested data type isn't "documents"
    if data_type != "documents":
        # Scrape deadlines and add them to data
        data["deadlines"] = [
            {   # Store deadline's title, due date & other information
                "title": deadline.get("name"),
                "dueDate": deadline.get("dueDate"),
                "time": deadline.get("createdDate"),
                "course": course_key, "courseId": course_id,
                "contentId": deadline.get("contentid")[1:-2]
            }   # Loop through all course items which have a due date
            for deadline in course.findall(".//*[@dueToday]")
        ]
        # If requested data type is "deadlines"
        if data_type == "deadlines":
            # Only return the deadlines
            return data["deadlines"]
    # If requested data type isn't "deadlines"
    if data_type != "deadlines":
        # Scrape documents and add them to data
        data["documents"] = [
            {  # Extract document xid and content id using Regex from its URL
                "id": "_".join(__document_ids.search(document.get("url")).groups()),
                # Store document's title, upload date & course key
                "course": course_key,
                "title": document.getparent().getparent().get("name"),
                "file": document.get("name"),
                "time": document.get("modifiedDate"),
            }   # Loop through all course documents (not more than 25)
            for document in (course.findall(".//attachment") or [])[:25]
        ]
        # If requested data type is "documents"
        if data_type == "documents":
            # Only return the documents
            return data["documents"]
    # Return everything if data type isn't specified or invalid
    return data


def course_grades(response, course_key):
    grades = []
    # If there are any grades
    if response:
        # Split response into scores and schema
        scores, schema = response
        # Loop through scores
        for score in scores:
            # If score is not graded, then skip it
            if score.get("status") != "Graded": continue
            # Get the column corresponding to the current score
            column = next(column for column in schema if column["id"] == score["columnId"])
            # Add grade dictionary to grades
            grades.append({
                # Grade's course key and title
                "course": course_key,
                "title": column["name"],
                # Grade and full mark rounded up
                "grade": ceil(float(score["score"])),
                "outOf": ceil(float(column["score"]["possible"])),
            })
    return grades
