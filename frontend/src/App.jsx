import React, { useState } from "react";
import ChatWidget from "./components/ChatWidget.jsx";
import AdminDashboard from "./components/AdminDashboard.jsx";

export default function App() {
  const [tab, setTab] = useState("chat");

  return (
    <div className="app-shell">
      <div className="app-header">
        <div>
          <h1>Nordic Cart Support Agent</h1>
          <div className="subtitle">LangGraph order lookup &amp; return agent -- Finland 14-day policy demo</div>
        </div>
        <div className="tabs">
          <button className={`tab-button ${tab === "chat" ? "active" : ""}`} onClick={() => setTab("chat")}>
            Customer chat
          </button>
          <button className={`tab-button ${tab === "admin" ? "active" : ""}`} onClick={() => setTab("admin")}>
            Admin dashboard
          </button>
        </div>
      </div>

      {tab === "chat" ? <ChatWidget /> : <AdminDashboard />}
    </div>
  );
}
