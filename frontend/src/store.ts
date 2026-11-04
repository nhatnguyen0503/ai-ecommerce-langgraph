import {configureStore} from "@reduxjs/toolkit";
import chatReducer from "./features/chat/chatSlice";
import {ordersApi} from "./services/ordersApi";
import {agentApi} from "./services/agentApi";

export const store = configureStore({
    reducer: {
        chat: chatReducer,
        [ordersApi.reducerPath]: ordersApi.reducer,
        [agentApi.reducerPath]: agentApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware().concat(ordersApi.middleware, agentApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

