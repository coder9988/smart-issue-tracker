import { Routes, Route, Link, useNavigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import IssueList from "./pages/IssueList";
import IssueForm from "./pages/IssueForm";
import IssueDetail from "./pages/IssueDetail";
import ProtectedRoute from "./components/ProtectedRoute";
import { logout, getToken, getUser } from "./auth";

const roleDashboard = {
  admin: "/admin/dashboard",
  developer: "/developer/dashboard",
  reporter: "/reporter/dashboard",
};

function App() {
  const navigate = useNavigate();
  const token = getToken();
  const user = getUser();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="app-shell">
      {token && <header className="app-header">
        <div>
          <Link to={roleDashboard[user?.role] || "/dashboard"} className="brand">
            Smart Issue Tracker
          </Link>
        </div>
        <nav>
          <Link to={roleDashboard[user?.role] || "/dashboard"}>Dashboard</Link>
          <Link to="/issues">Issues</Link>
          {user?.role !== "developer" && <Link to="/issues/new">New Issue</Link>}
          {user?.role === "admin" && <Link to="/admin/dashboard">Admin</Link>}
          <div className="user-menu">
            <span className="role-badge">{user?.role || "user"}</span>
            <span>{user?.username || "User"}</span>
          </div>
          <button className="link-button" onClick={handleLogout}>
            Logout
          </button>
        </nav>
      </header>}
      <main>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/dashboard"
            element={
              <ProtectedRoute roles={["admin"]}>
                <Dashboard role="admin" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/developer/dashboard"
            element={
              <ProtectedRoute roles={["developer"]}>
                <Dashboard role="developer" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reporter/dashboard"
            element={
              <ProtectedRoute roles={["reporter"]}>
                <Dashboard role="reporter" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/issues"
            element={
              <ProtectedRoute>
                <IssueList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/issues/new"
            element={
              <ProtectedRoute>
                <IssueForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/issues/:id"
            element={
              <ProtectedRoute>
                <IssueDetail />
              </ProtectedRoute>
            }
          />
          <Route
            path="/issues/:id/edit"
            element={
              <ProtectedRoute>
                <IssueForm editMode />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;
