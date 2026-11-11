import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";

import ChatWidget from "./ChatWidget";
import { renderWithProviders } from "../test/render";
import { AGENT, server } from "../test/server";
import type { ChatResponse } from "../types/api";

// Type a message and press Send, like a real user.
async function send(text: string) {
  const user = userEvent.setup();
  await user.type(screen.getByPlaceholderText(/ask about an order/i), text);
  await user.click(screen.getByRole("button", { name: "Send" }));
}

// Make the fake agent answer POST /chat with this body.
function replyWith(body: ChatResponse) {
  server.use(http.post(`${AGENT}/chat`, () => HttpResponse.json(body)));
}

describe("ChatWidget", () => {
  it("shows a hint when there is no history yet", async () => {
    renderWithProviders(<ChatWidget />);
    expect(
      await screen.findByText(/What's the status of order/i),
    ).toBeInTheDocument();
  });

  it("sends a message and shows the agent reply", async () => {
    let sentBody: unknown = null;
    server.use(
      http.post(`${AGENT}/chat`, async ({ request }) => {
        sentBody = await request.json();
        return HttpResponse.json({
          session_id: "s",
          reply: "Your order is in transit.",
          status: "ok",
          messages: [
            { role: "user", content: "Where is FI-10237?" },
            { role: "assistant", content: "Your order is in transit." },
          ],
        });
      }),
    );
    renderWithProviders(<ChatWidget />);
    await send("Where is FI-10237?");

    expect(
      await screen.findByText("Your order is in transit."),
    ).toBeInTheDocument();
    expect(screen.getByText("Where is FI-10237?")).toBeInTheDocument();
    // The input is cleared after sending
    expect(screen.getByPlaceholderText(/ask about an order/i)).toHaveValue("");
    expect(sentBody).toMatchObject({ message: "Where is FI-10237?" });
  });

  it("shows the approval banner when a refund needs an admin", async () => {
    replyWith({
      session_id: "s",
      reply: "Your refund was submitted for review.",
      status: "awaiting_approval",
      messages: [{ role: "user", content: "Refund FI-10236 please" }],
    });
    renderWithProviders(<ChatWidget />);
    await send("Refund FI-10236 please");

    expect(
      await screen.findByText(/waiting for admin approval/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Your refund was submitted for review."),
    ).toBeInTheDocument();
  });

  it("shows an error when the agent fails", async () => {
    server.use(
      http.post(`${AGENT}/chat`, () =>
        HttpResponse.json(
          { detail: "Agent unavailable", request_id: "req-chat" },
          { status: 500 },
        ),
      ),
    );
    renderWithProviders(<ChatWidget />);
    await send("Hello");

    expect(
      await screen.findByText("Agent unavailable (request id: req-chat)"),
    ).toBeInTheDocument();
    // sending finished, so the button is back to "Send" (not "Sending...")
    expect(screen.getByRole("button", { name: "Send" })).toBeInTheDocument();
  });
});
