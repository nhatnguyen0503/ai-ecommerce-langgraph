import type { SerializedError } from "@reduxjs/toolkit";
import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";
import type { ApiErrorBody } from "../types/api";

type QueryError = FetchBaseQueryError | SerializedError | undefined;

export function queryErrorText(error: QueryError, fallback: string): string {
    if (!error) return "";
    if ("status" in error) {
        // HTTP error (or network error: status "FETCH_ERROR")
        const body = error.data as ApiErrorBody | undefined;
        const detail = typeof body?.detail === "string" ? body.detail : fallback;
        return body?.request_id ? `${detail} (request id: ${body.request_id})` : detail;
    }
    return error.message ?? fallback; // SerializedError: a JS error thrown inside RTK
}