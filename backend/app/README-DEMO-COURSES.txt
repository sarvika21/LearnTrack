LEARNTRACK — TWO DEMO COURSES

This small add-on inserts two complete courses into the MongoDB database configured
by your existing backend/.env. It does not change your login, frontend, or existing
course records.

Adds:
1. Python Programming Fundamentals — 3 lessons, each with a quiz.
2. Web Development Essentials — 3 lessons, each with a quiz.

Total: 2 courses, 6 lessons, 6 quizzes, 18 quiz questions.

INSTALL
1. Extract this ZIP.
2. Copy the file backend/app/seed_demo_courses.py into your existing project at:
   LearnTrack/backend/app/seed_demo_courses.py
3. Do not replace your existing .env. It must contain the working MONGO_URI and DATABASE_NAME.
4. Open a terminal in LearnTrack/backend.
5. Activate the existing virtual environment:
   PowerShell: .\venv\Scripts\Activate.ps1
   If PowerShell blocks scripts, use Command Prompt:
   venv\Scripts\activate.bat
6. Run:
   python -m app.seed_demo_courses

IMPORTANT
- Run the script from the backend directory.
- It uses the existing app.database.connection.connect_database() function.
- It is safe to run again: it updates these two demo courses by seed_key instead
  of creating duplicate course/lesson/quiz records.
- Existing courses are not deleted.
- It uses the schema expected by the LearnTrack learning API:
  courses, lessons, quizzes.
- After success, sign in as Admin and click Courses in the left sidebar.
  The admin account sees the courses and can inspect their lessons.
- Sign out and register/sign in as a Student to browse and enroll in published courses.
