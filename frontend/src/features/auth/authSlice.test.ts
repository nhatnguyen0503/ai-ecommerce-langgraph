import { describe, expect, it } from "vitest";
import reducer, { loggedIn, loggedOut } from "./authSlice";

describe("authSlice", () => {
  it("stores the token on loggedIn", () => {
    const state = reducer({ token: null }, loggedIn("abc"));
    expect(state.token).toBe("abc");
  });

  it("clears the token on loggedOut", () => {
    const state = reducer({ token: "abc" }, loggedOut());
    expect(state.token).toBe(null);
  });
});
