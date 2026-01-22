# Articlio Blog

Live on : https://articlio-nb11.onrender.com/

Note : Render Takes time to awake site (This Site is only utilized for big screens)

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
- **Database**: SQLite (Development) , postgresql (Production)
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

## Screenshotes

<img width="1890" height="1150" alt="127 0 0 1_8000_" src="https://github.com/user-attachments/assets/2cd5c6af-5d27-419d-8211-0c532ff3aaa7" />
<img width="1890" height="1129" alt="2" src="https://github.com/user-attachments/assets/98f7f949-8e97-4497-affb-e7877d2dd284" />
<img width="1890" height="849" alt="3" src="https://github.com/user-attachments/assets/e2eb9d5b-90cc-4dcb-8d61-102f16c4e120" />
<img width="1890" height="905" alt="4" src="https://github.com/user-attachments/assets/01b778be-44c3-427f-bff1-d4e861479a0d" />
<img width="1911" height="927" alt="5" src="https://github.com/user-attachments/assets/45dba872-2af4-46f7-8b07-e2e85c4b9328" />
<img width="1890" height="974" alt="6" src="https://github.com/user-attachments/assets/1d7f946f-516d-4ff7-ad5f-05374815cdd4" />
<img width="1920" height="927" alt="7" src="https://github.com/user-attachments/assets/ae5fcea6-ae4c-4e6d-a5c4-53e0a14fceec" />
<img width="1890" height="1490" alt="8" src="https://github.com/user-attachments/assets/cf4e2367-5de0-4ca8-8539-4b0b9815deca" />
<img width="1890" height="1160" alt="9" src="https://github.com/user-attachments/assets/4894134b-c827-4f40-b489-97edfe12e7a0" />
<img width="1890" height="1361" alt="10" src="https://github.com/user-attachments/assets/d7f98092-7305-4132-95a9-afc1625c70e1" />
<img width="1920" height="930" alt="11" src="https://github.com/user-attachments/assets/51f9d7b5-80a2-4369-a9dc-8481285d45a8" />
<img width="1920" height="931" alt="12" src="https://github.com/user-attachments/assets/4820b23e-fcab-4c66-b614-509f0c8ce7d8" />
<img width="1890" height="1039" alt="13" src="https://github.com/user-attachments/assets/e8daf271-85e3-4f61-b73c-c5998aafd84f" />


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.



