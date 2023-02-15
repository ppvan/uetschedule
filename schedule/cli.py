import click
import re
from . import schedule
from .schedule import SchedulerService


def validate_student_id(ctx, param, value):
    """Callback function that validates student ID."""
    if not re.match(r"^\d{8}$", value):
        raise click.BadParameter("Invalid student ID. Must have 8-digits (e.g 21020782).")
    return value


def validate_email(ctx, param, value):
    """Callback function that validates an email address."""
    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        raise click.BadParameter("Invalid email address.")
    return value


@click.command()
@click.option("--student-id", callback=validate_student_id, required=True, help="The id of student.")
@click.option("--user-mail", callback=validate_email, required=True, help="The google account to create event.")
@click.option("--calendar-name", default=schedule.DEFAULT_CALENDAR, help="The calendar name. Default `Schedule`.")
def main(student_id: str, user_mail: str, calendar_name: str):
    service = SchedulerService()
    service.schedule_courses(student_id, user_mail, calendar_name)


if __name__ == '__main__':
    main()
