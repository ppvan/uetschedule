from typing import List
from .crawler import ScheduleCourse, CourseCrawler
from .calendars import Event, GoogleCalendarService

import webbrowser
import halo
from dateutil import rrule
from datetime import time, datetime, timedelta

SEMESTER_WEEKS = 16

DEFAULT_CALENDAR = "Schedule"

LESSON_TIME = {
    "1": time(7, 0, 0),
    "2": time(8, 0, 0),
    "3": time(9, 0, 0),
    "4": time(10, 0, 0),
    "5": time(11, 0, 0),
    "6": time(12, 0, 0),
    "7": time(13, 0, 0),
    "8": time(14, 0, 0),
    "9": time(15, 0, 0),
    "10": time(16, 0, 0),
    "11": time(17, 0, 0),
    "12": time(18, 0, 0),
    "13": time(18, 0, 0),
    "14": time(19, 0, 0),
    "15": time(20, 0, 0),
}


class SchedulerService:
    def __init__(self) -> None:
        self.crawler = CourseCrawler()
        self.calendar_service = GoogleCalendarService()

    def fetch_schedule_from_server(self, student_id: str, term_id: str = None):
        student_courses = self.crawler.fetch_courses(student_id, term_id)
        scheduled_courses = self.crawler.fetch_schedule(student_courses)

        return scheduled_courses

    def schedule_courses(self, student_id: str, user_mail: str, calendar_name: str = DEFAULT_CALENDAR):
        """
        Schedule student courses in google calenlar and share it to user_mail.
        This also open browser to that URL
        student_id: The UET student id. E.g 21020782
        user_mail: An normal gmail abc@gmail.com.
        They are stored in info dictionary. e.g info["student_id"]
        """

        spinner = halo.Halo(text="Fetch schedule from school API", spinner="dots")
        spinner.start()
        scheduled_courses = self.fetch_schedule_from_server(student_id)
        spinner.stop_and_persist("✔", f"Got {len(scheduled_courses)} courses.")

        spinner.text = "Create the calendar."
        spinner.start()
        calendar = self.calendar_service.create_calendar(calendar_name)
        self.calendar_service.share_calendar_with_user(calendar.id, user_mail)
        all_events = []
        for course in scheduled_courses:
            course_events = self.create_course_events(course)
            all_events.extend(course_events)
        spinner.stop_and_persist("✔", f"Succeeded. {calendar_name} is created.")

        spinner.text = "Create events on Google Calendar. This may take a few minutes."
        spinner.start()
        for event in all_events:
            self.calendar_service.create_event(event, calendar)

        spinner.stop_and_persist("✔", "Done, opening the browser.")
        invite_link = f"https://calendar.google.com/calendar/u/0?cid={calendar.id}&invite={user_mail}"
        # Open invite link in user browser
        webbrowser.open(invite_link)

    def convert_period_to_time(self, period: str):
        """
        The period is in the format number-number. E.g 1-2, where number is from 1 to 14
        Convert in to actual lesson time (7:00, 9:00)
        """
        start, end = period.split("-")

        return LESSON_TIME[start], LESSON_TIME[str(int(end) + 1)]

    def create_course_events(self, course: ScheduleCourse, repeat=SEMESTER_WEEKS) -> List[Event]:
        start, end = self.convert_period_to_time(course.period)

        week_rule = rrule.weekday(int(course.weekDay) - 2)
        start_rule = rrule.rrule(
            rrule.WEEKLY,
            dtstart=datetime.now() - timedelta(weeks=1),
            byweekday=week_rule,
            count=repeat,
            byhour=start.hour,
            byminute=start.minute,
            bysecond=start.second
        )
        end_rule = rrule.rrule(
            rrule.WEEKLY,
            dtstart=datetime.now() - timedelta(weeks=1),
            byweekday=week_rule,
            count=repeat,
            byhour=end.hour,
            byminute=end.minute,
            bysecond=end.second
        )

        events = []
        for start_time, end_time in zip(start_rule, end_rule):
            title = f"{course.course.name} {course.course.group} - {course.theater}"
            event = Event(title, start_time, end_time)
            events.append(event)

        return events


if __name__ == "__main__":
    student_id = "21020782"
    term_id = "036"

    scheduler = SchedulerService()

    scheduler.schedule_courses(student_id, term_id)
