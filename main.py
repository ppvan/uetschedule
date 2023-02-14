from crawler import Course, ScheduleCourse, CourseCrawler

import time

# student_id = input("Enter student id: ")
# term_id = input("Enter term id: ")

student_id = "21020782"
term_id = "036"

t1 = time.perf_counter()

crawler = CourseCrawler()

courses = crawler.fetch_courses(student_id, term_id)

# print(ScheduleCourse.fetch_schedule(courses))

# print(courses)

for course in crawler.fetch_schedule(courses):
    print(course)

t2 = time.perf_counter()

print(t2 - t1)
