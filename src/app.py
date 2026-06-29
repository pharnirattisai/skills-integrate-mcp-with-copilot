"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

from db import (
    init_db,
    get_activities as db_get_activities,
    signup_for_activity as db_signup_for_activity,
    unregister_from_activity as db_unregister_from_activity,
)

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

init_db()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return db_get_activities()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    try:
        message = db_signup_for_activity(activity_name, email)
        return {"message": message}
    except KeyError:
        raise HTTPException(status_code=404, detail="Activity not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Student is already signed up")
    except OverflowError:
        raise HTTPException(status_code=400, detail="Activity is full")


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    try:
        message = db_unregister_from_activity(activity_name, email)
        return {"message": message}
    except KeyError:
        raise HTTPException(status_code=404, detail="Activity not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
