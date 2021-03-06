from lxml.html import fromstring as __parse
from . import seasons_codes
import requests, re


# Gets this year's Academic Calendar page
def academic_calendar():
    # HTTP get request from UOS homepage
    return requests.get("http://www.sharjah.ac.ae/en/academics/A-Calendar/Pages/accal18-19.aspx").text


# Scrapes all terms in academic calendar
def all_terms(response):
    # Initialize terms dictionary
    terms = {}
    # Loop through terms in academic calendar
    for term in __parse(response).findall(".//div[@class='pageTurn']/div/div"):
        # Split(" ") term & store it's season and year
        season, _, year = term.find("label").text.split()
        # Add term to terms dictionary as a {term name: term code} pair
        terms[season + " " + year.replace("/", "-")] = year[:4] + seasons_codes[season]
    return terms


# Scrapes specified term's calendar events
def term_events(response, term_code):
    # Initialize events and store year
    year, events = term_code[:4], []
    # Define a function to clean cell from whitespaces
    clean = lambda cell: re.sub(" +", " ", cell.strip())
    # Format term name in "Fall Semester 2017/2017" format from term code
    term_name = f"{seasons_codes[term_code[4:]]} {year}/{int(year) + 1}"
    # Loop through available terms calendars
    for term in __parse(response).findall(".//div[@class='pageTurn']/div/div"):
        # If calendar's label matches requested term name
        if term.find("label").text == term_name:
            # Loop through it's events (table rows)
            for event in term.findall(".//tbody/tr")[2:]:
                # Store event row's cells
                cells = event.findall("td")
                # Add event's date and text to events array
                events.append({
                    "date": clean(re.sub("(Till|-|–)", " - ", cells[1].text_content())).split(',')[0],
                    "text": clean(cells[3].text_content())
                })
            return events
