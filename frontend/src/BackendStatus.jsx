
import { useEffect, useState } from "react";
import API from "./services/api";

function BackendStatus() {
  const [status, setStatus] = useState("Checking connection...");

  useEffect(() => {
    API.get("/api/health")
      .then((response) => {
        setStatus(`Connected! Backend says: ${response.data.status}`);
      })
      .catch((error) => {
        console.error(error);
        setStatus("Backend connection failed!");
      });
  }, []);

  return (
    <div>
      <h2>Backend Connection</h2>
      <p>{status}</p>
    </div>
  );
}

export default BackendStatus;
