import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";

export default function IssueList() {
  const [issues, setIssues] = useState([]);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState({ status: "", category: "" });

  const loadIssues = async () => {
    const params = {};
    if (query) params.search = query;
    if (filter.status) params.status = filter.status;
    if (filter.category) params.category = filter.category;
    const resp = await api.get("issues/", { params });
    setIssues(resp.data.results || resp.data);
  };

  useEffect(() => {
    loadIssues();
  }, []);

  return (
    <div className="page-container">
      <div className="list-header">
        <h2>Issues</h2>
        <div className="search-filter-row">
          <input
            value={query}
            placeholder="Search issues"
            onChange={(e) => setQuery(e.target.value)}
          />
          <select
            value={filter.status}
            onChange={(e) => setFilter({ ...filter, status: e.target.value })}
          >
            <option value="">All statuses</option>
            <option value="open">Open</option>
            <option value="assigned">Assigned</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
            <option value="reopened">Reopened</option>
          </select>
          <select
            value={filter.category}
            onChange={(e) => setFilter({ ...filter, category: e.target.value })}
          >
            <option value="">All categories</option>
            <option value="bug">Bug</option>
            <option value="feature">Feature</option>
            <option value="task">Task</option>
            <option value="other">Other</option>
          </select>
          <button onClick={loadIssues}>Search</button>
        </div>
      </div>
      <div className="table-card">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Status</th>
              <th>Category</th>
              <th>Priority</th>
              <th>Reporter</th>
              <th>Assignee</th>
            </tr>
          </thead>
          <tbody>
            {issues.map((issue) => (
              <tr key={issue.id}>
                <td>
                  <Link to={`/issues/${issue.id}`}>{issue.title}</Link>
                </td>
                <td><span className={`status-pill status-${issue.status}`}>{issue.status.replace("_", " ")}</span></td>
                <td>{issue.category}</td>
                <td>{issue.priority}</td>
                <td>{issue.reporter?.username}</td>
                <td>{issue.assignee?.username || "Unassigned"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
