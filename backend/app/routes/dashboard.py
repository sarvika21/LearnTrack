
from fastapi import APIRouter, Depends

from app.auth.dependencies import require_student, require_admin

router = APIRouter(prefix="/api", tags=["Dashboards"])

@router.get("/student/dashboard")
def student_dashboard(user=Depends(require_student)):
    return {
        "message": "Welcome to your student dashboard!",
        "role": "student",
        "user_id": user["user_id"],
        "courses": [],
        "completed_lessons": 0,
        "progress": 0
    }

@router.get("/admin/dashboard")
def admin_dashboard(user=Depends(require_admin)):
    return {
        "message": "Welcome to the admin dashboard!",
        "role": "admin",
        "user_id": user["user_id"]
    }