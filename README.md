# Kneecap Backend

Kneecap is an open-source RSS generator and mirror project built with Django 5.1.4+.

## Features
- Dashboard for managing feeds and subscriptions
- Audio player with advanced playback controls
- RSS feed generation and mirroring
- OPML import/export
- REST API (Django REST Framework)
- Docker support for easy deployment

## Tech Stack
- Python (Django 5.1.4+)
- Django REST Framework
- feedparser
- python-dateutil
- requests
- django-solo
- SQLite (default DB)

## Getting Started

### Prerequisites
- Python 3.10+
- Docker (optional, for containerized deployment)

### Setup (Local)
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Docker
```bash
docker build -t kneecap-backend .
docker run -p 8000:8000 kneecap-backend
```

### API
API documentation is available at `/api/` when running locally.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](LICENSE)