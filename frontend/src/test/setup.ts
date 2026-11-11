import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterAll, afterEach, beforeAll } from "vitest";
import { server } from "./server";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  server.resetHandlers(); // drop per-test overrides made with server.use(...)
  cleanup(); // unmount components rendered in the previous test
  localStorage.clear(); // no token leaking between tests
});
afterAll(() => server.close());
