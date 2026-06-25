"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import json
import os
import secrets
from pathlib import Path
from threading import Lock

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

security = HTTPBasic()
db_lock = Lock()
data_dir = current_dir / "data"
db_file = data_dir / "db.json"

DEFAULT_DB = {
    "users": {
        "teacher@mergington.edu": {
            "name": "Ms. Carter",
            "password": "teacher123",
            "role": "organizer"
        },
        "emma@mergington.edu": {
            "name": "Emma Johnson",
            "password": "student123",
            "role": "student"
        },
        "sophia@mergington.edu": {
            "name": "Sophia Brown",
            "password": "student123",
            "role": "student"
        }
    },
    "activities": {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the school soccer team and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice and play basketball with the school team",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "mia@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore your creativity through painting and drawing",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act, direct, and produce plays and performances",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
        },
        "Math Club": {
            "description": "Solve challenging problems and participate in math competitions",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
        }
    }
}


def initialize_db() -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    if not db_file.exists():
        with db_file.open("w", encoding="utf-8") as file:
            json.dump(DEFAULT_DB, file, indent=2)


def load_db() -> dict:
    with db_lock:
        with db_file.open("r", encoding="utf-8") as file:
            return json.load(file)


def save_db(data: dict) -> None:
    with db_lock:
        with db_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> dict:
    db = load_db()
    user = db["users"].get(credentials.username)

    if not user or not secrets.compare_digest(user["password"], credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return {
        "email": credentials.username,
        "name": user.get("name", ""),
        "role": user.get("role", "student")
    }


initialize_db()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/auth/login")
def login(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Login successful",
        "user": current_user
    }


@app.get("/auth/me")
def me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}


@app.get("/activities")
def get_activities():
    db = load_db()
    return db["activities"]


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, current_user: dict = Depends(get_current_user)):
    """Sign up the authenticated user for an activity."""
    db = load_db()
    activities = db["activities"]
    email = current_user["email"]

    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Add student
    activity["participants"].append(email)
    save_db(db)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, current_user: dict = Depends(get_current_user)):
    """Unregister the authenticated user from an activity."""
    db = load_db()
    activities = db["activities"]
    email = current_user["email"]

    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    save_db(db)
    return {"message": f"Unregistered {email} from {activity_name}"}
