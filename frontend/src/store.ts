import { configureStore } from "@reduxjs/toolkit";
import chatReducer from "./features/chat/chatSlice";
import authReducer, { saveToken } from "./features/auth/authSlice";
import { backendApi } from "./services/backendApi";
import { agentApi } from "./services/agentApi";

export function makeStore() {
  const store = configureStore({
    reducer: {
      auth: authReducer,
      chat: chatReducer,
      [backendApi.reducerPath]: backendApi.reducer,
      [agentApi.reducerPath]: agentApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(backendApi.middleware, agentApi.middleware),
  });

  // Persist the token whenever it changes (side effect lives outside the reducer).
  let lastToken = store.getState().auth.token;
  store.subscribe(() => {
    const token = store.getState().auth.token;
    if (token !== lastToken) {
      lastToken = token;
      saveToken(token);
    }
  });

  return store;
}

export const store = makeStore();

export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore["getState"]>;
export type AppDispatch = AppStore["dispatch"];
