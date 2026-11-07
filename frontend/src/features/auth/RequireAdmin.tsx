import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAppSelector } from "../../hooks";
import { useMeQuery } from "../../services/backendApi";

export default function RequireAdmin() {
  const token = useAppSelector((s) => s.auth.token);
  const location = useLocation();
  // Skip the request entirely when there is no token.
  const {
    data: me,
    isLoading,
    isError,
  } = useMeQuery(undefined, { skip: !token });

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  if (isError) {
    return (
      <div className="card">Cannot reach the server. Try again later.</div>
    );
  }
  if (isLoading || !me) {
    return <div className="card">Checking session…</div>;
  }
  if (me.role !== "admin") {
    return (
      <div className="card">Admins only. You are signed in as a customer.</div>
    );
  }
  return <Outlet />;
}
