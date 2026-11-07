import { Navigate, NavLink, Outlet, Route, Routes } from "react-router-dom";
import ChatWidget from "./components/ChatWidget";
import AdminDashboard from "./components/AdminDashboard";
import LoginPage from "./pages/LoginPage";
import NotFound from "./pages/NotFound";

const navClass = ({ isActive }: { isActive: boolean }) =>
  `tab-button ${isActive ? "active" : ""}`;

function Layout() {
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
          <NavLink to="/login" className={navClass}>
            Login
          </NavLink>
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
        <Route path="admin" element={<AdminDashboard />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
