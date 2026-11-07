import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type {
  ApprovalDecision,
  ChatMessage,
  ChatResponse,
  DecisionResult,
  PendingApproval,
  SentEmail,
} from "../types/api";

const enc = encodeURIComponent;

export const agentApi = createApi({
  reducerPath: "agentApi",
  baseQuery: fetchBaseQuery({
    baseUrl: import.meta.env.VITE_AGENT_API_BASE_URL || "http://localhost:8001",
  }),
  tagTypes: ["Approval", "Email", "Messages"],
  endpoints: (build) => ({
    // --- chat ---
    getMessages: build.query<ChatMessage[], string>({
      query: (sessionId) => `/chat/${enc(sessionId)}/messages`,
      providesTags: ["Messages"],
    }),
    sendMessage: build.mutation<
      ChatResponse,
      { sessionId: string; message: string }
    >({
      query: ({ sessionId, message }) => ({
        url: "/chat",
        method: "POST",
        body: { session_id: sessionId, message },
      }),
    }),

    // --- admin ---
    listPendingApprovals: build.query<PendingApproval[], void>({
      query: () => "/admin/pending-approvals",
      providesTags: ["Approval"],
    }),
    listSentEmails: build.query<SentEmail[], void>({
      query: () => "/admin/emails",
      providesTags: ["Email"],
    }),
    decideApproval: build.mutation<
      DecisionResult,
      { approvalId: string; decision: ApprovalDecision; note?: string }
    >({
      query: ({ approvalId, decision, note = "" }) => ({
        url: `/admin/approvals/${enc(approvalId)}/decision`,
        method: "POST",
        body: { decision, note, decided_by: "admin" },
      }),
      invalidatesTags: ["Approval", "Email", "Messages"],
    }),
  }),
});

export const {
  useGetMessagesQuery,
  useSendMessageMutation,
  useListPendingApprovalsQuery,
  useListSentEmailsQuery,
  useDecideApprovalMutation,
} = agentApi;
