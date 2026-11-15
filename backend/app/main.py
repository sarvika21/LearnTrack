from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import connect_database
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.learning import router as learning_router

app = FastAPI(
    title="LearnTrack API",
    description="E-Learning and Student Progress Tracking System Using Finite Automata",
    version="2.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(learning_router)

@app.on_event("startup")
def startup_event():
    db = connect_database()
    db["users"].create_index("email", unique=True)
    db["enrollments"].create_index([("course_id", 1), ("user_id", 1)], unique=True)
    db["progress"].create_index([("course_id", 1), ("lesson_id", 1), ("user_id", 1)], unique=True)
    db["courses"].create_index("created_at")
    db["lessons"].create_index([("course_id", 1), ("order", 1)], unique=True)

@app.get("/")
def home():
    return {"message": "Welcome to LearnTrack API!", "status": "Running"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "database": "connected", "project": "LearnTrack"}
