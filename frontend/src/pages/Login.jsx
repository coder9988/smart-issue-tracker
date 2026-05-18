import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import { saveAuth } from "../auth";

const roleDashboard = {
  admin: "/admin/dashboard",
  developer: "/developer/dashboard",
  reporter: "/reporter/dashboard",
};

export default function Login() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await api.post("token/", form);
      const { access, refresh, user } = response.data;
      saveAuth({ access, refresh, user });
      navigate(roleDashboard[user?.role] || "/reporter/dashboard");
    } catch (err) {
      setError("Login failed. Check credentials.");
    }
  };

  return (
    <div className="auth-wrapper">
      <section className="auth-left-panel">
        <div className="brand-mark">SIT</div>
        <div>
          <p className="eyebrow">Engineering workflow platform</p>
          <h1>Smart Issue Tracker</h1>
          <p className="auth-subtitle">
            AI-powered issue workflow and root cause analysis platform
          </p>
        </div>
        <div className="feature-list">
          <span>Track issues</span>
          <span>Assign developers</span>
          <span>Monitor workflows</span>
          <span>Analyze recurring problems</span>
        </div>
        <div className="mock-stats-grid">
          <div>
            <strong>248</strong>
            <span>Issues Resolved</span>
          </div>
          <div>
            <strong>18h</strong>
            <span>Avg Resolution Time</span>
          </div>
          <div>
            <strong>7</strong>
            <span>Open Critical Bugs</span>
          </div>
          <div>
            <strong>92%</strong>
            <span>Developer Productivity</span>
          </div>
        </div>
      </section>
      <section className="auth-right-panel">
        <div className="auth-card">
          <p className="eyebrow">Welcome back</p>
          <h2>Sign in to your workspace</h2>
          <form onSubmit={handleSubmit}>
            <label>
              Username
              <input
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                required
              />
            </label>
            <label>
              Password
              <input
                type="password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
              />
            </label>
            {error && <div className="error-message">{error}</div>}
            <button type="submit">Sign in</button>
          </form>
        </div>
      </section>
    </div>
  );
}
