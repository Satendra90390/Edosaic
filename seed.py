"""Seed the Django database with demo data."""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms_django.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from accounts.models import User
from core.models import (
    Institution, Student, Faculty, Course, FacultyTeaching,
    StudentCourse, Result, Attendance, Fee, AuditLog,
)
from datetime import date, timedelta
import random

if Institution.objects.exists():
    print("Database already has data. Skipping seed.")
    sys.exit(0)

print("Seeding database...")

# Institution
inst = Institution.objects.create(
    name="Demo University", slug="demo-university",
    inst_type="University", phone="9000000000",
    email="info@demouniversity.edu", address="New Delhi, India",
)

# Admin
admin = User.objects.create_user(
    username="admin", password="admin123",
    role="admin", institution=inst, first_name="Admin User",
)

# Students
student_data = [
    ("Aarav Patel", 20, "Male", "9876543210"),
    ("Priya Sharma", 19, "Female", "9876543211"),
    ("Rohan Gupta", 21, "Male", "9876543212"),
    ("Ananya Singh", 20, "Female", "9876543213"),
    ("Vikram Desai", 22, "Male", "9876543214"),
]
students = []
for i, (name, age, sex, phone) in enumerate(student_data, 1):
    uname = f"student{i}"
    user = User.objects.create_user(username=uname, password="stud123", role="student", institution=inst)
    s = Student.objects.create(institution=inst, user=user, name=name, age=age, sex=sex, phone=phone)
    students.append(s)
print(f"  Created {len(students)} students")

# Faculty
faculty_data = [
    ("Dr. Suresh Kumar", "B.Tech", "9111111111", "Ph.D", "suresh@university.edu"),
    ("Prof. Meena Joshi", "B.Tech", "9111111112", "M.Tech", "meena@university.edu"),
    ("Dr. Rajesh Verma", "MBA", "9111111113", "Ph.D", "rajesh@university.edu"),
    ("Prof. Kavita Reddy", "Pharmacy", "9111111114", "M.Pharm", "kavita@university.edu"),
]
faculties = []
for i, (name, dept, phone, qual, email) in enumerate(faculty_data, 1):
    uname = f"faculty{i}"
    user = User.objects.create_user(username=uname, password="fac123", role="faculty", institution=inst)
    f = Faculty.objects.create(institution=inst, user=user, name=name, department=dept, phone=phone, qualification=qual, email=email)
    faculties.append(f)
print(f"  Created {len(faculties)} faculty")

# Courses
cs = Course.objects.create(name="Computer Science (CS)", department="B.Tech", institution=inst)
fin = Course.objects.create(name="Finance", department="MBA", institution=inst)
pharm = Course.objects.create(name="Pharmaceutics", department="Pharmacy", institution=inst)
courses = [cs, fin, pharm]

# Teaching assignments
teachings = [
    (faculties[0], cs, "Data Structures", "2nd Year", "3rd Semester"),
    (faculties[0], cs, "Algorithms", "2nd Year", "4th Semester"),
    (faculties[1], cs, "Database Systems", "3rd Year", "5th Semester"),
    (faculties[2], fin, "Financial Management", "1st Year", "1st Semester"),
    (faculties[3], pharm, "Pharmaceutical Technology", "2nd Year", "3rd Semester"),
]
for fac, course, subj, year, sem in teachings:
    FacultyTeaching.objects.create(
        institution=inst, faculty=fac, course=course,
        subject=subj, year=year, semester=sem, designation="Professor",
    )
print(f"  Created {len(teachings)} teaching assignments")

# Student-Course assignments
for s in students[:3]:
    StudentCourse.objects.create(institution=inst, student=s, course=cs, faculty=faculties[0])

# Results
grades = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "D", None]
results_data = [
    (students[0], faculties[0], cs, "A"),
    (students[0], faculties[1], fin, "B+"),
    (students[1], faculties[0], cs, "A+"),
    (students[1], faculties[2], fin, "A-"),
    (students[2], faculties[0], cs, "B"),
    (students[2], faculties[2], pharm, "B-"),
    (students[3], faculties[0], cs, "C+"),
    (students[3], faculties[1], fin, "A"),
    (students[4], faculties[2], cs, None),
    (students[4], faculties[0], pharm, "D"),
]
for s, f, c, g in results_data:
    Result.objects.create(institution=inst, student=s, faculty=f, course=c, grade=g)
print(f"  Created {len(results_data)} results")

# Attendance
today = date.today()
attendance = []
for day_offset in range(5):
    d = today - timedelta(days=day_offset)
    for s in students:
        status = random.choice(["Present", "Present", "Present", "Absent"])
        attendance.append(Attendance(institution=inst, student=s, date=d, status=status))
Attendance.objects.bulk_create(attendance)
print(f"  Created {len(attendance)} attendance records")

# Fees
fees_data = [
    (students[0], 50000, today + timedelta(days=30), "Paid", "Tuition", "Semester 3 tuition fees"),
    (students[1], 50000, today + timedelta(days=30), "Pending", "Tuition", "Semester 3 tuition fees"),
    (students[2], 5000, today + timedelta(days=15), "Paid", "Exam", "Exam fees"),
    (students[3], 50000, today + timedelta(days=30), "Partial", "Tuition", "Partial payment"),
    (students[4], 10000, today + timedelta(days=45), "Pending", "Hostel", "Hostel accommodation"),
]
for s, amt, due, status, ftype, desc in fees_data:
    Fee.objects.create(institution=inst, student=s, amount=amt, due_date=due, status=status, fee_type=ftype, description=desc)
print(f"  Created {len(fees_data)} fee records")

print("\nSeed complete!")
print("Login credentials:")
print("  admin    / admin123  (Admin)")
print("  student1 / stud123   (Student)")
print("  faculty1 / fac123    (Faculty)")
