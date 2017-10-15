from .values import __split_subject, __events, __assignment, __content, __announcement, __clean_event
from Requests import clean_course_name as __clean


# Scrapes personal emails details
def personal_emails(raw_emails):
    # Array to store emails
    emails = []
    # Loop through raw emails
    for email in raw_emails:
        # Match and store email event (if any), title and sender
        event, title = __split_subject.match(email["Subject"]).groups()
        sender = email["Sender"]["EmailAddress"]
        # Add extracted email details to emails
        emails.append({
            # Extract event and title using Regex matches
            "title": title,
            "event": __events[event[:2].lower()] if event else "New Email",
            # Get sender name and email
            "sender": sender["Name"],
            "from": sender["Address"],
            # Get email time and body directly
            "time": email["DateTimeSent"],
            "body": email["Body"]["Content"],
        })
    return emails


# Scrapes Blackboard generated courses emails
def courses_emails(raw_emails):
    # Array to store emails
    emails = []
    # Loop through raw emails
    for email in raw_emails:
        # Store email preview and subject
        preview = email["BodyPreview"]
        subject = email["Subject"]
        # Match content details and format email event
        # When email is about an assignment due
        if subject.startswith("Assignment:"):
            match = __assignment.match(subject)
            event = "Assignment Due " + match.group(3) + " " + match.group(4)
        # When email is about an assignment or content item being added
        elif preview.startswith("Content Item:") or preview.startswith("Assignment:"):
            match = __content.match(preview)
            event = "New {}".format(match.group(1).split()[0])
        else:  # When email is about an announcement
            match = __announcement.match(subject)
            event = "New Announcement"
        # Add extracted email data to emails
        emails.append({
            "event": event,
            # Extract title and course using Regex matches
            "title": match.group("title"),
            "course": __clean(match.group("course")),
            # Get email time and body directly
            "time": email["DateTimeSent"],
            "body": email["Body"]["Content"]
        })
    return emails


# Scrapes university events related emails
def events_emails(raw_emails):
    # Return an array of emails dictionaries
    return [
        {   # Extract and add event body, time and cleaned title
            "title": __clean_event.sub("", email["Subject"]),
            "time": email["DateTimeSent"],
            "body": email["Body"]["Content"]
        }   # Loop through raw emails
        for email in raw_emails
    ]
