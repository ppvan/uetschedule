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

# Security risk, i admit.
CLIENT_INFO = {
    "type": "service_account",
    "project_id": "autoschedule-377806",
    "private_key_id": "6cb2e5f42e653c3caa4a54702a947bc73b1ca509",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDQoF7EFnb+QOv4\nzEK1/U+EIMhmXvW+z8nuTNVKDFZhbBMzx1QpcRlTZPA0qsbXIBcDbLx6pgDGTq6X\nXnLm9L/Ocx7uTGkV5O/0EIBUGos0ndovKWdqXmZZuU5JVAmco2/OYy5YPpZ4OCXG\nxa5Oc9HlFxJbAYPgs7h77HuvpHJ5vNoP9+xA1gw2zm1dENgQx2JKHIRxv83D55zQ\nYbf8nZAtMvBmDhvB0vI+0CVQNpCSXCS81bGZw3XHgcM6IUgj+1AiSigiNdFVSdBT\nMM6SQVVed09LnktmYhgBR7mKm9U5mrzEYFf3KzuQUo2ZiJ5pHblJylgFcfnKHWAH\nkuiKWdgBAgMBAAECggEACDwWcvQ+OrMfrsT/DXb/ipV9Z93BUUKyk6yR+qqIXTsn\neicY1Zx4aHC5yiGr475yD+rRG+aWbckOL7FcPD5tzBewz9uunXRZQ/VmyGsQhwc9\n2V3MvOqMD9yTbU7Paq3Uz06YKoadLmP4PWN8rKfi8vWtuED2yKD1OR5E8QDh4Jei\nz9EYwtiYV1jDdvSLnnmxkNni811V41QVK0zDX0/N56v63emRfmdBT8Cd3idbCcga\njUMaDtgHnJLMiMf8bbNXsWMJTgsg0YRW67TA2wHk/uHlTtsOteEilxgeSkJewx0j\nUbTNeMqT6M6wlcEVrus3OgOcIzez3dT21w1gFHUWlQKBgQDxawLzNW0gBPBm2duO\nqpXVFkstitz1d2w/wM6fjQPkFKO+4fDlRuYy+tSEh036vVv56aw1aCBNR2oAYUs4\nDupTsVgTtLbRmztK9UdhYsuzjO3NqDWuB1eW2XuzAtOxgRMrGmgATnl28CI7uYks\nVH9SKhuUB1FeIPf2mG8uNNOz9wKBgQDdOk+Axhv7js94MfehNqtTiKypZPkWLx6j\nwTYchaI05aQA3SEF797JGSFDQFEt8Wg1KWubHJ8XdHk2Fz+eLflJM1PJfJOdbase\nV3CCgRDjHs+rpnw+T02b7w6QEeoHIGNOOzxykCxwr0w+HEERp2sUmgR4hM4i5k3g\nFJpTp1vlxwKBgGxbEoTkuuj/LoOLTs9W408z5WQ4inomMtDekh7spQ1u8hvPv1a5\nHsNM76vYKvjamvitl9yUssLcxcgL4z3y+9u6ooSdvNyRZuh69KHSPQmGvIls8UL+\nCqMrVCkBoNBv1ZGoFXvlvQDUQRk7akUaW9ceDSjArBWqiIEG5AgCL+77AoGAUNX8\ntPYuxWWyg53meR7rzXM0fBUsOyHulTGFXzipQ6Dho3splOzIQD0RfWxj/WCnjj1b\nV2tG6qAhplUqZtcvrsK1i/scSTsIeubCcr1MeWEJyxPjdDUwC5l3fcc992qrPqvA\nc7AgvPAg8NUMJbJCG14H4i3M0M3MiOOeXJDbsIMCgYEA6cnS2xY2wBuwZUuG5hQ+\nY5e+JSlSs46LvnQBbMyTqjbPkSolxWT+ft4Ii9BtM0ScWZ1IGXdNqljj7h8bFT1c\nzRtwBTHfBkx+DUM/i8yNBHipn+S1TonNO0LBADNyMJzbLs/2fUsCvcz7AP93t7Yr\nw1qqBUJV0VLXG5qrvRELBZE=\n-----END PRIVATE KEY-----\n",
    "client_email": "schedulebot@autoschedule-377806.iam.gserviceaccount.com",
    "client_id": "104157667300773377339",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/schedulebot%40autoschedule-377806.iam.gserviceaccount.com"
}


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

    def __init__(self):
        self.service = None

        self.authenticate()

    def authenticate(self):
        credentials = service_account.Credentials.from_service_account_info(
            CLIENT_INFO, scopes=SCOPES
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
        except HttpError as error:
            print("An error occurred: %s" % error)
