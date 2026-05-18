import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import { getUser } from "../auth";
import StatsChart from "../components/StatsChart";

const titles = {
  admin: "Admin Dashboard",
  developer: "Developer Dashboard",
  reporter: "Reporter Dashboard",
};

function MetricCard({ label, value, hint }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      {hint && <small>{hint}</small>}
    </div>
  );
}

function RecentIssues({ issues = [], title = "Recent Issues" }) {
  return (
    <div className="panel">
      <div className="panel-header">
        <h3>{title}</h3>
        <Link to="/issues">View all</Link>
      </div>
      <div className="compact-list">
        {issues.length ? issues.map((issue) => (
          <Link key={issue.id} to={`/issues/${issue.id}`} className="compact-row">
            <span>{issue.title}</span>
            <em>{issue.status.replace("_", " ")}</em>
          </Link>
        )) : <p>No recent issues.</p>}
      </div>
    </div>
  );
}

function RootCausePanel({ data }) {
  return (
    <div className="panel">
      <div className="panel-header">
        <h3>Rule-Based Analytical Insights</h3>
      </div>
      {!data ? (
        <p>Loading analysis...</p>
      ) : (
        <div className="insight-grid">
          <MetricCard label="Reopened Issues" value={data.reopened_count || 0} />
          <MetricCard label="Avg Resolution" value={`${data.avg_resolution_hours || 0}h`} />
          <div className="insight-copy">
            {(data.notes?.length ? data.notes : ["No recurring pattern detected yet."]).map((note) => (
              <p key={note}>{note}</p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function Dashboard({ role }) {
  const [stats, setStats] = useState(null);
  const [rootCause, setRootCause] = useState(null);
  const currentRole = role || getUser()?.role || "reporter";

  useEffect(() => {
    api.get("issues/dashboard/").then((resp) => setStats(resp.data));
    api.get("issues/root_cause/").then((resp) => setRootCause(resp.data));
  }, []);

  return (
    <div className="page-container dashboard-page">
      <div className="page-title-row">
        <div>
          <p className="eyebrow">{currentRole}</p>
          <h2>{titles[currentRole] || "Dashboard"}</h2>
        </div>
        <Link className="button-secondary" to="/issues">
          Open Issue Queue
        </Link>
      </div>

      <div className="metrics-grid">
        <MetricCard label="Total Issues" value={stats?.total ?? "..."} />
        {currentRole === "admin" && <MetricCard label="Critical Issues" value={stats?.critical ?? "..."} />}
        {currentRole === "admin" && <MetricCard label="Reopened" value={stats?.reopened ?? "..."} />}
        {currentRole === "developer" && <MetricCard label="Assigned Issues" value={stats?.total ?? "..."} />}
        {currentRole === "developer" && <MetricCard label="In Progress" value={stats?.in_progress ?? "..."} />}
        {currentRole === "reporter" && <MetricCard label="Reported By You" value={stats?.total ?? "..."} />}
        {currentRole === "reporter" && <MetricCard label="Resolved" value={stats?.resolved ?? "..."} />}
        <MetricCard label="Open" value={stats?.open ?? "..."} />
        <MetricCard label="Closed" value={stats?.closed ?? "..."} />
        <MetricCard label="Avg Resolution" value={`${stats?.avg_resolution_hours ?? 0}h`} />
      </div>

      <div className="dashboard-grid">
        <div className="panel">
          <h3>Workflow Status</h3>
          <StatsChart title="" data={stats?.by_status || []} />
        </div>
        <div className="panel">
          <h3>Priority Overview</h3>
          <StatsChart title="" data={stats?.by_priority || []} />
        </div>
        {currentRole === "admin" && (
          <div className="panel">
            <h3>Developer Workload</h3>
            <StatsChart title="" data={stats?.developer_workload || []} />
          </div>
        )}
        <RootCausePanel data={rootCause} />
        <RecentIssues
          issues={stats?.recent_issues || []}
          title={currentRole === "reporter" ? "Your Recent Updates" : "Recent Work Items"}
        />
        <div className="panel">
          <div className="panel-header">
            <h3>{currentRole === "admin" ? "User Management" : "Recent Comments"}</h3>
            {currentRole === "admin" && <Link to="/issues/new">Create issue</Link>}
          </div>
          {currentRole === "admin" ? (
            <p>Use assignment controls in issue detail or edit screens to route work to developers.</p>
          ) : (
            <div className="compact-list">
              {stats?.recent_comments?.length ? stats.recent_comments.map((comment) => (
                <div key={comment.id} className="compact-row static">
                  <span>{comment.body}</span>
                  <em>{comment.author?.username}</em>
                </div>
              )) : <p>No recent comments.</p>}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
