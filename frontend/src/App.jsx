import { useCallback, useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api";
const TOKEN_KEY = "claimflow_token";

function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem(TOKEN_KEY));
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [claims, setClaims] = useState([]);
  const [message, setMessage] = useState("");

  const logout = useCallback(() => {
    sessionStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setClaims([]);
  }, []);

  const loadClaims = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/claims/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.status === 401) {
        logout();
        return;
      }
      setClaims(await response.json());
    } catch {
      setMessage("Unable to reach the server.");
    }
  }, [token, logout]);

  useEffect(() => {
    if (token) {
      loadClaims();
    }
  }, [token, loadClaims]);

  const handleLogin = async (event) => {
    event.preventDefault();
    setError("");
    try {
      const response = await fetch(`${API_URL}/auth/token/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!response.ok) {
        setError("Invalid username or password.");
        return;
      }
      const data = await response.json();
      sessionStorage.setItem(TOKEN_KEY, data.access);
      setToken(data.access);
      setPassword("");
    } catch {
      setError("Unable to reach the server.");
    }
  };

  const checkStatus = async (claim) => {
    setMessage("");
    try {
      const response = await fetch(`${API_URL}/claims/${claim.id}/check-status/`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        setMessage(`Status check queued for ${claim.claim_number}. Check the bot logs for the result.`);
      } else {
        setMessage(`Could not queue the status check for ${claim.claim_number}.`);
      }
    } catch {
      setMessage("Unable to reach the server.");
    }
  };

  if (!token) {
    return (
      <div className="page">
        <form className="card login" onSubmit={handleLogin}>
          <h1>ClaimFlow</h1>
          <p className="subtitle">Healthcare Claims Automation</p>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            required
          />
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
          {error && <p className="error">{error}</p>}
          <button type="submit">Sign In</button>
        </form>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="card wide">
        <div className="header">
          <h1>Claims</h1>
          <div className="actions">
            <button className="secondary" onClick={loadClaims}>Refresh</button>
            <button className="secondary" onClick={logout}>Sign Out</button>
          </div>
        </div>
        {message && <p className="notice">{message}</p>}
        <table>
          <thead>
            <tr>
              <th>Claim</th>
              <th>Patient</th>
              <th>Insurer</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Bot</th>
            </tr>
          </thead>
          <tbody>
            {claims.map((claim) => (
              <tr key={claim.id}>
                <td>{claim.claim_number}</td>
                <td>{claim.patient_name}</td>
                <td>{claim.insurer}</td>
                <td>{claim.amount}</td>
                <td>
                  <span className={`badge ${claim.status}`}>{claim.status}</span>
                </td>
                <td>
                  <button onClick={() => checkStatus(claim)}>Check Status</button>
                </td>
              </tr>
            ))}
            {claims.length === 0 && (
              <tr>
                <td colSpan="6">No claims found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;