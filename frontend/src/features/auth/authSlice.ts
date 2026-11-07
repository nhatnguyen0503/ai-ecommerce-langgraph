import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

const TOKEN_KEY = "access_token";

function loadToken(): string | null {
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

function saveToken(token: string | null): void {
  try {
    if (token) window.localStorage.setItem(TOKEN_KEY, token);
    else window.localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* ignore */
  }
}

interface AuthState {
  token: string | null;
}

const initialState: AuthState = { token: loadToken() };

export const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    loggedIn(state, action: PayloadAction<string>) {
      state.token = action.payload;
    },
    loggedOut(state) {
      state.token = null;
    },
  },
});

export const { loggedIn, loggedOut } = authSlice.actions;
export default authSlice.reducer;
export { saveToken };
