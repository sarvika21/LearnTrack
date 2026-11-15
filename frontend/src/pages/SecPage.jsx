import { useState } from "react";
import API from "../services/api";

function SecPage({ onAuth }) {
  const [mode, setMode] = useState("login");
  const [role, setRole] = useState("student");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const isRegister = mode === "register";

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const endpoint = isRegister
        ? "/api/auth/register"
        : "/api/auth/login";

      const payload = isRegister
        ? { name, email, password }
        : { email, password };

      const response = await API.post(endpoint, payload);
      const data = response.data;

      if (!isRegister && data.user.role !== role) {
        setError(`This account is not registered as ${role}.`);
        setLoading(false);
        return;
      }

      localStorage.setItem("learntrack_token", data.access_token);
      localStorage.setItem("learntrack_user", JSON.stringify(data.user));

      onAuth(data.user);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="brand">
          <div className="brand-icon">L</div>
          <span>LearnTrack</span>
        </div>

        <div className="auth-heading">
          <p className="eyebrow">YOUR LEARNING JOURNEY STARTS HERE</p>
          <h1>{isRegister ? "Create your account" : "Welcome back"}</h1>
          <p>
            {isRegister
              ? "Join LearnTrack and start learning."
              : "Sign in to continue your learning journey."}
          </p>
        </div>

        {!isRegister && (
          <div className="role-switch">
            <button
              type="button"
              className={role === "student" ? "active" : ""}
              onClick={() => setRole("student")}
            >
              Student
            </button>
            <button
              type="button"
              className={role === "admin" ? "active" : ""}
              onClick={() => setRole("admin")}
            >
              Admin
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          {isRegister && (
            <label>
              Full name
              <input
                type="text"
                placeholder="Enter your full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                minLength={2}
                maxLength={80}
              />
            </label>
          )}

          <label>
            Email address
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>

          <label>
            Password
            <input
              type="password"
              placeholder="At least 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              maxLength={128}
            />
          </label>

          {error && <div className="error-message">{error}</div>}

          <button className="primary-button" disabled={loading}>
            {loading
              ? "Please wait..."
              : isRegister
                ? "Create Student Account"
                : "Sign In"}
          </button>
        </form>

        <div className="auth-footer">
          {isRegister ? "Already have an account?" : "New to LearnTrack?"}
          <button
            type="button"
            onClick={() => {
              setMode(isRegister ? "login" : "register");
              setError("");
            }}
          >
            {isRegister ? "Sign in" : "Create student account"}
          </button>
        </div>

        <p className="security-note">
          Secure access powered by LearnTrack authentication
        </p>
      </section>
    </main>
  );
}

export default SecPage;