import { Navigate } from "react-router-dom";
import { getToken, getUser } from "../auth";

export default function ProtectedRoute({ children, roles }) {
  const token = getToken();
  const user = getUser();
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  if (roles?.length && !roles.includes(user?.role)) {
    return <Navigate to={`/${user?.role || "reporter"}/dashboard`} replace />;
  }
  return children;
}
