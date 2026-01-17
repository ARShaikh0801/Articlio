# Articlio Blog

A Django-based blogging platform with user authentication, blog management, and interactive features.

## Features

- User authentication and profile management
- Create, edit, and publish blog posts
- Category and tag system for blog organization
- Bookmarking functionality for readers
- Like and comment system
- Search functionality

## Tech Stack

- **Backend**: Django 5.2
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **Database**: SQLite
- **CSS Framework**: Tailwind CSS
- **Build Tool**: npm

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js
- pip and npm

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/ARShaikh0801/Articlio.git
   cd "Articlio Blog"
   ```

2. Create virtual environment
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   npm install
   ```

4. Run migrations
   ```bash
   python manage.py migrate
   ```

5. Create superuser
   ```bash
   python manage.py createsuperuser
   ```

6. Start development server
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` in your browser.

## Project Structure

```
.
├── Articlio/          # Django project settings
├── blog/              # Blog application
├── home/              # Authentication app
├── static/            # Static files (CSS, JS, images)
├── templates/         # HTML templates
├── manage.py          # Django CLI
├── requirements.txt   # Python dependencies
└── package.json       # Node.js dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


