import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms_django.settings')
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS = ['*']
settings.SECURE_SSL_REDIRECT = False
settings.DEBUG = True

from django.test import Client
from core.models import *
from accounts.models import User
from datetime import date, timedelta

print("=" * 70)
print("EDOSAIC SMS - COMPREHENSIVE INTEGRATION TEST")
print("=" * 70)

# CLEANUP any leftovers from prior failed runs
Institution.objects.filter(slug='test-coll').delete()
for uname in ['test_chairman_int','tnewstu','tnewfac','thodfac','tfacstu','tdebugstu3','tnewhod','tnewdir','tnewlib','tnewacc','tdir','thod','tfac','tstu','tlib','tacc']:
    User.objects.filter(username=uname).delete()
print("Pre-test cleanup done.")

# SETUP
inst, _ = Institution.objects.get_or_create(slug='test-coll', defaults={'name':'Test College','inst_type':'College','phone':'9999999999','invite_code':'TESTCOLL'})
chairman_user, _ = User.objects.get_or_create(username='test_chairman_int', defaults={'institution':inst,'role':'chairman','first_name':'Chairman','phone':'1111111111','is_active':True})
chairman_user.set_password('test123'); chairman_user.save()
Chairman.objects.get_or_create(user=chairman_user, defaults={'institution':inst,'name':'Chairman','phone':'1111111111'})

course1, _ = Course.objects.get_or_create(name='B.Tech CS', code='CS', institution=inst)
course2, _ = Course.objects.get_or_create(name='B.Tech ME', code='ME', institution=inst)
branch1, _ = Branch.objects.get_or_create(name='CSE-A', course=course1, institution=inst, defaults={'code':'CSEA'})
subject1, _ = Subject.objects.get_or_create(name='Data Structures', code='CS201', course=course1, branch=branch1, institution=inst, defaults={'subject_type':'Theory','year':'2','semester':'3','credits':4})

tu = {}
for role, uname in [('director','tdir'),('hod','thod'),('faculty','tfac'),('student','tstu'),('librarian','tlib'),('accountant','tacc')]:
    u, _ = User.objects.get_or_create(username=uname, defaults={'institution':inst,'role':role,'first_name':role.title(),'phone':'2222222222','is_active':True})
    u.set_password('test123'); u.save(); tu[role] = u

d_obj, _ = Director.objects.get_or_create(user=tu['director'], defaults={'institution':inst,'name':'Dir','department':'CS','phone':'2222222222'})
d_obj.courses.add(course1, course2)
h_obj, _ = HOD.objects.get_or_create(user=tu['hod'], defaults={'institution':inst,'name':'HOD','department':'CS','phone':'2222222222'})
h_obj.courses.add(course1)
f_obj, _ = Faculty.objects.get_or_create(user=tu['faculty'], defaults={'institution':inst,'name':'Fac','department':'CS','phone':'3333333333','qualification':'PhD'})
f_obj.courses.add(course1)
s_obj, _ = Student.objects.get_or_create(user=tu['student'], defaults={'institution':inst,'name':'Stu','age':20,'sex':'Male','phone':'4444444444','course':course1,'year':'2','semester':'3'})

exam, _ = Exam.objects.get_or_create(title='Midterm', course=course1, institution=inst, defaults={'exam_type':'Midterm','subject':'DS','exam_date':date.today(),'total_marks':100,'passing_marks':40})
event, _ = Event.objects.get_or_create(title='Annual Day', institution=inst, defaults={'description':'Test','event_type':'Academic','start_date':date.today(),'end_date':date.today()+timedelta(days=1),'venue':'Hall'})
book, _ = Book.objects.get_or_create(title='Algorithms', author='CLRS', institution=inst, defaults={'isbn':'978','category':'CS','total_copies':5,'available_copies':5})

p = 0; f2 = 0; errs = []

def t(name, method, url, user=None, data=None, want_code=None, want_redirect=None, want_cont=None):
    global p, f2, errs
    c = Client()
    if user:
        c.login(username=user.username, password='test123')
    try:
        if method == 'GET':
            resp = c.get(url)
        else:
            resp = c.post(url, data or {})
        status = resp.status_code
        loc = resp.get('Location', '')
        body = resp.content.decode('utf-8', 'replace')

        if want_redirect:
            if want_redirect in loc:
                p += 1; print(f"  OK {name}")
            else:
                f2 += 1; m = f"FAIL {name}: want redirect '{want_redirect}', got '{loc}' (status={status})"
                errs.append(m); print(f"  {m}")
        elif want_code:
            if status == want_code:
                p += 1; print(f"  OK {name}")
            else:
                f2 += 1; m = f"FAIL {name}: want {want_code}, got {status}"
                errs.append(m); print(f"  {m}")
        elif want_cont:
            if want_cont in body:
                p += 1; print(f"  OK {name}")
            else:
                f2 += 1; m = f"FAIL {name}: '{want_cont}' not in response (status={status})"
                errs.append(m); print(f"  {m}")
        else:
            if status in (200, 302):
                p += 1; print(f"  OK {name}")
            else:
                f2 += 1; m = f"FAIL {name}: status {status}"
                errs.append(m); print(f"  {m}")
    except Exception as e:
        f2 += 1; m = f"FAIL {name}: {type(e).__name__}: {str(e)[:150]}"
        errs.append(m); print(f"  {m}")

