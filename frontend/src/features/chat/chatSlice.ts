import {createSlice, type PayloadAction} from "@reduxjs/toolkit";
import type {ChatMessage} from "../../types/api";
import {getOrCreateSessionId} from "./session";

interface ChatState {
    sessionId: string;
    messages: ChatMessage[];
    sending: boolean;
    awaitingApproval: boolean;
    error: string;
}

const initialState: ChatState = {
    sessionId: getOrCreateSessionId(),
    messages: [],
    sending: false,
    awaitingApproval: false,
    error: "",
};

export const chatSlice = createSlice({
    name: "chat",
    initialState,
    reducers: {
        messagesLoaded(state, action: PayloadAction<ChatMessage[]>) {
            state.messages = action.payload;
        },
        userMessageAdded(state, action: PayloadAction<string>) {
            state.messages.push({role: "user", content: action.payload});
        },
        sendStarted(state) {
            state.sending = true;
            state.error = "";
        },
        sendFinished(state) {
            state.sending = false;
        },
        sendFailed(state, action: PayloadAction<string>) {
            state.error = action.payload;
        },
        awaitingApprovalChanged(state, action: PayloadAction<boolean>) {
            state.awaitingApproval = action.payload;
        },
    },
});

export const {
    messagesLoaded,
    userMessageAdded,
    sendStarted,
    sendFinished,
    sendFailed,
    awaitingApprovalChanged,
} = chatSlice.actions;

export default chatSlice.reducer;