import crawler

student_id = input("Enter student id: ")
term_id = input("Enter term id: ")

courses = crawler.fetch_courses(student_id, term_id)


print(courses)