print("\n--- DASHBOARD ROUTER ---")
for role, u in tu.items():
    dp = {'director':'/dashboard/director/','hod':'/dashboard/hod/','faculty':'/dashboard/faculty/','student':'/dashboard/student/','librarian':'/dashboard/librarian/','accountant':'/dashboard/accountant/'}.get(role)
    if dp: t(f"Router:{role}", 'GET', '/dashboard/', user=u, want_redirect=dp)
t("Router:chairman", 'GET', '/dashboard/', user=chairman_user, want_redirect='/dashboard/admin/')
t("Router:anon", 'GET', '/dashboard/', want_redirect='/login/')

print("\n--- CHAIRMAN VIEWS ---")
t("Chairman dashboard", 'GET', '/dashboard/admin/', user=chairman_user, want_code=200)
t("Chairman dashboard guard", 'GET', '/dashboard/admin/', user=tu['faculty'], want_redirect='/dashboard/')
t("Chairman students", 'GET', '/dashboard/admin/students/', user=chairman_user, want_code=200)
t("Chairman students search", 'GET', '/dashboard/admin/students/?q=Stu', user=chairman_user, want_code=200)
t("Chairman add student form", 'GET', '/dashboard/admin/students/add/', user=chairman_user, want_code=200)
t("Chairman add student POST", 'POST', '/dashboard/admin/students/add/', user=chairman_user, data={'name':'NewStu','age':21,'sex':'Male','phone':'5555555555','course':course1.id,'year':'2','semester':'3','username':'tnewstu','password':'test123'}, want_redirect='/dashboard/admin/students/')
assert User.objects.filter(username='tnewstu').exists(), "Student user not created"
assert Student.objects.filter(user__username='tnewstu').exists(), "Student profile not created"

t("Chairman faculty", 'GET', '/dashboard/admin/faculty/', user=chairman_user, want_code=200)
t("Chairman add faculty POST", 'POST', '/dashboard/admin/faculty/add/', user=chairman_user, data={'name':'NewFac','department':'CS','phone':'6666666666','qualification':'MSc','email':'f@t.com','username':'tnewfac','password':'test123'}, want_redirect='/dashboard/admin/faculty/')
assert Faculty.objects.filter(user__username='tnewfac').exists()

t("Chairman courses", 'GET', '/dashboard/admin/courses/', user=chairman_user, want_code=200)
t("Chairman add course POST", 'POST', '/dashboard/admin/courses/add/', user=chairman_user, data={'name':'B.Sc Phy','code':'PHY','department':'Sci','description':'Physics'}, want_redirect='/dashboard/admin/courses/')
assert Course.objects.filter(name='B.Sc Phy', institution=inst).exists()

t("Chairman branches", 'GET', f'/dashboard/admin/courses/{course1.id}/branches/', user=chairman_user, want_code=200)
t("Chairman add branch POST", 'POST', f'/dashboard/admin/courses/{course1.id}/branches/add/', user=chairman_user, data={'name':'CSE-B','code':'CSEB'}, want_redirect=f'/dashboard/admin/courses/{course1.id}/branches/')
assert Branch.objects.filter(name='CSE-B',course=course1).exists()

t("Chairman subjects manage", 'GET', f'/dashboard/admin/courses/{course1.id}/subjects/', user=chairman_user, want_code=200)
t("Chairman add subject POST", 'POST', f'/dashboard/admin/courses/{course1.id}/subjects/add/', user=chairman_user, data={'name':'OS','code':'CS301','subject_type':'Theory','year':'3','semester':'5','credits':4}, want_redirect=f'/dashboard/admin/courses/{course1.id}/subjects/')
assert Subject.objects.filter(name='OS',institution=inst).exists()

