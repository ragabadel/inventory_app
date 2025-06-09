# IT Asset Management System

A comprehensive IT Asset Management System built with Django for tracking and managing IT assets, employee assignments, and department resources.

## Features

- Asset Management (computers, laptops, phones, etc.)
- Employee Management
- Department Organization
- Permission-based Access Control
- Asset History Tracking
- Notification System
- Warranty Management
- Asset Assignment Workflow

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 13 or higher
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd inventory_app
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\\venv\\Scripts\\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file:
```bash
cp .env.example .env
# Edit .env with your database and other configuration settings
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

### Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

- `DEBUG`: Set to False in production
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL database URL
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `TIME_ZONE`: Your timezone (default: UTC)

### Production Deployment

For production deployment:

1. Set DEBUG=False in .env
2. Configure proper database settings
3. Set up proper web server (e.g., Nginx + Gunicorn)
4. Configure static files serving
5. Set up SSL certificate

### Security Setup

1. Create a secure environment file:
```bash
cp .env.example .env
```

2. Generate a new Django secret key:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

3. Update the .env file with:
- The newly generated secret key
- Your database credentials
- Appropriate DEBUG setting (False for production)
- Allowed hosts for your environment
- Email settings if using email notifications

4. Security Checklist for Production:
- [ ] Set DEBUG=False
- [ ] Use strong, unique SECRET_KEY
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Set up SSL/TLS certificate
- [ ] Configure secure database credentials
- [ ] Enable HTTPS only
- [ ] Set up proper backup strategy
- [ ] Configure proper logging
- [ ] Review user permissions
- [ ] Set up firewall rules

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
