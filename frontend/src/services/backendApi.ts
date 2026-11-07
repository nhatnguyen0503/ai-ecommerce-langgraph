import {
  createApi,
  fetchBaseQuery,
  type BaseQueryFn,
  type FetchArgs,
  type FetchBaseQueryError,
} from "@reduxjs/toolkit/query/react";
import type { RootState } from "../store";
import { loggedOut } from "../features/auth/authSlice";
import type {
  Order,
  ReturnEligibility,
  TokenResponse,
  CurrentUser,
} from "../types/api";

const enc = encodeURIComponent;

const rawBaseQuery = fetchBaseQuery({
  baseUrl: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  // Runs before EVERY request: attach the token if we have one.
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.token;
    if (token) headers.set("Authorization", `Bearer ${token}`);
    return headers;
  },
});

// Wrapper: if the server says 401 (token missing/expired/invalid), log out locally.
const baseQuery: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  const result = await rawBaseQuery(args, api, extraOptions);
  if (result.error?.status === 401) {
    api.dispatch(loggedOut());
  }
  return result;
};

export const backendApi = createApi({
  reducerPath: "backendApi",
  baseQuery,
  tagTypes: ["Me"],
  endpoints: (build) => ({
    // --- auth ---
    login: build.mutation<TokenResponse, { email: string; password: string }>({
      query: ({ email, password }) => ({
        url: "/auth/login",
        method: "POST",
        // OAuth2 password flow expects a FORM, not JSON (same as Swagger's Authorize)
        body: new URLSearchParams({ username: email, password }),
      }),
      invalidatesTags: ["Me"],
    }),
    me: build.query<CurrentUser, void>({
      query: () => "/auth/me",
      providesTags: ["Me"],
    }),

    // --- orders ---
    listOrders: build.query<Order[], void>({ query: () => "/orders" }),
    getOrder: build.query<Order, string>({
      query: (id) => `/orders/${enc(id)}`,
    }),
    getReturnEligibility: build.query<ReturnEligibility, string>({
      query: (id) => `/orders/${enc(id)}/return-eligibility`,
    }),
  }),
});

export const {
  useLoginMutation,
  useMeQuery,
  useListOrdersQuery,
  useGetOrderQuery,
  useGetReturnEligibilityQuery,
} = backendApi;
