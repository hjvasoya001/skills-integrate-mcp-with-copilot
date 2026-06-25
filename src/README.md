# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Login with student/organizer credentials
- Sign up and unregister for activities as the authenticated user
- Persist users, activities, and registrations in a JSON database

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| GET    | `/auth/login`                                                     | Validate HTTP Basic credentials and return user info                |
| GET    | `/auth/me`                                                        | Return current authenticated user                                   |
| POST   | `/activities/{activity_name}/signup`                              | Sign up authenticated user for an activity                          |
| DELETE | `/activities/{activity_name}/unregister`                          | Unregister authenticated user from an activity                      |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Users** - Uses email as identifier:
   - Name
   - Role (`student` or `organizer`)
   - Password (demo-only plain text)

All data is stored in `src/data/db.json`, so updates survive server restarts.

## Demo Credentials

- `emma@mergington.edu` / `student123`
- `sophia@mergington.edu` / `student123`
- `teacher@mergington.edu` / `teacher123`
