# Airport Management System

## Project Description
A web-based application for managing flights, airplanes, routes, crew assignments,
and providing users with the ability to book tickets.

## Features
- Manage airplanes, flight schedules, and seat configurations.
- Assign crew members to flights.
- Track international routes and airports.
- Django admin panel for data management.
- User interface for browsing available flights and booking tickets easily.

## Technologies Used
- **Backend:** Django Framework
- **Database:** PostgreSQL
- **API:** Django REST Framework

## Installation
### Python 3 must be installed
1. Clone the repository:
   ```bash
   git clone https://github.com/danilsiv/airport-api.git
   cd airport-api
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate  # For Windows
3. Install dependencies:
    ```bash
   pip install -r requirements.txt
4. Apply database migrations:
    ```bash
   python manage.py migrate
5. Create a superuser (for accessing the admin panel):
   ```bash
   python manage.py createsuperuser
6. Start the development server:
    ```bash
   python manage.py runserver
7. To load test data into the database, use the following command:
    ```bash
   python manage.py loaddata data.json

## Database Structure
![API Structure](static/docs/API%20Structure.jpg)
