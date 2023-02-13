#!/usr/bin/python3

from __future__ import annotations
from bs4 import BeautifulSoup
import requests


class Course:
    """
    Represent a course in school system.
    Ex. ('INT2208 2', 'Công nghệ phần mềm', 'CL')
    """

    API_URL = "http://112.137.129.87/qldt"
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

    @staticmethod
    def fetch_courses(student_id: str, term_id: str) -> list[Course]:
        """Make API requests to get coursess of student"""

        payload = Course.create_params(student_id, term_id)
        res = requests.get(Course.API_URL, params=payload)

        soup = BeautifulSoup(res.text, "lxml")
        table = soup.select_one("div#sinhvien-lmh-grid")

        courses = []
        for row in table.select("tbody>tr"):
            columns = list(map(lambda tag: tag.get_text(), row.findChildren(name="td")))
            _id, name, group = columns[5:8]  # interesting column

            courses.append(Course(_id, name, group))

        return courses

    @staticmethod
    def create_params(student_id: str, term_id: str):
        params = Course.DEFAULT_PAYLOAD.copy()
        params["SinhvienLmh[masvTitle]"] = student_id
        params["SinhvienLmh[term_id]"] = term_id

        return params

    def __init__(self, _id: str, name: str, group: str) -> None:
        self.id = _id
        self.name = name
        self.group = group

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.id}, {self.name}, {self.group}"

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Course):
            return self.id == __o.id

    def __hash__(self) -> int:
        return hash(self.id)


class ScheduleCourse:

    API_URL = "http://112.137.129.115/tkb/listbylist.php"

    def __init__(self, course: Course, weekDay, period, lecture_theater) -> ScheduleCourse:
        self.course = course
        self.weekDay = weekDay
        self.period = period
        self.theater = lecture_theater

    @staticmethod
    def fetch_schedule(courses: list[Course]) -> list[ScheduleCourse]:
        pass
