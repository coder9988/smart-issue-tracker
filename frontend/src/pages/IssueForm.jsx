import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api";
import { getUser } from "../auth";

const defaultForm = {
  title: "",
  description: "",
  category: "bug",
  priority: "medium",
  status: "open",
  assignee_id: "",
};

export default function IssueForm({ editMode }) {
  const [form, setForm] = useState(defaultForm);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [developers, setDevelopers] = useState([]);
  const user = getUser();
  const { id } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    api.get("users/", { params: { role: "developer" } }).then((resp) => {
      setDevelopers(resp.data.results || resp.data);
    });
  }, []);

  useEffect(() => {
    if (editMode && id) {
      api.get(`issues/${id}/`).then((resp) => {
        setForm({
          title: resp.data.title,
          description: resp.data.description,
          category: resp.data.category,
          priority: resp.data.priority,
          status: resp.data.status,
          assignee_id: resp.data.assignee?.id || "",
        });
      });
    }
  }, [editMode, id]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    try {
      if (editMode && id) {
        const payload = { ...form };
        if (user?.role === "reporter") delete payload.assignee_id;
        if (!payload.assignee_id) delete payload.assignee_id;
        await api.put(`issues/${id}/`, payload);
        setSuccess("Issue updated successfully.");
      } else {
        const payload = { ...form, status: "open" };
        if (user?.role === "reporter") delete payload.assignee_id;
        if (!payload.assignee_id) delete payload.assignee_id;
        await api.post("issues/", payload);
        setSuccess("Issue created successfully.");
      }
      setTimeout(() => navigate("/issues"), 700);
    } catch (err) {
      setError("Unable to save issue. Check required fields and try again.");
    }
  };

  return (
    <div className="page-container">
      <div className="card">
        <h2>{editMode ? "Edit Issue" : "Create Issue"}</h2>
        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            Title
            <input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              required
            />
          </label>
          <label>
            Description
            <textarea
              value={form.description}
              onChange={(e) =>
                setForm({ ...form, description: e.target.value })
              }
            />
          </label>
          <label>
            Category
            <select
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
            >
              <option value="bug">Bug</option>
              <option value="feature">Feature</option>
              <option value="task">Task</option>
              <option value="other">Other</option>
            </select>
          </label>
          <label>
            Priority
            <select
              value={form.priority}
              onChange={(e) => setForm({ ...form, priority: e.target.value })}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
          {editMode && <label>
            Status
            <select
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value })}
            >
              <option value="open">Open</option>
              <option value="assigned">Assigned</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
              <option value="reopened">Reopened</option>
            </select>
          </label>}
          {user?.role !== "reporter" && <label>
            Assignee
            <select
              value={form.assignee_id}
              onChange={(e) =>
                setForm({ ...form, assignee_id: e.target.value })
              }
            >
              <option value="">Unassigned</option>
              {developers.map((dev) => (
                <option key={dev.id} value={dev.id}>
                  {dev.username}
                </option>
              ))}
            </select>
          </label>}
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}
          <button type="submit">
            {editMode ? "Update Issue" : "Create Issue"}
          </button>
        </form>
      </div>
    </div>
  );
}
