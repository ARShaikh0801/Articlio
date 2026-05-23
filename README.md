# ✒️ Articlio Blog

[![Live Site](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge)](https://articlio-nb11.onrender.com/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4.0-06B6D4?style=for-the-badge&logo=tailwindcss)](https://tailwindcss.com/)

A modern, responsive, and secure blogging platform built using **Django** and **Tailwind CSS**. Articlio supports user authentication (including OAuth), user role management, custom themes, history tracking with reading progress, bookmarking, and nested comments.

> [!IMPORTANT]
> The live site is hosted on Render and may take a few moments to spin up from standby. It is optimized for larger desktop displays.

---

## 🚀 Features

- **Rich Authentication**: Multi-channel login support (standard email/password signup and social sign-in via Google & GitHub).
- **Profile Customization**: Choose custom roles (`Reader` or `Author`) and update display metrics.
- **Dynamic Theming Engine**: Select from five beautiful accent themes: Ocean 🔵, Emerald 🟢, Slate 🔘, Crimson 🔴, and Violet 🟣. The user dashboard, emails, and comments adapt instantly.
- **Blog Publisher**: Manage, draft, edit, and publish posts using modern templates.
- **Interactive Readers**: Bookmark posts, like articles, and comment with nested threads.
- **Reading History & Metrics**: Tracks articles viewed by the user and records their scroll/reading progress.
- **Bloom Filter Performance**: Employs an in-memory cached Bloom Filter to deliver instant username availability checks on signup.
- **Security Protections**: Configured Content Security Policy (CSP) with random script nonces and Clickjacking prevention headers.

---

## 🛠️ Tech Stack

- **Backend**: Django 5.2 (Python 3.11+)
- **Frontend**: HTML5, Vanilla JavaScript, CSS (Tailwind CSS v4 + PostCSS compile)
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

## 🖼️ Screenshots

<details>
  <summary>📸 Expand to View App Gallery</summary>

  <br>

  #### Home Page
  <img width="1890" height="1150" alt="127 0 0 1_8000_" src="https://github.com/user-attachments/assets/2cd5c6af-5d27-419d-8211-0c532ff3aaa7" />

  #### Article Feed
  <img width="1890" height="1129" alt="2" src="https://github.com/user-attachments/assets/98f7f949-8e97-4497-affb-e7877d2dd284" />

  #### Custom Dashboard
  <img width="1890" height="849" alt="3" src="https://github.com/user-attachments/assets/e2eb9d5b-90cc-4dcb-8d61-102f16c4e120" />

  #### Writing Interface
  <img width="1890" height="905" alt="4" src="https://github.com/user-attachments/assets/01b778be-44c3-427f-bff1-d4e861479a0d" />

  #### Themed Layout Examples
  <img width="1911" height="927" alt="5" src="https://github.com/user-attachments/assets/45dba872-2af4-46f7-8b07-e2e85c4b9328" />
  <img width="1890" height="974" alt="6" src="https://github.com/user-attachments/assets/1d7f946f-516d-4ff7-ad5f-05374815cdd4" />
  <img width="1920" height="927" alt="7" src="https://github.com/user-attachments/assets/ae5fcea6-ae4c-4e6d-a5c4-53e0a14fceec" />
  <img width="1890" height="1490" alt="8" src="https://github.com/user-attachments/assets/cf4e2367-5de0-4ca8-8539-4b0b9815deca" />
  <img width="1890" height="1160" alt="9" src="https://github.com/user-attachments/assets/4894134b-c827-4f40-b489-97edfe12e7a0" />
  <img width="1890" height="1361" alt="10" src="https://github.com/user-attachments/assets/d7f98092-7305-4132-95a9-afc1625c70e1" />
  <img width="1920" height="930" alt="11" src="https://github.com/user-attachments/assets/51f9d7b5-80a2-4369-a9dc-8481285d45a8" />
  <img width="1920" height="931" alt="12" src="https://github.com/user-attachments/assets/4820b23e-fcab-4c66-b614-509f0c8ce7d8" />
  <img width="1890" height="1039" alt="13" src="https://github.com/user-attachments/assets/e8daf271-85e3-4f61-b73c-c5998aafd84f" />
  <img width="1917" height="928" alt="t" src="https://github.com/user-attachments/assets/8d7343e1-215c-4df1-ac89-9f92f0252850" />
</details>

---

## 🤝 Contributing

Contributions are welcome! Please feel free to open issues or submit Pull Requests to help improve the project.
