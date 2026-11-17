
import { useEffect, useState } from "react";
import API from "../services/api";

function Dashboard({ user, onLogout }) {
  const isAdmin = user.role === "admin";
  const [tab, setTab] = useState(isAdmin ? "overview" : "catalog");
  const [courses, setCourses] = useState([]);
  const [mine, setMine] = useState([]);
  const [overview, setOverview] = useState({});
  const [students, setStudents] = useState([]);
  const [logs, setLogs] = useState([]);
  const [progress, setProgress] = useState([]);
  const [selected, setSelected] = useState(null);
  const [lessons, setLessons] = useState([]);
  const [activeLesson, setActiveLesson] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const [courseForm, setCourseForm] = useState({
    title: "",
    description: "",
    category: "",
    level: "Beginner",
    published: true,
  });

  const [lessonForm, setLessonForm] = useState({
    title: "",
    content: "",
    order: 1,
    video_url: "",
  });

  const [quizForm, setQuizForm] = useState({
    lesson_id: "",
    title: "",
    pass_mark: 60,
    questions:
      '[{"question":"What is the main idea?","options":["Option A","Option B"],"answer_index":0,"explanation":""}]',
  });

  async function load() {
    setError("");

    try {
      if (isAdmin) {
        const [c, o, s, l, p] = await Promise.all([
          API.get("/api/courses"),
          API.get("/api/admin/overview"),
          API.get("/api/admin/students"),
          API.get("/api/admin/dfa-logs"),
          API.get("/api/admin/progress"),
        ]);

        setCourses(c.data.courses);
        setOverview(o.data);
        setStudents(s.data.students);
        setLogs(l.data.logs);
        setProgress(p.data.progress);
      } else {
        const [c, m, p] = await Promise.all([
          API.get("/api/courses"),
          API.get("/api/my-courses"),
          API.get("/api/student/progress"),
        ]);

        setCourses(c.data.courses);
        setMine(m.data.courses);
        setProgress(p.data.progress);
      }
    } catch (e) {
      setError(
        e.response?.data?.detail || "Unable to load LearnTrack data."
      );
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function openCourse(course) {
    setSelected(course);
    setActiveLesson(null);
    setQuiz(null);

    try {
      const r = await API.get(`/api/courses/${course.id}`);

      if (isAdmin) {
        setLessons(r.data.lessons);
      } else {
        const mineCourse = mine.find(
          (x) => x.course.id === course.id
        );

        if (mineCourse) {
          const lr = await API.get(
            `/api/courses/${course.id}/lessons`
          );
          setLessons(lr.data.lessons);
        } else {
          setLessons(r.data.lessons);
        }
      }

      setTab("course");
    } catch (e) {
      setError(e.response?.data?.detail || "Could not open course.");
    }
  }

  async function enroll(courseId) {
    setBusy(true);
    setNotice("");
    setError("");

    try {
      const r = await API.post(`/api/courses/${courseId}/enroll`);
      setNotice(r.data.message);
      await load();
    } catch (e) {
      setError(e.response?.data?.detail || "Enrollment failed.");
    } finally {
      setBusy(false);
    }
  }

  async function createCourse(e) {
    e.preventDefault();
    setBusy(true);

    try {
      await API.post("/api/admin/courses", courseForm);

      setCourseForm({
        title: "",
        description: "",
        category: "",
        level: "Beginner",
        published: true,
      });

      setNotice("Course created.");
      await load();
    } catch (e) {
      setError(e.response?.data?.detail || "Could not create course.");
    } finally {
      setBusy(false);
    }
  }

  async function addLesson(e) {
    e.preventDefault();

    if (!selected) return;

    setBusy(true);

    try {
      await API.post(
        `/api/admin/courses/${selected.id}/lessons`,
        lessonForm
      );

      setNotice("Lesson added.");

      setLessonForm({
        title: "",
        content: "",
        order: lessons.length + 2,
        video_url: "",
      });

      await openCourse(selected);
    } catch (e) {
      setError(e.response?.data?.detail || "Could not add lesson.");
    } finally {
      setBusy(false);
    }
  }

  async function lessonAction(lesson, action) {
    setError("");
    setNotice("");

    try {
      if (action === "start") {
        const r = await API.post(`/api/lessons/${lesson.id}/start`);
        setActiveLesson({ ...lesson, state: r.data.state });
      }

      if (action === "complete") {
        const r = await API.post(
          `/api/lessons/${lesson.id}/complete`
        );
        setNotice(r.data.message);
        await refreshLessons();
      }

      if (action === "quiz") {
        const r = await API.get(
          `/api/lessons/${lesson.id}/quiz`
        );
        setQuiz(r.data.quiz);
        setActiveLesson(lesson);
        setAnswers([]);
      }
    } catch (e) {
      setError(e.response?.data?.detail || "Action failed.");
    }
  }

  async function refreshLessons() {
    const r = await API.get(
      `/api/courses/${selected.id}/lessons`
    );
    setLessons(r.data.lessons);
  }

  async function submitQuiz(e) {
    e.preventDefault();

    try {
      const r = await API.post(
        `/api/lessons/${activeLesson.id}/quiz/submit`,
        { answers }
      );

      setNotice(
        `Your score: ${r.data.score}%. ${r.data.message}`
      );

      setQuiz(null);
      await refreshLessons();
      await load();
    } catch (e) {
      setError(
        e.response?.data?.detail || "Quiz submission failed."
      );
    }
  }

  async function saveQuiz(e) {
    e.preventDefault();

    try {
      const questions = JSON.parse(quizForm.questions);

      await API.post(
        `/api/admin/lessons/${quizForm.lesson_id}/quiz`,
        {
          title: quizForm.title,
          pass_mark: Number(quizForm.pass_mark),
          questions,
        }
      );

      setNotice("Quiz saved for the selected lesson.");
    } catch (e) {
      setError(
        e.response?.data?.detail ||
          (e instanceof SyntaxError
            ? "Questions must be valid JSON."
            : "Could not save quiz.")
      );
    }
  }

  async function deleteCourse(id) {
    if (!window.confirm("Delete this course?")) return;

    try {
      await API.delete(`/api/admin/courses/${id}`);
      setNotice("Course deleted.");
      await load();
    } catch (e) {
      setError(e.response?.data?.detail || "Delete failed.");
    }
  }

  const enrolledIds = new Set(
    mine.map((x) => x.course.id)
  );

  const nav = isAdmin
    ? [
        ["overview", "Overview"],
        ["catalog", "Courses"],
        ["students", "Students"],
        ["monitor", "Progress Monitor"],
        ["dfa", "DFA Logs"],
      ]
    : [
        ["catalog", "Course catalogue"],
        ["mine", "My courses"],
        ["progress", "My progress"],
      ];

  return (
    <div className="dashboard-page">
      <header className="dashboard-nav">
        <div className="brand">
          <div className="brand-icon">L</div>
          <span>LearnTrack</span>
        </div>

        <div className="nav-user">
          <span>{user.name}</span>
          <span className="role-tag">{user.role}</span>
          <button className="logout-button" onClick={onLogout}>
            Logout
          </button>
        </div>
      </header>

      <div className="app-shell">
        <aside className="sidebar">
          <p className="eyebrow">LEARNING SPACE</p>

          {nav.map(([key, label]) => (
            <button
              key={key}
              className={
                tab === key ? "side-link active" : "side-link"
              }
              onClick={() => {
                setTab(key);
                setSelected(null);
                setQuiz(null);
              }}
            >
              {label}
            </button>
          ))}
        </aside>

        <main className="workspace">
          <div className="welcome-row">
            <div>
              <p className="eyebrow">
                {isAdmin ? "ADMIN CONSOLE" : "STUDENT WORKSPACE"}
              </p>

              <h1>Hello, {user.name.split(" ")[0]} 👋</h1>

              <p className="muted">
                {isAdmin
                  ? "Manage learning content and monitor activity."
                  : "Learn at your pace. Your progress is saved as you go."}
              </p>
            </div>

            <button className="outline-button" onClick={load}>
              ↻ Refresh
            </button>
          </div>

          {notice && (
            <div className="success-message">{notice}</div>
          )}

          {error && (
            <div className="error-message">{error}</div>
          )}

          {tab === "overview" && isAdmin && (
            <>
              <div className="stats-grid">
                {[
                  ["Students", overview.students],
                  ["Courses", overview.courses],
                  ["Enrollments", overview.enrollments],
                  ["Certificates", overview.certificates],
                ].map(([k, v]) => (
                  <div className="stat-card" key={k}>
                    <span>{k}</span>
                    <strong>{v ?? 0}</strong>
                  </div>
                ))}
              </div>

              <section className="panel">
                <h2>Create a course</h2>

                <form
                  className="stack-form"
                  onSubmit={createCourse}
                >
                  <input
                    required
                    placeholder="Course title"
                    value={courseForm.title}
                    onChange={(e) =>
                      setCourseForm({
                        ...courseForm,
                        title: e.target.value,
                      })
                    }
                  />

                  <textarea
                    required
                    placeholder="Course description"
                    value={courseForm.description}
                    onChange={(e) =>
                      setCourseForm({
                        ...courseForm,
                        description: e.target.value,
                      })
                    }
                  />

                  <div className="form-row">
                    <input
                      placeholder="Category"
                      value={courseForm.category}
                      onChange={(e) =>
                        setCourseForm({
                          ...courseForm,
                          category: e.target.value,
                        })
                      }
                    />

                    <select
                      value={courseForm.level}
                      onChange={(e) =>
                        setCourseForm({
                          ...courseForm,
                          level: e.target.value,
                        })
                      }
                    >
                      <option>Beginner</option>
                      <option>Intermediate</option>
                      <option>Advanced</option>
                    </select>
                  </div>

                  <button
                    className="primary-button"
                    disabled={busy}
                  >
                    Create course
                  </button>
                </form>
              </section>
            </>
          )}

          {(tab === "catalog" || tab === "mine") && (
            <>
              <div className="section-heading">
                <h2>
                  {tab === "mine"
                    ? "My enrolled courses"
                    : "Explore courses"}
                </h2>

                <span className="muted">
                  {tab === "mine" ? mine.length : courses.length} courses
                </span>
              </div>

              <div className="course-grid">
                {(tab === "mine"
                  ? mine.map((x) => x.course)
                  : courses
                ).map((c) => (
                  <article className="course-card" key={c.id}>
                    <div className="course-art">LT</div>

                    <div className="course-body">
                      <span className="course-category">
                        {c.category || "GENERAL"} ·{" "}
                        {c.level || "Beginner"}
                      </span>

                      <h3>{c.title}</h3>
                      <p>{c.description}</p>

                      {tab === "mine" && (
                        <div className="progress-track">
                          <span
                            style={{
                              width: `${
                                mine.find(
                                  (x) => x.course.id === c.id
                                )?.progress || 0
                              }%`,
                            }}
                          />
                        </div>
                      )}

                      <div className="card-actions">
                        {tab === "mine" ? (
                          <button
                            className="primary-button"
                            onClick={() => openCourse(c)}
                          >
                            Continue learning
                          </button>
                        ) : (
                          <>
                            <button
                              className="outline-button"
                              onClick={() => openCourse(c)}
                            >
                              Details
                            </button>

                            {!isAdmin &&
                              !enrolledIds.has(c.id) && (
                                <button
                                  className="primary-button"
                                  disabled={busy}
                                  onClick={() => enroll(c.id)}
                                >
                                  Enroll
                                </button>
                              )}

                            {isAdmin && (
                              <button
                                className="danger-button"
                                onClick={() => deleteCourse(c.id)}
                              >
                                Delete
                              </button>
                            )}

                            {!isAdmin &&
                              enrolledIds.has(c.id) && (
                                <span className="state-pill">
                                  Enrolled
                                </span>
                              )}
                          </>
                        )}
                      </div>
                    </div>
                  </article>
                ))}
              </div>

              {courses.length === 0 && (
                <div className="empty-state">
                  No courses have been published yet.
                </div>
              )}
            </>
          )}

          {tab === "course" && selected && (
            <>
              <button
                className="text-button"
                onClick={() =>
                  setTab(
                    isAdmin
                      ? "catalog"
                      : enrolledIds.has(selected.id)
                        ? "mine"
                        : "catalog"
                  )
                }
              >
                ← Back to courses
              </button>

              <section className="panel course-detail">
                <span className="course-category">
                  {selected.category} · {selected.level}
                </span>

                <h2>{selected.title}</h2>
                <p>{selected.description}</p>

                {isAdmin ? (
                  <>
                    <h3>Lessons</h3>

                    {lessons.map((x) => (
                      <div className="lesson-row" key={x.id}>
                        <span>
                          {x.order}. {x.title}
                        </span>
                        <span className="state-pill">
                          Content ready
                        </span>
                      </div>
                    ))}

                    <h3>Add lesson</h3>

                    <form
                      className="stack-form"
                      onSubmit={addLesson}
                    >
                      <input
                        required
                        placeholder="Lesson title"
                        value={lessonForm.title}
                        onChange={(e) =>
                          setLessonForm({
                            ...lessonForm,
                            title: e.target.value,
                          })
                        }
                      />

                      <textarea
                        required
                        placeholder="Lesson content"
                        value={lessonForm.content}
                        onChange={(e) =>
                          setLessonForm({
                            ...lessonForm,
                            content: e.target.value,
                          })
                        }
                      />

                      <div className="form-row">
                        <input
                          type="number"
                          min="1"
                          required
                          value={lessonForm.order}
                          onChange={(e) =>
                            setLessonForm({
                              ...lessonForm,
                              order: Number(e.target.value),
                            })
                          }
                          placeholder="Order"
                        />

                        <input
                          placeholder="Optional video URL"
                          value={lessonForm.video_url}
                          onChange={(e) =>
                            setLessonForm({
                              ...lessonForm,
                              video_url: e.target.value,
                            })
                          }
                        />
                      </div>

                      <button className="primary-button">
                        Add lesson
                      </button>
                    </form>

                    <h3>Create or replace a lesson quiz</h3>

                    <form
                      className="stack-form"
                      onSubmit={saveQuiz}
                    >
                      <select
                        required
                        value={quizForm.lesson_id}
                        onChange={(e) =>
                          setQuizForm({
                            ...quizForm,
                            lesson_id: e.target.value,
                          })
                        }
                      >
                        <option value="">Choose lesson</option>
                        {lessons.map((l) => (
                          <option key={l.id} value={l.id}>
                            {l.order}. {l.title}
                          </option>
                        ))}
                      </select>

                      <input
                        required
                        placeholder="Quiz title"
                        value={quizForm.title}
                        onChange={(e) =>
                          setQuizForm({
                            ...quizForm,
                            title: e.target.value,
                          })
                        }
                      />

                      <input
                        type="number"
                        min="1"
                        max="100"
                        value={quizForm.pass_mark}
                        onChange={(e) =>
                          setQuizForm({
                            ...quizForm,
                            pass_mark: e.target.value,
                          })
                        }
                        placeholder="Pass mark %"
                      />

                      <textarea
                        rows="8"
                        value={quizForm.questions}
                        onChange={(e) =>
                          setQuizForm({
                            ...quizForm,
                            questions: e.target.value,
                          })
                        }
                      />

                      <small className="muted">
                        Questions JSON: each item needs question,
                        options array, answer_index (zero-based),
                        and optional explanation.
                      </small>

                      <button className="primary-button">
                        Save quiz
                      </button>
                    </form>
                  </>
                ) : !enrolledIds.has(selected.id) ? (
                  <button
                    className="primary-button"
                    onClick={() => enroll(selected.id)}
                  >
                    Enroll in this course
                  </button>
                ) : (
                  <>
                    <h3>Course lessons</h3>

                    {lessons.map(({ lesson, state }) => (
                      <div className="lesson-row" key={lesson.id}>
                        <div>
                          <strong>
                            {lesson.order}. {lesson.title}
                          </strong>
                          <small>
                            {state.replaceAll("_", " ")}
                          </small>
                        </div>

                        <div className="lesson-actions">
                          {state === "UNLOCKED" ||
                          state === "IN_PROGRESS" ? (
                            <button
                              className="outline-button"
                              onClick={() =>
                                lessonAction(lesson, "start")
                              }
                            >
                              Open
                            </button>
                          ) : null}

                          {state === "IN_PROGRESS" ? (
                            <button
                              className="primary-button"
                              onClick={() =>
                                lessonAction(lesson, "complete")
                              }
                            >
                              Mark complete
                            </button>
                          ) : null}

                          {state === "COMPLETED" ? (
                            <button
                              className="primary-button"
                              onClick={() =>
                                lessonAction(lesson, "quiz")
                              }
                            >
                              Take quiz
                            </button>
                          ) : null}

                          {state === "QUIZ_PASSED" ? (
                            <span className="state-pill">
                              Passed ✓
                            </span>
                          ) : null}

                          {state === "LOCKED" ? (
                            <span className="muted">Locked</span>
                          ) : null}
                        </div>
                      </div>
                    ))}

                    {activeLesson && !quiz && (
                      <div className="lesson-content">
                        <h3>{activeLesson.title}</h3>
                        <p>{activeLesson.content}</p>

                        {activeLesson.video_url && (
                          <a
                            href={activeLesson.video_url}
                            target="_blank"
                            rel="noreferrer"
                          >
                            Open lesson video ↗
                          </a>
                        )}
                      </div>
                    )}
                  </>
                )}
              </section>
            </>
          )}

          {tab === "progress" && !isAdmin && (
            <section className="panel">
              <h2>Learning progress</h2>

              {progress.map((p) => (
                <div className="progress-item" key={p.course}>
                  <div>
                    <strong>{p.course}</strong>
                    <span>
                      {p.completed}/{p.total} lessons passed ·{" "}
                      {p.percent}%
                    </span>
                  </div>

                  <div className="progress-track">
                    <span
                      style={{ width: `${p.percent}%` }}
                    />
                  </div>
                </div>
              ))}
            </section>
          )}

          {tab === "students" && isAdmin && (
            <section className="panel">
              <h2>Registered students</h2>

              {students.map((s) => (
                <div className="lesson-row" key={s.id}>
                  <div>
                    <strong>{s.name}</strong>
                    <small>{s.email}</small>
                  </div>
                  <span className="state-pill">Student</span>
                </div>
              ))}
            </section>
          )}

          {tab === "monitor" && isAdmin && (
            <section className="panel">
              <div className="section-heading">
                <h2>Student progress monitoring</h2>
                <span className="muted">
                  {progress.length} active enrolments
                </span>
              </div>

              {progress.length ? (
                progress.map((p, i) => (
                  <div
                    className="progress-item"
                    key={`${p.student_id}-${p.course_id}-${i}`}
                  >
                    <div>
                      <strong>
                        {p.student_name} · {p.course_title}
                      </strong>
                      <span>
                        {p.completed_lessons}/{p.total_lessons} lessons
                        passed · {p.percent}%
                      </span>
                    </div>

                    <p className="muted">{p.student_email}</p>

                    <div className="progress-track">
                      <span
                        style={{ width: `${p.percent}%` }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  No student enrolments to monitor yet.
                </div>
              )}
            </section>
          )}

          {tab === "dfa" && isAdmin && (
            <section className="panel">
              <h2>Finite automata transition history</h2>

              <p className="muted">
                Latest 100 validated state transitions. The diagrams
                show the accepted workflow states.
              </p>

              <div className="dfa-diagrams">
                <div className="dfa-card">
                  <h3>Course enrolment DFA</h3>
                  <div className="dfa-flow">
                    <span>NOT ENROLLED</span>
                    <b>→</b>
                    <span>REQUESTED</span>
                    <b>→</b>
                    <span>ENROLLED</span>
                  </div>
                  <small>REQUEST · APPROVE</small>
                </div>

                <div className="dfa-card">
                  <h3>Lesson completion DFA</h3>
                  <div className="dfa-flow">
                    <span>LOCKED</span>
                    <b>→</b>
                    <span>UNLOCKED</span>
                    <b>→</b>
                    <span>IN PROGRESS</span>
                    <b>→</b>
                    <span>COMPLETED</span>
                    <b>→</b>
                    <span>QUIZ PASSED</span>
                  </div>
                  <small>
                    UNLOCK · START · COMPLETE · PASS QUIZ
                  </small>
                </div>
              </div>

              {logs.map((log) => (
                <div className="lesson-row" key={log.id}>
                  <div>
                    <strong>
                      {log.entity}: {log.from_state} → {log.to_state}
                    </strong>
                    <small>
                      Action: {log.action} · User: {log.user_id}
                    </small>
                  </div>

                  <span className="state-pill">
                    {new Date(log.created_at).toLocaleString()}
                  </span>
                </div>
              ))}
            </section>
          )}

          {quiz && activeLesson && (
            <div className="modal-backdrop">
              <form className="quiz-modal" onSubmit={submitQuiz}>
                <button
                  type="button"
                  className="modal-close"
                  onClick={() => setQuiz(null)}
                >
                  ×
                </button>

                <p className="eyebrow">KNOWLEDGE CHECK</p>
                <h2>{quiz.title}</h2>
                <p className="muted">
                  Pass mark: {quiz.pass_mark}%
                </p>

                {quiz.questions.map((q, i) => (
                  <fieldset key={i}>
                    <legend>
                      {i + 1}. {q.question}
                    </legend>

                    {q.options.map((o, j) => (
                      <label className="option" key={j}>
                        <input
                          type="radio"
                          name={`q${i}`}
                          checked={answers[i] === j}
                          onChange={() =>
                            setAnswers((a) => {
                              const b = [...a];
                              b[i] = j;
                              return b;
                            })
                          }
                          required
                        />
                        {o}
                      </label>
                    ))}
                  </fieldset>
                ))}

                <button className="primary-button">
                  Submit answers
                </button>
              </form>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default Dashboard;
