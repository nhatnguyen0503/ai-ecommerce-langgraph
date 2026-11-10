import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

export const API = "http://localhost:8000";
export const AGENT = "http://localhost:8001";

// Default handlers = the "happy path". Individual tests override with server.use(...)
export const handlers = [
  http.post(`${API}/auth/login`, async ({ request }) => {
    const form = await request.formData();
    if (form.get("password") === "right-password") {
      return HttpResponse.json({
        access_token: "test-token",
        token_type: "bearer",
      });
    }
    return HttpResponse.json(
      { detail: "Incorrect email or password", request_id: "t-1" },
      { status: 401 },
    );
  }),

  http.get(`${API}/auth/me`, ({ request }) => {
    if (request.headers.get("Authorization") !== "Bearer test-token") {
      return HttpResponse.json(
        { detail: "Not authenticated", request_id: "t-2" },
        { status: 401 },
      );
    }
    return HttpResponse.json({
      id: 1,
      email: "admin@example.fi",
      role: "admin",
    });
  }),

  http.get(`${API}/orders`, () =>
    HttpResponse.json([
      {
        id: "FI-10234",
        customer_name: "Aino",
        customer_email: "aino@example.fi",
        items: [],
        total_amount: 29.9,
        currency: "EUR",
        status: "delivered",
        warehouse: "Posti Helsinki Hub",
        order_date: "2026-11-01T10:00:00",
        delivered_date: null,
      },
    ]),
  ),
];

export const server = setupServer(...handlers);
