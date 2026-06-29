# Mergington High School Activities API

A FastAPI application that allows students to view and sign up for extracurricular activities.

This project now uses a persistent SQLite database with file-based schema migrations.

## Features

- View all available extracurricular activities
- Sign up for activities
- Unregister from activities
- Persist activity and registration data across app restarts

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
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister from an activity                                      |

## Persistence and Migrations

- Database file: `src/data/activities.db`
- Migrations folder: `src/migrations/`
- Current migration: `src/migrations/001_init.sql`

On startup, the app automatically:

1. Creates the database file if it does not exist.
2. Applies any SQL files in `src/migrations/` that have not run yet.
3. Seeds default activities and participants if the `activities` table is empty.

No manual migration command is required for local development right now.

## Data Model

The database schema includes:

1. `users`
2. `clubs`
3. `club_memberships`
4. `events`
5. `event_registrations`
6. `activities`
7. `activity_participants`

The current UI/API flow uses `activities` and `activity_participants`. The remaining tables are included in the initial schema to support upcoming features.

For activity APIs, the model remains:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

Data is now stored in SQLite and survives application restarts.