t("Chairman exams", 'GET', '/dashboard/admin/exams/', user=chairman_user, want_code=200)
t("Chairman add exam POST", 'POST', '/dashboard/admin/exams/add/', user=chairman_user, data={'title':'Final26','course':course1.id,'exam_type':'Final','subject':'DS','exam_date':'2026-05-01','total_marks':100,'passing_marks':40}, want_redirect='/dashboard/admin/exams/')
assert Exam.objects.filter(title='Final26',institution=inst).exists()

t("Chairman exam results", 'GET', f'/dashboard/admin/exams/{exam.id}/results/', user=chairman_user, want_code=200)
t("Chairman events", 'GET', '/dashboard/admin/events/', user=chairman_user, want_code=200)
t("Chairman add event POST", 'POST', '/dashboard/admin/events/add/', user=chairman_user, data={'title':'TechFest','description':'TF','event_type':'Cultural','start_date':'2026-06-01','end_date':'2026-06-03','venue':'Aud'}, want_redirect='/dashboard/admin/events/')
assert Event.objects.filter(title='TechFest',institution=inst).exists()

t("Chairman books", 'GET', '/dashboard/admin/books/', user=chairman_user, want_code=200)
t("Chairman fees", 'GET', '/dashboard/admin/fees/', user=chairman_user, want_code=200)
t("Chairman analytics", 'GET', '/dashboard/admin/analytics/', user=chairman_user, want_code=200)
t("Chairman reports", 'GET', '/dashboard/admin/reports/', user=chairman_user, want_code=200)
t("Chairman settings", 'GET', '/dashboard/admin/settings/', user=chairman_user, want_code=200)
t("Chairman subjects page", 'GET', '/dashboard/admin/subjects/', user=chairman_user, want_code=200)

# DELETE operations
t("Chairman delete student", 'POST', '/dashboard/admin/students/', user=chairman_user, data={'delete_id': Student.objects.get(user__username='tnewstu').pk}, want_redirect='/dashboard/admin/students/')
assert not Student.objects.filter(user__username='tnewstu').exists()

print("\n--- CHAIRMAN: DIRECTORS & ACCOUNTANTS ---")
t("Chairman directors", 'GET', '/dashboard/chairman/directors/', user=chairman_user, want_code=200)
t("Chairman add director POST", 'POST', '/dashboard/chairman/directors/add/', user=chairman_user, data={'name':'NewDir','department':'CS','phone':'7777777777','qualification':'PhD','email':'d@t.com','username':'tnewdir','password':'test123','courses':course1.id}, want_redirect='/dashboard/chairman/directors/')
assert Director.objects.filter(user__username='tnewdir').exists()
nd = Director.objects.get(user__username='tnewdir')
assert nd.courses.filter(pk=course1.id).exists()

t("Chairman delete director", 'POST', '/dashboard/chairman/directors/', user=chairman_user, data={'delete_id':nd.pk}, want_redirect='/dashboard/chairman/directors/')
assert not Director.objects.filter(user__username='tnewdir').exists()
assert not User.objects.filter(username='tnewdir').exists()

t("Chairman accountants", 'GET', '/dashboard/chairman/accountants/', user=chairman_user, want_code=200)
t("Chairman add accountant POST", 'POST', '/dashboard/chairman/accountants/add/', user=chairman_user, data={'name':'NewAcc','phone':'8888888888','username':'tnewacc','password':'test123'}, want_redirect='/dashboard/chairman/accountants/')
assert User.objects.filter(username='tnewacc',role='accountant').exists()
na = User.objects.get(username='tnewacc')
t("Chairman delete accountant", 'POST', '/dashboard/chairman/accountants/', user=chairman_user, data={'delete_id':na.pk}, want_redirect='/dashboard/chairman/accountants/')
assert not User.objects.filter(username='tnewacc').exists()

print("\n--- DIRECTOR VIEWS ---")
t("Director dashboard", 'GET', '/dashboard/director/', user=tu['director'], want_code=200)
t("Director dashboard guard", 'GET', '/dashboard/director/', user=tu['faculty'], want_redirect='/dashboard/')
t("Director hods", 'GET', '/dashboard/director/hods/', user=tu['director'], want_code=200)
t("Director add HOD POST", 'POST', '/dashboard/director/hods/add/', user=tu['director'], data={'name':'NewHOD','department':'CS','phone':'9999999999','qualification':'PhD','email':'h@t.com','username':'tnewhod','password':'test123','courses':course1.id}, want_redirect='/dashboard/director/hods/')
assert HOD.objects.filter(user__username='tnewhod').exists()
nh = HOD.objects.get(user__username='tnewhod')
t("Director delete HOD", 'POST', '/dashboard/director/hods/', user=tu['director'], data={'delete_id':nh.pk}, want_redirect='/dashboard/director/hods/')
assert not HOD.objects.filter(user__username='tnewhod').exists()

