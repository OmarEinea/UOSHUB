import requests


# General Blackboard API request with common attributes
def get(link, session, params=None):
    return requests.get(
        # Get data from root url + api url
        'https://elearning.sharjah.ac.ae/learn/api/public/v1/' + link,
        # Send login session
        cookies=session,
        # Send required data
        params=params
    ).json()


# Get student's basic info (name, major, collage)
def basic_info(session, sid):
    # Request data from API url while passing student id
    student = get('users/userName:' + sid, session, {'fields': 'name,job'})
    # Extract and return a dictionary of student info
    return {
        'name': student['name']['given'],
        'major': student['job']['department'],
        'collage': student['job']['company']
    }
