import { configureStore } from "@reduxjs/toolkit";
import chatReducer from "./features/chat/chatSlice";
import authReducer, { saveToken } from "./features/auth/authSlice";
import { backendApi } from "./services/backendApi";
import { agentApi } from "./services/agentApi";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    chat: chatReducer,
    [backendApi.reducerPath]: backendApi.reducer,
    [agentApi.reducerPath]: agentApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(backendApi.middleware, agentApi.middleware),
});

// Persist the token whenever it changes (side effect lives outside the reducer)
let lastToken = store.getState().auth.token;
store.subscribe(() => {
  const token = store.getState().auth.token;
  if (token !== lastToken) {
    lastToken = token;
    saveToken(token);
  }
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
