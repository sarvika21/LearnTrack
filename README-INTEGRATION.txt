LEARNTRACK FEATURE ADDITIONS — INSTALLATION GUIDE

This is an overlay package. It contains NEW files and REPLACEMENTS for your existing project.
Keep a backup of your original LearnTrack folder before copying anything.

FEATURES ADDED
- Admin course creation, editing API, deletion, lesson creation and quiz authoring.
- Student course catalogue, enrolment, enrolled courses and sequential lesson access.
- Lesson workflow enforced by a finite-state machine: LOCKED -> UNLOCKED -> IN_PROGRESS -> COMPLETED -> QUIZ_PASSED.
- Enrolment workflow enforced by a finite-state machine: NOT_ENROLLED -> REQUESTED -> ENROLLED.
- Quiz scoring, pass mark, retry support, progress summaries and PDF certificates.
- Admin student list, dashboard counts and DFA transition log.
- MongoDB collections are created automatically as data is written: courses, lessons, enrollments,
  progress, quizzes, quiz_attempts, certificates and dfa_logs.

IMPORTANT EXISTING PROJECT SETTINGS
- Backend reads MONGO_URI and DATABASE_NAME from backend/.env.
- Backend reads JWT_SECRET from backend/.env.
- Do NOT replace your real backend/.env. Keep it private.
- Login uses your existing PyJWT/pwdlib implementation and token fields (sub, role).
- Public registration always creates student accounts. Create admins with your existing
  command: from backend folder, run `python -m app.create_admin`.

WHERE TO COPY
Copy the contents of this ZIP into your existing LearnTrack project folder, preserving folders.
When Windows asks whether to replace files, replace ONLY these listed existing files:
  backend/requirements.txt
  backend/app/main.py
  backend/app/automata/enrollment_dfa.py
  backend/app/automata/lesson_dfa.py
  frontend/src/pages/Dashboard.jsx
  frontend/src/pages/SecPage.jsx
  frontend/src/App.css
New files:
  backend/app/routes/learning.py
  backend/.env.example
  .gitignore
  README-INTEGRATION.txt

Do not copy .env.example over .env and do not delete your existing .env.

INSTALL / RUN
1. Open VS Code in the LearnTrack folder.
2. Open a terminal in backend:
   Windows PowerShell: .\venv\Scripts\Activate.ps1
   If PowerShell blocks activation, use Command Prompt:
   venv\Scripts\activate.bat
3. Install backend requirements:
   pip install -r requirements.txt
4. Start FastAPI from the backend folder:
   uvicorn app.main:app --reload
5. Open another terminal in frontend:
   npm install
   npm run dev
6. Visit http://localhost:5173. API docs: http://127.0.0.1:8000/docs

ADMIN WORKFLOW
- Create the first admin account from the backend terminal:
  python -m app.create_admin
- Sign in using the admin email/password and choose Admin in the login screen.
- In the admin dashboard choose Overview to create a course.
- Choose Courses, open the course, add lessons in order starting at 1.
- In the quiz section choose a lesson and enter quiz questions as JSON.
  Each question must have: question, options (array), answer_index (zero-based integer).
  Example:
  [
    {"question":"Which is a programming language?","options":["Python","HTML tag"],"answer_index":0}
  ]

STUDENT WORKFLOW
- Register a student account.
- Sign in as Student, open Course catalogue, enroll.
- Open My courses, open the course, start the unlocked lesson, mark it complete, then pass its quiz.
- Passing a quiz unlocks the next lesson. Passing the final lesson quiz issues a PDF certificate.

NOTES / LIMITATIONS
- The platform uses self-service enrolment: the API records REQUESTED and immediately approves it through
  the DFA, so the final state is ENROLLED. Admin approval/rejection UI is not included yet.
- Admin course update and lesson update/delete endpoints are available in the API, while the current
  dashboard provides course creation/deletion and lesson/quiz creation UI.
- This integration package has been syntax-checked for Python. Run the application and verify the
  Atlas connection in your own environment before deploying.
