#!/usr/bin/python3
from __future__ import annotations
from typing import List
import requests
from dataclasses import dataclass
from bs4 import BeautifulSoup


@dataclass
class Course:
    id: str
    name: str
    group: str


@dataclass
class ScheduleCourse:
    course: Course
    weekDay: str
    period: str
    theater: str


class CourseCrawler:

    def __init__(self) -> CourseCrawler:
        self.session = requests.Session()

    SCHEDULE_URL = "http://112.137.129.115/tkb/listbylist.php"
    COURSE_URL = "http://112.137.129.87/qldt"
    DEFAULT_PAYLOAD = {
        "SinhvienLmh[masvTitle]": "",
        "SinhvienLmh[hotenTitle]": "",
        "SinhvienLmh[ngaysinhTitle]": "",
        "SinhvienLmh[lopkhoahocTitle]": "",
        "SinhvienLmh[tenlopmonhocTitle]": "",
        "SinhvienLmh[tenmonhocTitle]": "",
        "SinhvienLmh[nhom]": "",
        "SinhvienLmh[sotinchiTitle]": "",
        "SinhvienLmh[ghichu]": "",
        "SinhvienLmh[term_id]": "",
        "SinhvienLmh_page": "1",
        "ajax": "sinhvien-lmh-grid",
        "pageSize": "5000"
    }

    def create_params(self, student_id: str, term_id: str):
        params = CourseCrawler.DEFAULT_PAYLOAD.copy()
        params["SinhvienLmh[masvTitle]"] = student_id
        params["SinhvienLmh[term_id]"] = term_id

        return params

    def auto_detect_term_id(self) -> str:
        """Auto detect term id code if not passed"""
        res = self.session.get(CourseCrawler.COURSE_URL)
        soup = BeautifulSoup(res.text, "lxml")

        term_ids = [tag["value"] for tag in soup.select("#SinhvienLmh_term_id>option")]
        # Pick the lastest term
        return max(term_ids)

    def fetch_courses(self, student_id: str, term_id: str = None) -> List[Course]:
        """Make API requests to get coursess of student"""

        if term_id is None:
            term_id = self.auto_detect_term_id()

        payload = self.create_params(student_id, term_id)
        res = self.session.get(CourseCrawler.COURSE_URL, params=payload)

        soup = BeautifulSoup(res.text, "lxml")
        table = soup.select_one("div#sinhvien-lmh-grid")

        courses = []
        for row in table.select("tbody>tr"):
            columns = list(map(lambda tag: str(tag.get_text()), row.findChildren(name="td")))
            _id, name, group = columns[5:8]  # interesting column

            courses.append(Course(_id, name, group))

        return courses

    def fetch_schedule(self, courses: List[Course]) -> List[ScheduleCourse]:

        res = self.session.get(CourseCrawler.SCHEDULE_URL)

        soup = BeautifulSoup(res.text, "lxml")
        table = soup.select_one("table:nth-child(4)")

        schedule_courses = []
        course_ids = {course.id: course for course in courses}
        for row in table.select("tr"):
            columns = list(map(lambda tag: tag.get_text(), row.findChildren(name="td")))

            # Not a valid column
            if len(columns) < 12:
                continue

            _id = columns[4]
            name = columns[2]
            group = columns[11]
            weekDay = columns[8]
            period = columns[9]
            theater = columns[10]

            if _id not in course_ids.keys():
                continue

            if group != "CL" and group != course_ids[_id].group:
                continue

            course = Course(_id, name, group)
            schedule_course = ScheduleCourse(course, weekDay, period, theater)

            schedule_courses.append(schedule_course)

        return schedule_courses


if __name__ == "__main__":
    crawler = CourseCrawler()
    print(crawler.fetch_courses("21020782"))
