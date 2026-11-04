import {createApi, fetchBaseQuery} from "@reduxjs/toolkit/query/react";
import type {Order, ReturnEligibility} from "../types/api";

const enc = encodeURIComponent;

export const ordersApi = createApi({
    reducerPath: "ordersApi",
    baseQuery: fetchBaseQuery({
        baseUrl: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
    }),
    endpoints: (build) => ({
        listOrders: build.query<Order[], void>({
            query: () => "/orders",
        }),
        getOrder: build.query<Order, string>({
            query: (orderId) => `/orders/${enc(orderId)}`,
        }),
        getReturnEligibility: build.query<ReturnEligibility, string>({
            query: (orderId) => `/orders/${enc(orderId)}/return-eligibility`,
        }),
    })
});

export const {useListOrdersQuery, useGetOrderQuery, useGetReturnEligibilityQuery} = ordersApi;