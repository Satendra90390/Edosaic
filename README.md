# Edosaic — Student Management System
---

## About

**Edosaic** is a comprehensive, role-based Student Management System built with Django, designed to streamline academic administration for schools, colleges, universities, and coaching centers. It provides a centralized platform to manage students, faculty, courses, attendance, grades, fees, exams, library resources, and events — all accessible through secure, role-specific dashboards.

What sets Edosaic apart is **STAN** — an integrated AI chatbot powered by Groq's Llama 3.1 8B model that is context-aware of your institution's data. STAN can answer real-time questions about student counts, attendance rates, fee collections, and academic performance, making administrative decisions faster and smarter.

### Key Highlights

- **Multi-Tenant Architecture** — Complete data isolation between institutions using a shared codebase
- **6 Role-Based Dashboards** — Admin, Accountant, Librarian, Faculty, Student, and Parent, each with tailored permissions and views
- **AI-Powered Assistant (STAN)** — Context-aware chatbot that queries your institution's live data
- **Full Academic Workflow** — Courses, branches, subjects, faculty assignments, attendance, exams, results, and grade tracking
- **Library & Event Management** — Book inventory, issue/return tracking, fine management, and institutional event scheduling
- **OAuth Authentication** — Secure login via Google and GitHub, plus invite-code-based self-registration
- **Dual Theme UI** — Light mode with professional gradients and dark mode with glassmorphism and neon accents
- **Responsive Design** — Fully functional on desktop, tablet, and mobile devices
- **Production-Ready** — Dockerized with Gunicorn, PostgreSQL, and auto-deploy support via Render.com and Oracle Cloud

### Security

- **CSRF Protection** — Enabled on all forms with `{% csrf_token %}` and API endpoints via `X-CSRFToken` header
- **XSS Prevention** — Django template auto-escaping enabled; no `mark_safe` or `|safe` usage; client-side `escapeHtml()` for chat messages
- **SQL Injection Safe** — Pure Django ORM usage; no raw SQL queries anywhere in the codebase
- **Rate Limiting** — `django-ratelimit` on login (5/min), registration (3/min), and chat endpoints (10-20/min)
- **HTTPS Enforcement** — HSTS headers, SSL redirect, and secure cookies enabled in production
- **Password Validation** — Minimum 8 characters with common password, numeric password, and user attribute similarity checks
- **Role-Based Access Control** — Every dashboard view checks `request.user.role`; OAuth users cannot self-select admin
- **CSRF-Protected Logout** — Logout requires POST with CSRF token, preventing session fixation via GET
- **Session Security** — `HttpOnly` and `Secure` flags on session and CSRF cookies in production
- **Docker Hardening** — Non-root container user, PostgreSQL not exposed to host, no default DB password fallback
- **Secrets Management** — All secrets via environment variables; `DEBUG` defaults to `False`; `SECRET_KEY` required (fails if missing)

### Built With

Python 3.12 · Django 6.0.7 · PostgreSQL 16 · django-allauth · Groq API · Docker · Render.com

## Features

### Role-Based Dashboards
- **Admin** — Full control: manage students, faculty, subjects, fees, reports, and analytics
- **Faculty** — View teaching assignments, department info
- **Student** — View results, fees, and quick actions
- **Parent** — Monitor child's grades and attendance

### Core Functionality
- **Student Management** — Add, search, and delete students with account credentials
- **Faculty Management** — Register faculty with department, qualification, and login access
- **Course & Subject Management** — Create courses, assign faculty to teach specific subjects
- **Attendance Tracking** — Record daily present/absent/late status per student
- **Results & Grades** — Track student performance across courses with letter grades
- **Fee Management** — Track tuition, exam, and other fees with Paid/Pending/Partial status
- **System Analytics** — Student-faculty ratio, attendance rate, and summary stats with charts

### AI Assistant (STAN)
- Context-aware chatbot that knows your institution's data
- Ask about students, attendance, fees, or get summaries
- Powered by Groq Llama 3.1 8B

### Design
- **Dual Theme** — Light mode (professional, soft gradients) and dark mode (glassmorphism, neon glow)
- **Responsive** — Works on desktop, tablet, and mobile with hamburger menu
- **Lucide Icons** — Crisp vector icons throughout the interface
- **Chart.js** — Doughnut charts for analytics visualizations

### Authentication
- Custom user model with role-based access (Admin / Faculty / Student / Parent)
- OAuth login via Google and GitHub (django-allauth)
- Institution registration with 2-step wizard (details + admin account)
- Password strength indicator

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.0.7, Python 3.12 |
| Database | PostgreSQL 16 (SQLite for dev) |
| Auth | django-allauth 65.x (OAuth + credentials) |
| AI Chat | Groq API (Llama 3.1 8B) |
| Frontend | Custom CSS (dual-theme design system), Lucide Icons, Chart.js |
| Deployment | Render.com, Docker |
| Static Files | Whitenoise |

## Project Structure

```
sms-django/
├── sms_django/           # Project config (settings, urls, wsgi)
├── accounts/             # Auth, user model, OAuth, landing page
├── core/                 # Business logic, models, dashboards, AI chat
├── templates/            # HTML templates
│   ├── components/       # Reusable sidebar templates
│   ├── admin_panel/      # Admin dashboard pages
│   ├── faculty/          # Faculty dashboard
│   ├── student/          # Student dashboard
│   ├── parent/           # Parent dashboard
│   └── accounts/         # Login, register, landing, role-select
├── static/css/           # theme.css, style.css, auth.css, chat.css, landing.css
├── Dockerfile
├── docker-compose.yml
└── render.yaml
```

## Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL (or use SQLite for development)
- A Groq API key (for STAN chatbot)

### Local Development

```bash
# Clone the repository
git clone https://github.com/Satendra90390/SMS-Pro.git
cd SMS-Pro

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your values

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed demo data (optional)
python seed.py

# Start development server
python manage.py runserver
```

### Environment Variables

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Optional — OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# Optional — AI Chatbot
GROQ_API_KEY=
```

### Docker Deployment

```bash
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### Render.com Deployment

The project includes `render.yaml` for automatic deployment. Just connect your GitHub repo to Render and it will configure the web service and PostgreSQL database automatically.

## Demo Credentials

After running `python seed.py`, use these to log in:

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Faculty | faculty1 | pass1234 |
| Student | student1 | pass1234 |
| Parent | parent1 | pass1234 |

## License

This project is open source and available under the [MIT License](LICENSE).
