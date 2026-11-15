
import { useEffect, useState } from "react";
import API from "./services/api";
import SecPage from "./pages/SecPage";
import Dashboard from "./pages/Dashboard";
import "./App.css";

function App() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("learntrack_token");

    if (!token) {
      setChecking(false);
      return;
    }

    API.get("/api/auth/me")
      .then((response) => {
        setUser(response.data.user);
      })
      .catch(() => {
        localStorage.removeItem("learntrack_token");
        localStorage.removeItem("learntrack_user");
      })
      .finally(() => {
        setChecking(false);
      });
  }, []);

  function handleLogout() {
    localStorage.removeItem("learntrack_token");
    localStorage.removeItem("learntrack_user");
    setUser(null);
  }

  if (checking) {
    return <div className="loading-screen">Loading LearnTrack...</div>;
  }

  return user ? (
    <Dashboard user={user} onLogout={handleLogout} />
  ) : (
    <SecPage onAuth={setUser} />
  );
}

export default App;