print("\n--- HOD VIEWS ---")
t("HOD dashboard", 'GET', '/dashboard/hod/', user=tu['hod'], want_code=200)
t("HOD dashboard guard", 'GET', '/dashboard/hod/', user=tu['faculty'], want_redirect='/dashboard/')
t("HOD faculty", 'GET', '/dashboard/hod/faculty/', user=tu['hod'], want_code=200)
t("HOD add faculty POST", 'POST', '/dashboard/hod/faculty/add/', user=tu['hod'], data={'name':'HodFac','phone':'1010101010','qualification':'MSc','email':'hf@t.com','username':'thodfac','password':'test123','courses':course1.id}, want_redirect='/dashboard/hod/faculty/')
assert Faculty.objects.filter(user__username='thodfac').exists()
nf = Faculty.objects.get(user__username='thodfac')
t("HOD delete faculty", 'POST', '/dashboard/hod/faculty/', user=tu['hod'], data={'delete_id':nf.pk}, want_redirect='/dashboard/hod/faculty/')
assert not Faculty.objects.filter(user__username='thodfac').exists()

t("HOD librarians", 'GET', '/dashboard/hod/librarians/', user=tu['hod'], want_code=200)
t("HOD add librarian POST", 'POST', '/dashboard/hod/librarians/add/', user=tu['hod'], data={'name':'NewLib','phone':'1212121212','username':'tnewlib','password':'test123'}, want_redirect='/dashboard/hod/librarians/')
assert User.objects.filter(username='tnewlib',role='librarian').exists()
nl = User.objects.get(username='tnewlib')
t("HOD delete librarian", 'POST', '/dashboard/hod/librarians/', user=tu['hod'], data={'delete_id':nl.pk}, want_redirect='/dashboard/hod/librarians/')
assert not User.objects.filter(username='tnewlib').exists()

print("\n--- FACULTY VIEWS ---")
t("Faculty dashboard", 'GET', '/dashboard/faculty/', user=tu['faculty'], want_code=200)
t("Faculty dashboard guard", 'GET', '/dashboard/faculty/', user=tu['student'], want_redirect='/dashboard/')
t("Faculty students", 'GET', '/dashboard/faculty/students/', user=tu['faculty'], want_code=200)
t("Faculty add student POST", 'POST', '/dashboard/faculty/students/add/', user=tu['faculty'], data={'name':'FacStu','age':'19','sex':'Female','phone':'1313131313','course':course1.id,'year':'1','semester':'1','username':'tfacstu','password':'test123'}, want_redirect='/dashboard/faculty/students/')
assert Student.objects.filter(user__username='tfacstu').exists()
ns = Student.objects.get(user__username='tfacstu')
t("Faculty delete student", 'POST', '/dashboard/faculty/students/', user=tu['faculty'], data={'delete_id':ns.pk}, want_redirect='/dashboard/faculty/students/')
assert not Student.objects.filter(user__username='tfacstu').exists()

t("Faculty exams", 'GET', '/dashboard/faculty/exams/', user=tu['faculty'], want_code=200)
t("Faculty events", 'GET', '/dashboard/faculty/events/', user=tu['faculty'], want_code=200)

print("\n--- STUDENT VIEWS ---")
t("Student dashboard", 'GET', '/dashboard/student/', user=tu['student'], want_code=200)
t("Student dashboard guard", 'GET', '/dashboard/student/', user=tu['faculty'], want_redirect='/dashboard/')
t("Student exams", 'GET', '/dashboard/student/exams/', user=tu['student'], want_code=200)
t("Student library", 'GET', '/dashboard/student/library/', user=tu['student'], want_code=200)
t("Student events", 'GET', '/dashboard/student/events/', user=tu['student'], want_code=200)

print("\n--- ACCOUNTANT VIEWS ---")
t("Accountant dashboard", 'GET', '/dashboard/accountant/', user=tu['accountant'], want_code=200)
t("Accountant dashboard guard", 'GET', '/dashboard/accountant/', user=tu['student'], want_redirect='/dashboard/')
t("Accountant fees", 'GET', '/dashboard/accountant/fees/', user=tu['accountant'], want_code=200)
t("Accountant add fee POST", 'POST', '/dashboard/accountant/fees/add/', user=tu['accountant'], data={'student':s_obj.id,'amount':25000,'due_date':'2026-08-01','fee_type':'Hostel','status':'Pending','description':'Hostel'}, want_redirect='/dashboard/accountant/fees/')
nf2 = Fee.objects.filter(student=s_obj,fee_type='Hostel').order_by('-created_at').first()
assert nf2 is not None
t("Accountant edit fee POST", 'POST', f'/dashboard/accountant/fees/{nf2.pk}/edit/', user=tu['accountant'], data={'student':s_obj.id,'amount':30000,'due_date':'2026-08-01','fee_type':'Hostel','status':'Paid','description':'Updated'}, want_redirect='/dashboard/accountant/fees/')
nf2.refresh_from_db()
assert nf2.amount == 30000 and nf2.status == 'Paid'
t("Accountant collections", 'GET', '/dashboard/accountant/collections/', user=tu['accountant'], want_code=200)
t("Accountant delete fee", 'POST', '/dashboard/accountant/fees/', user=tu['accountant'], data={'delete_id':nf2.pk}, want_redirect='/dashboard/accountant/fees/')
assert not Fee.objects.filter(pk=nf2.pk).exists()

