import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Routes } from "react-router-dom";
import { http, HttpResponse } from "msw";

import LoginPage from "../../pages/LoginPage";
import RequireAdmin from "./RequireAdmin";
import { renderWithProviders } from "../../test/render";
import { API, server } from "../../test/server";

// Minimal app: a login page and one protected page.
function TestRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<RequireAdmin />}>
        <Route path="/admin" element={<h1>Admin area</h1>} />
      </Route>
    </Routes>
  );
}

async function fillAndSubmit(password: string) {
  const user = userEvent.setup();
  await user.type(screen.getByPlaceholderText("Email"), "admin@example.fi");
  await user.type(screen.getByPlaceholderText("Password"), password);
  await user.click(screen.getByRole("button", { name: /sign in/i }));
}

describe("login flow", () => {
  it("redirects to the login page when there is no token", () => {
    renderWithProviders(<TestRoutes />, { route: "/admin" });
    expect(
      screen.getByRole("heading", { name: /admin login/i }),
    ).toBeInTheDocument();
  });

  it("shows the server error on a wrong password", async () => {
    renderWithProviders(<TestRoutes />, { route: "/login" });
    await fillAndSubmit("wrong-password");
    expect(
      await screen.findByText(/incorrect email or password/i),
    ).toBeInTheDocument();
  });

  it("logs in, stores the token and opens the protected page", async () => {
    renderWithProviders(<TestRoutes />, { route: "/admin" });
    await fillAndSubmit("right-password");
    expect(
      await screen.findByRole("heading", { name: "Admin area" }),
    ).toBeInTheDocument();
    expect(localStorage.getItem("access_token")).toBe("test-token");
  });

  it("keeps the session when a token is already stored", async () => {
    renderWithProviders(<TestRoutes />, {
      route: "/admin",
      token: "test-token",
    });
    expect(
      await screen.findByRole("heading", { name: "Admin area" }),
    ).toBeInTheDocument();
  });

  it("blocks customers from the admin page", async () => {
    server.use(
      http.get(`${API}/auth/me`, () =>
        HttpResponse.json({ id: 2, email: "aino@example.fi", role: "customer" }),
      ),
    );
    renderWithProviders(<TestRoutes />, {
      route: "/admin",
      token: "test-token",
    });
    expect(await screen.findByText(/admins only/i)).toBeInTheDocument();
  });
});
