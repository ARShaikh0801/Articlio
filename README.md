# ✒️ Articlio Blog

[![Live Site](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge)](https://articlio-nb11.onrender.com/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4.0-06B6D4?style=for-the-badge&logo=tailwindcss)](https://tailwindcss.com/)

A modern, responsive, and secure blogging platform built using **Django** and **Tailwind CSS**. Articlio supports user authentication (including OAuth), user role management, custom themes, history tracking with reading progress, bookmarking, and nested comments.

> [!IMPORTANT]
> The live site is hosted on Render and may take a few moments to spin up from standby.

---

## 🚀 Features

- **Rich Authentication**: Multi-channel login support (standard email/password signup and social sign-in via Google & GitHub).
- **Profile Customization**: Choose custom roles (`Reader` or `Author`) and update display metrics.
- **Dynamic Theming Engine**: Select from five beautiful accent themes: Ocean 🔵, Emerald 🟢, Slate 🔘, Crimson 🔴, and Violet 🟣. The user dashboard, emails, and comments adapt instantly.
- **Immersive Focus Mode**: Distraction-free reading surface with customizable content width (Narrow / Medium / Wide), reading background themes (Sepia, Warm, Light, Dark), and font size adjustments (`A-`, `reset`, `A+`).
- **Text-to-Speech (TTS) Narrator**: Built-in audio narrator utilizing the Web Speech API with play/pause, playback speed adjustment, and position skipping for hands-free listening.
- **Rich Text Highlighting**: Native text selection highlighter allowing users to save custom colored highlights (Yellow, Green, Blue, Pink) with custom annotations, persisted to the database.
- **Blog Publisher**: Manage, draft, edit, and publish posts using modern templates.
- **Interactive Readers**: Bookmark posts, like articles, comment with nested threads, and upvote/like individual comments.
- **Reading History & Live Metrics**: Tracks article scroll progress with exact resumption and displays real-time estimated time remaining indicators (~X min left).
- **Global Search Shortcut**: Pressing `/` anywhere on the site instantly focuses the global navigation search bar (unless already typing).
- **Modular Frontend Architecture**: Refactored monolithic scripts into decoupled, single-responsibility JS files under `static/js/blogPost/` for maintainability.
- **Bloom Filter Performance**: Employs an in-memory cached Bloom Filter to deliver instant username availability checks on signup.
- **Security Protections**: Configured Content Security Policy (CSP) with random script nonces and Clickjacking prevention headers.

---

## 🛠️ Tech Stack

- **Backend**: Django 5.2 (Python 3.11+)
- **Frontend**: HTML5, Vanilla JavaScript (Web Speech API, local storage state persistence), CSS (Tailwind CSS v4 + PostCSS compile)
- **Database**: SQLite (local development) / PostgreSQL (production)
- **OAuth Providers**: Google & GitHub (via `django-allauth`)
- **Assets Manager**: WhiteNoise (compressed static files caching)

---

## 📂 Project Structure

```
Articlio Blog/
├── Articlio/          # Main configuration folder (settings, routing, middleware)
├── blog/              # Blog application (posts, comments, views, templates tags)
├── home/              # User account application (authentication, profile completion, utils)
├── docs/              # Developer guides & system design documents
│   └── architecture.md
├── static/            # Frontend assets (source CSS, custom JS, images)
├── templates/         # HTML structure & email layouts
├── manage.py          # Django administrative utility
├── requirements.txt   # Backend Python packages list
└── package.json       # Node.js build configurations
```

For a comprehensive breakdown of our code abstractions, database schemas, and background validation structures, please read the [Developer Architecture Guide](file:///c:/Users/A%20K%20Shaikh/Documents/Projects/Articlio%20Blog/docs/architecture.md).

---

## ⚙️ Local Development Setup

Follow these steps to run Articlio on your local machine:

### Prerequisites
Make sure you have installed:
- Python 3.11+
- Node.js (with npm)

### Step 1: Clone the Repository
```bash
git clone https://github.com/ARShaikh0801/Articlio.git
cd Articlio
```

### Step 2: Establish Virtual Environment
Create and launch a python virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
Install Python libraries and npm build utilities:
```bash
pip install -r requirements.txt
npm install
```

### Step 4: Environment Configurations
Create a `.env` file in the root folder of the project using the template below:
```env
# General Settings
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (Defaults to local SQLite if left empty/omitted)
# DATABASE_URL=postgresql://user:password@host:port/dbname

# Email Setup (For email verification / password resets)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Articlio <your-email@gmail.com>

# Social OAuth (Optional - For Google/GitHub logins)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### Step 5: Run Migrations
Generate database tables (SQLite will be created in your root folder by default):
```bash
python manage.py migrate
```

### Step 6: Compile Tailwind CSS
Build the static stylesheet outputs:
```bash
npm run build
```

### Step 7: Create Administrative Account
Set up the superuser to access the Django Admin Panel:
```bash
python manage.py createsuperuser
```

### Step 8: Start the Server
Run the local server:
```bash
python manage.py runserver
```
Navigate to `http://localhost:8000` to interact with the application.

---

## 📦 Production Deployment (Render)

The application is configured to deploy directly to **Render** using the settings in `render.yaml` and `build.sh`:
- **Build Command**: `./build.sh` (installs packages and runs `collectstatic` with Node binaries).
- **Start Command**: `gunicorn Articlio.wsgi:application`
- **Static files service**: Handled directly through WhiteNoise middleware configuration.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to open issues or submit Pull Requests to help improve the project.
