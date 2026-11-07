import { Navigate, NavLink, Outlet, Route, Routes } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "./hooks";
import { loggedOut } from "./features/auth/authSlice";
import { backendApi } from "./services/backendApi";
import ChatWidget from "./components/ChatWidget";
import AdminDashboard from "./components/AdminDashboard";
import LoginPage from "./pages/LoginPage";
import NotFound from "./pages/NotFound";
import RequireAdmin from "./features/auth/RequireAdmin";

const navClass = ({ isActive }: { isActive: boolean }) =>
  `tab-button ${isActive ? "active" : ""}`;

function Layout() {
  const token = useAppSelector((s) => s.auth.token);
  const dispatch = useAppDispatch();

  function logout() {
    dispatch(loggedOut());
    dispatch(backendApi.util.resetApiState()); // drop cached /auth/me and orders
  }

  return (
    <div className="app-shell">
      <div className="app-header">
        <div>
          <h1>Nordic Cart Support Agent</h1>
          <div className="subtitle">
            LangGraph order lookup &amp; return agent -- Finland 14-day policy
            demo
          </div>
        </div>
        <nav className="tabs">
          <NavLink to="/chat" className={navClass}>
            Customer chat
          </NavLink>
          <NavLink to="/admin" className={navClass}>
            Admin dashboard
          </NavLink>
          {token ? (
            <button className="tab-button" onClick={logout}>
              Logout
            </button>
          ) : (
            <NavLink to="/login" className={navClass}>
              Login
            </NavLink>
          )}
        </nav>
      </div>
      <Outlet />
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/chat" replace />} />
        <Route path="chat" element={<ChatWidget />} />
        <Route element={<RequireAdmin />}>
          <Route path="admin" element={<AdminDashboard />} />
        </Route>
        <Route path="login" element={<LoginPage />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
