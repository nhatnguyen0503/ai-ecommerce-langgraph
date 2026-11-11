import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";

import AdminDashboard from "./AdminDashboard";
import { renderWithProviders } from "../test/render";
import { AGENT, server } from "../test/server";
import type { PendingApproval } from "../types/api";

// Test-data factory (like make_order in pytest): override only what a test care about.
function makeApproval(
  overrides: Partial<PendingApproval> = {},
): PendingApproval {
  return {
    id: "ap-1",
    session_id: "sess-1",
    order_id: "FI-10236",
    customer_email: "liisa@example.fi",
    refund_amount: 219,
    reason: "Does not fit",
    status: "pending",
    created_at: "2026-11-10T10:00:00",
    decided_at: null,
    decided_by: null,
    admin_note: null,
    ...overrides,
  };
}

describe("AdminDashboard", () => {
  it("shows an empty state when nothing is pending", async () => {
    renderWithProviders(<AdminDashboard />, { token: "test_token" });
    expect(
      await screen.findByText(/nothing waiting on you/i),
    ).toBeInTheDocument();
  });

  it("lists pending refunds and the orders table", async () => {
    server.use(
      http.get(`${AGENT}/admin/pending-approvals`, () =>
        HttpResponse.json([makeApproval()]),
      ),
    );
    renderWithProviders(<AdminDashboard />, { token: "test-token" });

    expect(
      await screen.findByText(/refunds awaiting approval \(1\)/i),
    ).toBeInTheDocument();
    expect(screen.getByText("EUR 219.00")).toBeInTheDocument();
    // the orders table comes from the other API (:8000)
    expect(
      await screen.findByRole("cell", { name: "FI-10234" }),
    ).toBeInTheDocument();
  });

  it("approves a refund and refreshes the list", async () => {
    // A tiny in-memory "server": the POST changes what the next GET return
    let approvals = [makeApproval()];
    let sentDecision: unknown = null;
    server.use(
      http.get(`${AGENT}/admin/pending-approvals`, () =>
        HttpResponse.json(approvals),
      ),
      http.post(
        `${AGENT}/admin/approvals/:id/decision`,
        async ({ request, params }) => {
          sentDecision = await request.json();
          approvals = approvals.map((a) =>
            a.id === params.id
              ? {
                  ...a,
                  status: "approved",
                  decided_at: "20226-11-10T11:00:00",
                  decided_by: "admin",
                }
              : a,
          );
          return HttpResponse.json({
            approval_id: params.id,
            decision: "approved",
            session_id: "sess-1",
            final_customer_message: null,
          });
        },
      ),
    );
    renderWithProviders(<AdminDashboard />, { token: "test_token" });

    await userEvent
      .setup()
      .click(await screen.findByRole("button", { name: "Approve" }));

    // InvalidatesTags make RTK Query refetch: pending is empty, the item moved to "Recently decided"
    expect(
      await screen.findByText(/nothing waiting on you/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /recently decided/i }),
    ).toBeInTheDocument();
    expect(sentDecision).toMatchObject({
      decision: "approved",
      decided_by: "admin",
    });
  });

  it("shows an error banner when the approvals API fails", async () => {
    server.use(
      http.get(`${AGENT}/admin/pending-approvals`, () =>
        HttpResponse.json(
          { detail: "Database is down", request_id: "req-500" },
          { status: 500 },
        ),
      ),
    );
    renderWithProviders(<AdminDashboard />, { token: "test=token" });
    expect(
      await screen.findByText(/database is down \(request id: req-500\)/i),
    ).toBeInTheDocument();
  });
});
