from .general import root_url
from datetime import datetime
import re

# These are the possible values of Blackboard variables

__types = {
    "GB": "Item",
    "AS": "Assignment",
    "TE": "Assignment",
    "CR": "Course",
    "SU": "Survey",
    "CO": "Content",
    "AN": "Announcement",
}

__events = {
    "AVAIL": "Available",
    "OVERDUE": "Overdue",
    "DUE": "Due",
}

__terms = {
    "10": {
        "name": "FALL",
        "range": [12, 8]
    },
    "30": {
        "name": "SUM",
        "range": [7, 6]
    },
    "20": {
        "name": "SPR",
        "range": [5, 1]
    },
    "FAL": {
        "name": "Fall",
        "code": "10"
    },
    "SPR": {
        "name": "Spring",
        "code": "20"
    },
    "SUM": {
        "name": "Summer",
        "code": "30"
    },
}

__timestamp = datetime.fromtimestamp

# Blackboard stream URLs
__stream_root_url = root_url + "webapps/streamViewer/"
__stream_url = __stream_root_url + "streamViewer"
__dismiss_update_url = __stream_root_url + "dwr_open/call/plaincall/NautilusViewService.removeRecipient.dwr"

# Blackboard assignment submission URLs
__submit_files_url = root_url + "webapps/assignment/uploadAssignment?action=submit"
__new_submission_url = __submit_files_url[:-6] + "newAttempt&course_id={}&content_id={}"
# Regex to get assignment's nonce ids from Blackboard's new assignment's page
__get_nonce = re.compile("value='([\w-]{36})'.*\n.*id=\"ajaxNonceId\".*value=\"([\w-]{36})\"")

# Blackboard document xid and content id from URL
__document_ids = re.compile("xid-([0-9]+)_1&content_id=_([0-9]+)_1&")
