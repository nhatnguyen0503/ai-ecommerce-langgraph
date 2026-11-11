import type { ReactElement } from "react";
import { render } from "@testing-library/react";
import { Provider } from "react-redux";
import { MemoryRouter } from "react-router-dom";
import { makeStore } from "../store";

interface Options {
  route?: string; // starting URL, e.g. "/admin"
  token?: string; // start already logged in
}

export function renderWithProviders(
  ui: ReactElement,
  { route = "/", token }: Options = {},
) {
  if (token) localStorage.setItem("access_token", token); // read by loadToken()
  const store = makeStore();
  const result = render(
    <Provider store={store}>
      <MemoryRouter
        initialEntries={[route]}
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        {ui}
      </MemoryRouter>
    </Provider>,
  );
  return { store, ...result };
}
