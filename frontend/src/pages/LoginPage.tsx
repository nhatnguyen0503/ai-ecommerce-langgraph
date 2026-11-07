import { useState, type FormEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAppDispatch } from "../hooks";
import { loggedIn } from "../features/auth/authSlice";
import { useLoginMutation } from "../services/backendApi";
import { queryErrorText } from "../services/queryError";

export default function LoginPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  // Where to go after login: the page that sent us here, or /admin by default.
  const from = (location.state as { from?: string } | null)?.from ?? "/admin";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [login, { isLoading, error }] = useLoginMutation();

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    try {
      const { access_token } = await login({ email, password }).unwrap();
      dispatch(loggedIn(access_token));
      navigate(from, { replace: true });
    } catch {
      /* error is shown from the mutation state */
    }
  }

  return (
    <div className="card" style={{ maxWidth: 360 }}>
      <h2 className="section-title" style={{ marginTop: 0 }}>
        Admin login
      </h2>
      {error && (
        <div
          className="status-banner"
          style={{ background: "#fbe3e3", color: "#c23636" }}
        >
          {queryErrorText(error, "Login failed.")}
        </div>
      )}
      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 8 }}>
        <input
          type="email"
          placeholder="Email"
          autoComplete="username"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Signing in…" : "Sign in"}
        </button>
      </form>
    </div>
  );
}
