from __future__ import print_function, annotations
from typing import List

from dataclasses import dataclass
from datetime import datetime
from dateutil import tz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

KEY_FILE_PATH = "secret/autoschedule.json"


@dataclass
class Calendar:
    id: str
    name: str


@dataclass
class Event:
    title: str
    start_time: datetime
    end_time: datetime


class GoogleCalendarService:

    def __init__(self, key_file_path=KEY_FILE_PATH):
        self.key_file_path = key_file_path
        self.service = None

        self.authenticate()

    def authenticate(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.key_file_path, scopes=SCOPES
        )

        self.service = build("calendar", "v3", credentials=credentials)

    def get_calendars(self) -> List[Calendar]:
        try:
            calendar_list = self.service.calendarList().list().execute()

            calendars = []
            for calendar_data in calendar_list["items"]:
                calendar = Calendar(calendar_data["id"], calendar_data["summary"])
                calendars.append(calendar)

            return calendars
        except HttpError as error:
            print("An error occurred: %s" % error)

        return []

    def share_calendar_with_user(self, calendar_id: str, user_email: str):
        rule = {
            "scope": {
                "type": "user",
                "value": user_email
            },
            "role": "writer"
        }
        self.service.acl().insert(calendarId=calendar_id, body=rule).execute()

    def create_calendar(self, summary: str) -> Calendar:
        body = {
            "summary": summary
        }

        google_created_calendar = self.service.calendars().insert(body=body).execute()
        calendar = Calendar(google_created_calendar["id"], google_created_calendar["summary"])

        return calendar

    def delete_calendar(self, calendar_id: str):
        try:
            self.service.calendars().delete(calendarId=calendar_id).execute()
            print("Calendar with ID {} has been deleted".format(calendar_id))
        except HttpError as error:
            print('An error occurred: %s' % error)

    def create_event(self, event: Event, calendar: Calendar = None):
        start_time = event.start_time.replace(tzinfo=tz.tzlocal())
        end_time = event.end_time.replace(tzinfo=tz.tzlocal())

        event_body = {
            "summary": event.title,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": start_time.tzname(),
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": end_time.tzname(),
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 30},
                ],
            },
        }

        # Call API to create events on google calendar
        try:
            calendar_id = calendar.id if calendar is not None else "primary"
            self.service.events().insert(calendarId=calendar_id, body=event_body).execute()

            print(f"Event {event.title} created in {calendar_id}.")
        except HttpError as error:
            print("An error occurred: %s" % error)
