function makeSessionId() {
    return `sess_${Math.random().toString(36).slice(2, 10)}${Date.now().toString(36)}`;
}

export function getOrCreateSessionId() {
    try {
        const existing = window.localStorage.getItem("support_session_id");
        if (existing) return existing;
        const fresh = makeSessionId();
        window.localStorage.setItem("support_session_id", fresh);
        return fresh;
    } catch {
        // localStorage unavailable (private mode etc.) -- fall back to an in-memory id
        return makeSessionId();
    }
}
