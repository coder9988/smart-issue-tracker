import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import api from "../api";

const workflow = ["open", "assigned", "in_progress", "resolved", "closed", "reopened"];

export default function IssueDetail() {
  const [issue, setIssue] = useState(null);
  const [comment, setComment] = useState("");
  const [error, setError] = useState(null);
  const { id } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    api.get(`issues/${id}/`).then((resp) => setIssue(resp.data));
  }, [id]);

  const handleDelete = async () => {
    try {
      await api.delete(`issues/${id}/`);
      navigate("/issues");
    } catch (err) {
      setError("Unable to delete issue.");
    }
  };

  const handleComment = async (event) => {
    event.preventDefault();
    setError(null);
    try {
      await api.post("comments/", { issue: id, body: comment });
      const resp = await api.get(`issues/${id}/`);
      setIssue(resp.data);
      setComment("");
    } catch (err) {
      setError("Unable to post comment.");
    }
  };

  if (!issue) {
    return (
      <div className="page-container">
        <p>Loading issue...</p>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="card">
        <h2>{issue.title}</h2>
        <p>{issue.description}</p>
        <div className="detail-grid">
          <div>
            <strong>Status:</strong>{" "}
            <span className={`status-pill status-${issue.status}`}>
              {issue.status.replace("_", " ")}
            </span>
          </div>
          <div>
            <strong>Category:</strong> {issue.category}
          </div>
          <div>
            <strong>Priority:</strong> {issue.priority}
          </div>
          <div>
            <strong>Reporter:</strong> {issue.reporter?.username}
          </div>
          <div>
            <strong>Assignee:</strong>{" "}
            {issue.assignee?.username || "Unassigned"}
          </div>
          <div>
            <strong>Updated:</strong>{" "}
            {new Date(issue.updated_at).toLocaleString()}
          </div>
        </div>
        <div className="action-row">
          <Link to={`/issues/${id}/edit`} className="button-secondary">
            Edit
          </Link>
          <button className="button-danger" onClick={handleDelete}>
            Delete
          </button>
        </div>
      </div>

      <div className="panel">
        <h3>Workflow</h3>
        <div className="workflow-row">
          {workflow.map((status) => (
            <span
              key={status}
              className={`workflow-step ${issue.status === status ? "active" : ""}`}
            >
              {status.replace("_", " ")}
            </span>
          ))}
        </div>
      </div>

      <div className="card">
        <h3>Comments</h3>
        {issue.comments.length ? (
          issue.comments.map((commentItem) => (
            <div key={commentItem.id} className="comment-card">
              <div className="comment-author">
                {commentItem.author.username}
              </div>
              <p>{commentItem.body}</p>
            </div>
          ))
        ) : (
          <p>No comments yet.</p>
        )}
        <form onSubmit={handleComment} className="comment-form">
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Add a comment"
            required
          />
          <button type="submit">Post Comment</button>
        </form>
        {error && <div className="error-message">{error}</div>}
      </div>
    </div>
  );
}