print("\n--- LIBRARIAN VIEWS ---")
t("Librarian dashboard", 'GET', '/dashboard/librarian/', user=tu['librarian'], want_code=200)
t("Librarian dashboard guard", 'GET', '/dashboard/librarian/', user=tu['student'], want_redirect='/dashboard/')
t("Librarian books", 'GET', '/dashboard/librarian/books/', user=tu['librarian'], want_code=200)
t("Librarian add book POST", 'POST', '/dashboard/librarian/books/add/', user=tu['librarian'], data={'title':'Clean Code','author':'Martin','isbn':'111','category':'CS','total_copies':3}, want_redirect='/dashboard/librarian/books/')
assert Book.objects.filter(title='Clean Code',institution=inst).exists()
nb = Book.objects.get(title='Clean Code',institution=inst)
t("Librarian edit book POST", 'POST', f'/dashboard/librarian/books/{nb.pk}/edit/', user=tu['librarian'], data={'title':'Clean Code 2e','author':'Martin','isbn':'111','category':'CS','total_copies':5}, want_redirect='/dashboard/librarian/books/')
nb.refresh_from_db()
assert nb.title == 'Clean Code 2e' and nb.total_copies == 5

t("Librarian issue book POST", 'POST', '/dashboard/librarian/issue/', user=tu['librarian'], data={'book':book.id,'person':s_obj.id,'due_date':'2026-08-01'}, want_redirect='/dashboard/librarian/issues/')
issue = BookIssue.objects.filter(book=book,student=s_obj,status='Issued').first()
assert issue is not None
book.refresh_from_db()
assert book.available_copies == 4

t("Librarian issues list", 'GET', '/dashboard/librarian/issues/', user=tu['librarian'], want_code=200)
t("Librarian return book", 'POST', '/dashboard/librarian/issues/', user=tu['librarian'], data={'action':'return','return_id':issue.pk}, want_redirect='/dashboard/librarian/issues/')
issue.refresh_from_db()
assert issue.status == 'Returned'
book.refresh_from_db()
assert book.available_copies == 5

t("Librarian fines", 'GET', '/dashboard/librarian/fines/', user=tu['librarian'], want_code=200)
t("Librarian add fine", 'POST', '/dashboard/librarian/fines/', user=tu['librarian'], data={'action':'add','issue_id':issue.pk,'amount':100,'reason':'Late'}, want_redirect='/dashboard/librarian/fines/')
fine = BookFine.objects.filter(student=s_obj).order_by('-created_at').first()
assert fine is not None
t("Librarian pay fine", 'POST', '/dashboard/librarian/fines/', user=tu['librarian'], data={'action':'pay','fine_id':fine.pk}, want_redirect='/dashboard/librarian/fines/')
fine.refresh_from_db()
assert fine.status == 'Paid'

print("\n" + "=" * 70)
print(f"RESULTS: {p} PASSED, {f2} FAILED")
print("=" * 70)
if errs:
    print("\nFAILURES:")
    for e in errs:
        print(f"  - {e}")

print("\n--- CLEANING UP TEST DATA ---")
for uname in ['tnewstu','tnewfac','thodfac','tfacstu']:
    User.objects.filter(username=uname).delete()
Exam.objects.filter(title='Final26',institution=inst).delete()
Event.objects.filter(title='TechFest',institution=inst).delete()
Course.objects.filter(name='B.Sc Phy',institution=inst).delete()
Branch.objects.filter(name='CSE-B',course=course1).delete()
Subject.objects.filter(name='OS',institution=inst).delete()
Book.objects.filter(title__in=['Clean Code 2e','Clean Code'],institution=inst).delete()
Fee.objects.filter(fee_type='Hostel',institution=inst).delete()
Institution.objects.filter(slug='test-coll').delete()
print("Test data cleaned up.")
