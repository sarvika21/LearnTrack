from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from io import BytesIO
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from app.auth.dependencies import get_current_user, require_admin, require_student
from app.database.connection import get_database
from app.automata.enrollment_dfa import transition as enrollment_transition
from app.automata.lesson_dfa import transition as lesson_transition

router = APIRouter(prefix="/api", tags=["Learning"])

def now():
    return datetime.now(timezone.utc)

def oid(value, label="id"):
    if not ObjectId.is_valid(value):
        raise HTTPException(400, f"Invalid {label}")
    return ObjectId(value)

def clean(doc):
    if not doc: return doc
    result = dict(doc)
    result["id"] = str(result.pop("_id"))
    for key, value in list(result.items()):
        if isinstance(value, ObjectId): result[key] = str(value)
        elif isinstance(value, datetime): result[key] = value.isoformat()
    return result

class CourseIn(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=5, max_length=2000)
    category: str = Field(default="General", max_length=60)
    level: str = Field(default="Beginner", max_length=30)
    published: bool = True

class LessonIn(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    content: str = Field(min_length=1, max_length=20000)
    video_url: str | None = None
    order: int = Field(ge=1)

class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(min_length=2)
    answer_index: int = Field(ge=0)
    explanation: str = ""

class QuizIn(BaseModel):
    title: str
    questions: list[QuizQuestion] = Field(min_length=1)
    pass_mark: int = Field(default=60, ge=1, le=100)

class QuizSubmission(BaseModel):
    answers: list[int]

def log_transition(db, user_id, course_id, lesson_id, entity, before, action, after):
    db["dfa_logs"].insert_one({
        "user_id": user_id, "course_id": course_id, "lesson_id": lesson_id,
        "entity": entity, "from_state": before, "action": action,
        "to_state": after, "valid": True, "created_at": now()
    })

@router.get("/courses")
def list_courses(user=Depends(get_current_user)):
    db = get_database()
    query = {} if user["role"] == "admin" else {"published": True}
    return {"courses": [clean(x) for x in db["courses"].find(query).sort("created_at", -1)]}

@router.post("/admin/courses", status_code=201)
def create_course(data: CourseIn, user=Depends(require_admin)):
    db = get_database()
    doc = data.model_dump()
    doc.update({"created_by": user["user_id"], "created_at": now(), "updated_at": now()})
    result = db["courses"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return {"course": clean(doc)}

@router.put("/admin/courses/{course_id}")
def update_course(course_id: str, data: CourseIn, user=Depends(require_admin)):
    db = get_database(); cid = oid(course_id, "course id")
    result = db["courses"].update_one({"_id": cid}, {"$set": {**data.model_dump(), "updated_at": now()}})
    if not result.matched_count: raise HTTPException(404, "Course not found")
    return {"course": clean(db["courses"].find_one({"_id": cid}))}

@router.delete("/admin/courses/{course_id}")
def delete_course(course_id: str, user=Depends(require_admin)):
    db = get_database(); cid = oid(course_id, "course id")
    if not db["courses"].find_one({"_id": cid}): raise HTTPException(404, "Course not found")
    db["courses"].delete_one({"_id": cid})
    return {"message": "Course deleted"}

@router.get("/courses/{course_id}")
def course_detail(course_id: str, user=Depends(get_current_user)):
    db = get_database(); cid = oid(course_id, "course id")
    course = db["courses"].find_one({"_id": cid})
    if not course or (user["role"] != "admin" and not course.get("published", True)):
        raise HTTPException(404, "Course not found")
    lessons = [clean(x) for x in db["lessons"].find({"course_id": str(cid)}).sort("order", 1)]
    return {"course": clean(course), "lessons": lessons}

@router.post("/courses/{course_id}/enroll")
def enroll(course_id: str, user=Depends(require_student)):
    db = get_database(); cid = oid(course_id, "course id"); uid = user["user_id"]
    if not db["courses"].find_one({"_id": cid, "published": True}):
        raise HTTPException(404, "Published course not found")
    enrollments = db["enrollments"]
    existing = enrollments.find_one({"course_id": str(cid), "user_id": uid})
    state = existing["state"] if existing else "NOT_ENROLLED"
    try: next_state = enrollment_transition(state, "REQUEST")
    except ValueError as e: raise HTTPException(409, str(e))
    doc = {"course_id": str(cid), "user_id": uid, "state": next_state, "updated_at": now()}
    enrollments.update_one({"course_id": str(cid), "user_id": uid}, {"$set": doc, "$setOnInsert": {"created_at": now()}}, upsert=True)
    log_transition(db, uid, str(cid), None, "enrollment", state, "REQUEST", next_state)
    # Enrolled immediately for this self-service learning platform: approve the request through the DFA.
    final_state = enrollment_transition(next_state, "APPROVE")
    enrollments.update_one({"course_id": str(cid), "user_id": uid}, {"$set": {"state": final_state, "updated_at": now()}})
    log_transition(db, uid, str(cid), None, "enrollment", next_state, "APPROVE", final_state)
    lessons = list(db["lessons"].find({"course_id": str(cid)}).sort("order", 1))
    if lessons:
        first = lessons[0]
        db["progress"].update_one(
            {"course_id": str(cid), "lesson_id": str(first["_id"]), "user_id": uid},
            {"$set": {"state": "UNLOCKED", "updated_at": now()}, "$setOnInsert": {"created_at": now()}}, upsert=True)
        log_transition(db, uid, str(cid), str(first["_id"]), "lesson", "LOCKED", "UNLOCK", "UNLOCKED")
    return {"message": "Enrolled successfully", "state": final_state}

@router.get("/my-courses")
def my_courses(user=Depends(require_student)):
    db = get_database(); uid = user["user_id"]
    items = []
    for enrollment in db["enrollments"].find({"user_id": uid, "state": "ENROLLED"}):
        course = db["courses"].find_one({"_id": oid(enrollment["course_id"])})
        if course:
            total = db["lessons"].count_documents({"course_id": enrollment["course_id"]})
            completed = db["progress"].count_documents({"course_id": enrollment["course_id"], "user_id": uid, "state": "QUIZ_PASSED"})
            items.append({"course": clean(course), "total_lessons": total, "completed_lessons": completed,
                          "progress": round(completed / total * 100) if total else 0})
    return {"courses": items}

@router.get("/courses/{course_id}/lessons")
def get_lessons(course_id: str, user=Depends(require_student)):
    db = get_database(); cid = oid(course_id, "course id"); uid = user["user_id"]
    if not db["enrollments"].find_one({"course_id": str(cid), "user_id": uid, "state": "ENROLLED"}):
        raise HTTPException(403, "Enroll in this course first")
    lessons = list(db["lessons"].find({"course_id": str(cid)}).sort("order", 1))
    output = []
    for i, lesson in enumerate(lessons):
        progress = db["progress"].find_one({"course_id": str(cid), "lesson_id": str(lesson["_id"]), "user_id": uid})
        output.append({"lesson": clean(lesson), "state": progress["state"] if progress else ("LOCKED" if i else "UNLOCKED")})
    return {"lessons": output}

@router.post("/admin/courses/{course_id}/lessons", status_code=201)
def create_lesson(course_id: str, data: LessonIn, user=Depends(require_admin)):
    db = get_database(); cid = oid(course_id, "course id")
    if not db["courses"].find_one({"_id": cid}): raise HTTPException(404, "Course not found")
    if db["lessons"].find_one({"course_id": str(cid), "order": data.order}):
        raise HTTPException(409, "A lesson already uses this order number")
    doc = {**data.model_dump(), "course_id": str(cid), "created_at": now()}
    result = db["lessons"].insert_one(doc); doc["_id"] = result.inserted_id
    return {"lesson": clean(doc)}

@router.put("/admin/lessons/{lesson_id}")
def update_lesson(lesson_id: str, data: LessonIn, user=Depends(require_admin)):
    db = get_database(); lid = oid(lesson_id, "lesson id")
    result = db["lessons"].update_one({"_id": lid}, {"$set": data.model_dump()})
    if not result.matched_count: raise HTTPException(404, "Lesson not found")
    return {"lesson": clean(db["lessons"].find_one({"_id": lid}))}

@router.delete("/admin/lessons/{lesson_id}")
def delete_lesson(lesson_id: str, user=Depends(require_admin)):
    db = get_database(); lid = oid(lesson_id, "lesson id")
    result = db["lessons"].delete_one({"_id": lid})
    if not result.deleted_count: raise HTTPException(404, "Lesson not found")
    db["quizzes"].delete_many({"lesson_id": lesson_id})
    return {"message": "Lesson deleted"}

@router.post("/lessons/{lesson_id}/start")
def start_lesson(lesson_id: str, user=Depends(require_student)):
    db = get_database(); lid = oid(lesson_id, "lesson id"); uid = user["user_id"]
    lesson = db["lessons"].find_one({"_id": lid})
    if not lesson: raise HTTPException(404, "Lesson not found")
    cid = lesson["course_id"]
    if not db["enrollments"].find_one({"course_id": cid, "user_id": uid, "state": "ENROLLED"}):
        raise HTTPException(403, "You are not enrolled in this course")
    progress = db["progress"].find_one({"course_id": cid, "lesson_id": str(lid), "user_id": uid})
    state = progress["state"] if progress else "LOCKED"
    try: after = lesson_transition(state, "START") if state == "UNLOCKED" else state
    except ValueError as e: raise HTTPException(409, str(e))
    if state not in ("UNLOCKED", "IN_PROGRESS"): raise HTTPException(409, f"Lesson is {state}; complete the previous lesson first")
    if state == "UNLOCKED":
        db["progress"].update_one({"course_id": cid, "lesson_id": str(lid), "user_id": uid},
            {"$set": {"state": after, "updated_at": now()}, "$setOnInsert": {"created_at": now()}}, upsert=True)
        log_transition(db, uid, cid, str(lid), "lesson", state, "START", after)
    return {"lesson": clean(lesson), "state": after}

@router.post("/lessons/{lesson_id}/complete")
def complete_lesson(lesson_id: str, user=Depends(require_student)):
    db = get_database(); lid = oid(lesson_id, "lesson id"); uid = user["user_id"]
    lesson = db["lessons"].find_one({"_id": lid})
    if not lesson: raise HTTPException(404, "Lesson not found")
    cid = lesson["course_id"]
    progress = db["progress"].find_one({"course_id": cid, "lesson_id": str(lid), "user_id": uid})
    state = progress["state"] if progress else "LOCKED"
    try: after = lesson_transition(state, "COMPLETE")
    except ValueError as e: raise HTTPException(409, str(e))
    db["progress"].update_one({"course_id": cid, "lesson_id": str(lid), "user_id": uid},
        {"$set": {"state": after, "updated_at": now()}, "$setOnInsert": {"created_at": now()}}, upsert=True)
    log_transition(db, uid, cid, str(lid), "lesson", state, "COMPLETE", after)
    quiz = db["quizzes"].find_one({"lesson_id": str(lid)})
    return {"state": after, "quiz_available": bool(quiz), "message": "Lesson marked complete. Pass its quiz to unlock the next lesson."}

@router.post("/admin/lessons/{lesson_id}/quiz", status_code=201)
def create_quiz(lesson_id: str, data: QuizIn, user=Depends(require_admin)):
    db = get_database(); lid = oid(lesson_id, "lesson id")
    lesson = db["lessons"].find_one({"_id": lid})
    if not lesson: raise HTTPException(404, "Lesson not found")
    doc = {"lesson_id": str(lid), "course_id": lesson["course_id"], "title": data.title,
           "questions": [q.model_dump() for q in data.questions], "pass_mark": data.pass_mark, "created_at": now()}
    db["quizzes"].replace_one({"lesson_id": str(lid)}, doc, upsert=True)
    return {"message": "Quiz saved"}

@router.get("/lessons/{lesson_id}/quiz")
def get_quiz(lesson_id: str, user=Depends(require_student)):
    db = get_database(); lid = oid(lesson_id, "lesson id"); quiz = db["quizzes"].find_one({"lesson_id": str(lid)})
    if not quiz: raise HTTPException(404, "Quiz not found")
    return {"quiz": {"title": quiz["title"], "pass_mark": quiz["pass_mark"],
        "questions": [{"question": q["question"], "options": q["options"]} for q in quiz["questions"]]}}

@router.post("/lessons/{lesson_id}/quiz/submit")
def submit_quiz(lesson_id: str, data: QuizSubmission, user=Depends(require_student)):
    db = get_database(); lid = oid(lesson_id, "lesson id"); uid = user["user_id"]
    quiz = db["quizzes"].find_one({"lesson_id": str(lid)})
    if not quiz: raise HTTPException(404, "Quiz not found")
    lesson = db["lessons"].find_one({"_id": lid}); cid = lesson["course_id"]
    progress = db["progress"].find_one({"course_id": cid, "lesson_id": str(lid), "user_id": uid})
    if not progress or progress["state"] != "COMPLETED": raise HTTPException(409, "Complete the lesson before taking its quiz")
    questions = quiz["questions"]
    if len(data.answers) != len(questions): raise HTTPException(400, "Submit one answer per question")
    correct = sum(1 for i, q in enumerate(questions) if data.answers[i] == q["answer_index"])
    score = round(correct / len(questions) * 100)
    passed = score >= quiz["pass_mark"]
    db["quiz_attempts"].insert_one({"user_id": uid, "course_id": cid, "lesson_id": str(lid),
        "score": score, "passed": passed, "submitted_at": now()})
    if passed:
        after = lesson_transition("COMPLETED", "PASS_QUIZ")
        db["progress"].update_one({"course_id": cid, "lesson_id": str(lid), "user_id": uid},
            {"$set": {"state": after, "updated_at": now(), "quiz_score": score}})
        log_transition(db, uid, cid, str(lid), "lesson", "COMPLETED", "PASS_QUIZ", after)
        next_lesson = db["lessons"].find_one({"course_id": cid, "order": {"$gt": lesson["order"]}}, sort=[("order", 1)])
        if next_lesson:
            db["progress"].update_one({"course_id": cid, "lesson_id": str(next_lesson["_id"]), "user_id": uid},
                {"$set": {"state": "UNLOCKED", "updated_at": now()}, "$setOnInsert": {"created_at": now()}}, upsert=True)
            log_transition(db, uid, cid, str(next_lesson["_id"]), "lesson", "LOCKED", "UNLOCK", "UNLOCKED")
        else:
            db["certificates"].update_one({"user_id": uid, "course_id": cid},
                {"$setOnInsert": {"user_id": uid, "course_id": cid, "issued_at": now(), "certificate_code": f"LT-{uid[-6:]}-{str(cid)[-6:]}"}}, upsert=True)
    return {"score": score, "passed": passed, "pass_mark": quiz["pass_mark"],
            "message": "Quiz passed! Next lesson unlocked." if passed else "Not passed yet. Review the lesson and try again."}

@router.get("/student/progress")
def student_progress(user=Depends(require_student)):
    db = get_database(); uid = user["user_id"]; rows = []
    for enrollment in db["enrollments"].find({"user_id": uid, "state": "ENROLLED"}):
        cid = enrollment["course_id"]; course = db["courses"].find_one({"_id": oid(cid)})
        total = db["lessons"].count_documents({"course_id": cid})
        done = db["progress"].count_documents({"course_id": cid, "user_id": uid, "state": "QUIZ_PASSED"})
        rows.append({"course": course.get("title") if course else "Course", "total": total, "completed": done,
                     "percent": round(done / total * 100) if total else 0})
    return {"progress": rows}


@router.get("/student/certificates/{certificate_id}/download")
def download_certificate(
    certificate_id: str,
    user=Depends(require_student)
):
    db = get_database()

    certificate = db["certificates"].find_one({
        "_id": oid(certificate_id, "certificate id"),
        "user_id": user["user_id"]
    })

    if not certificate:
        raise HTTPException(404, "Certificate not found")

    course = db["courses"].find_one({
        "_id": oid(certificate["course_id"], "course id")
    })

    course_title = course.get("title", "LearnTrack Course") if course else "LearnTrack Course"

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setTitle("LearnTrack Completion Certificate")
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(width / 2, height - 150, "CERTIFICATE OF COMPLETION")

    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(width / 2, height - 220, "This certificate is proudly presented to")

    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(width / 2, height - 270, user.get("name", "Student"))

    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(width / 2, height - 330, "For successfully completing")

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(width / 2, height - 370, course_title)

    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(
        width / 2, height - 440,
        f"Certificate ID: {certificate['certificate_code']}"
    )

    pdf.drawCentredString(
        width / 2, height - 465,
        f"Issued: {certificate['issued_at'].strftime('%d-%m-%Y')}"
    )

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(width / 2, height - 540, "LearnTrack")

    pdf.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="LearnTrack-{certificate["certificate_code"]}.pdf"'
        }
    )

