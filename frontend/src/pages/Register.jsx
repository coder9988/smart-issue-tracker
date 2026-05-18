import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

export default function Register() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    role: "reporter",
  });
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await api.post("register/register/", form);
      setSuccess("Registration successful. Please login.");
      setError(null);
      setTimeout(() => navigate("/login"), 800);
    } catch (err) {
      setSuccess(null);
      const responseData = err?.response?.data;
      let message = "Registration failed. Check your submission.";
      if (responseData) {
        if (typeof responseData === "string") {
          message = responseData;
        } else if (responseData.non_field_errors) {
          message = responseData.non_field_errors.join(" ");
        } else {
          message = Object.entries(responseData)
            .map(
              ([key, value]) =>
                `${key}: ${Array.isArray(value) ? value.join(" ") : value}`,
            )
            .join(" ");
        }
      }
      setError(message);
    }
  };

  return (
    <div className="auth-card">
      <h2>Register</h2>
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
          Email
          <input
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
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
        <label>
          Role
          <select
            value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}
          >
            <option value="reporter">Reporter</option>
            <option value="developer">Developer</option>
          </select>
        </label>
        {success && <div className="success-message">{success}</div>}
        {error && <div className="error-message">{error}</div>}
        <button type="submit">Create account</button>
      </form>
    </div>
  );
}
