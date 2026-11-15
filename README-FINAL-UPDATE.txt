LEARNTRACK — UPDATED COMPLETE PROJECT

This ZIP is based on the uploaded LearnTrack(1).zip source tree.
The original folder structure is preserved. The .git folder, nested ZIP backups,
Python bytecode caches, and any .env files are excluded.

WHAT WAS ALREADY PRESENT IN THE UPLOADED SOURCE
- React frontend calling FastAPI REST endpoints using Axios and JSON.
- JWT bearer authentication; registration creates student accounts; admin/student
  role dependencies protect backend routes.
- Admin dashboard overview, course create/list/delete, course update API,
  lesson create/update/delete APIs, quiz create/replace API.
- Student catalogue/course details, enrolment, my courses, sequential lesson
  state handling, lesson start/completion, quiz attempts/scores, progress and
  PDF certificates.
- Enrolment and lesson DFAs with invalid transitions rejected as HTTP 409.
- MongoDB transition history for successful transitions.
- Admin student listing and DFA log listing.
- Existing login/auth and MongoDB connection files retained.

ADDED IN THIS UPDATE
- Dark theme across the login page, dashboard, forms, cards, modal and navigation.
- Admin Progress Monitor tab with per-student/per-course progress aggregation
  sourced from MongoDB.
- DFA state-flow visualization in the admin DFA Logs screen.

IMPORTANT GAPS IN THE UPLOADED SOURCE (not represented as fully implemented)
- Student management is currently a registered-student listing, not account
  editing/suspension/deletion.
- Admin UI offers create/delete courses, but course edit is API-only.
- Lesson update/delete are API-only; the admin UI currently adds lessons.
- Quiz management UI creates/replaces quizzes; it does not provide a full
  question-by-question quiz editor.
- Invalid transitions are rejected by the DFA/API, but the existing transition
  history stores successful transitions only (not rejected attempts).

SETUP
1. Extract this ZIP.
2. Copy your private backend/.env into the extracted backend folder.
   Do NOT share or upload that file. Required names used by this project:
   MONGO_URI, DATABASE_NAME, JWT_SECRET.
3. Recreate the Python virtual environment in backend if needed:
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
4. In backend terminal:
   uvicorn app.main:app --reload
5. In a second terminal:
   cd frontend
   npm install
   npm run dev
6. Open http://localhost:5173
7. API docs: http://127.0.0.1:8000/docs

No real .env, venv, or node_modules is included in this archive.