@router.get("/admin/students")
def admin_students(user=Depends(require_admin)):
    db = get_database()
    return {"students": [clean(x) for x in db["users"].find({"role": "student"}, {"password_hash": 0})]}

@router.get("/admin/overview")
def admin_overview(user=Depends(require_admin)):
    db = get_database()
    return {"students": db["users"].count_documents({"role": "student"}),
            "courses": db["courses"].count_documents({}),
            "enrollments": db["enrollments"].count_documents({"state": "ENROLLED"}),
            "certificates": db["certificates"].count_documents({})}



@router.get("/admin/progress")
def admin_progress(user=Depends(require_admin)):
    """Aggregate enrolment and lesson progress for the admin monitoring screen."""
    db = get_database()
    rows = []
    for enrollment in db["enrollments"].find({"state": "ENROLLED"}).sort("updated_at", -1):
        uid = enrollment.get("user_id")
        cid = enrollment.get("course_id")
        student = None
        try:
            student = db["users"].find_one({"_id": ObjectId(uid)}) if ObjectId.is_valid(uid) else None
        except Exception:
            student = None
        course = None
        try:
            course = db["courses"].find_one({"_id": ObjectId(cid)}) if ObjectId.is_valid(cid) else None
        except Exception:
            course = None
        total = db["lessons"].count_documents({"course_id": cid})
        completed = db["progress"].count_documents({
            "course_id": cid, "user_id": uid, "state": "QUIZ_PASSED"
        })
        rows.append({
            "student_id": uid,
            "student_name": student.get("name", "Unknown student") if student else "Unknown student",
            "student_email": student.get("email", "") if student else "",
            "course_id": cid,
            "course_title": course.get("title", "Deleted course") if course else "Deleted course",
            "completed_lessons": completed,
            "total_lessons": total,
            "percent": round(completed / total * 100) if total else 0,
            "enrollment_state": enrollment.get("state", "UNKNOWN"),
        })
    return {"progress": rows}

@router.get("/admin/dfa-logs")
def dfa_logs(user=Depends(require_admin)):
    db = get_database()
    return {"logs": [clean(x) for x in db["dfa_logs"].find().sort("created_at", -1).limit(100)]}
