import logging

from app.request_context import RequestIdFilter, request_id_var, resolve_request_id


def test_resolve_keeps_valid_client_id():
    assert resolve_request_id("my-test-123") == "my-test-123"


def test_resolve_generates_id_when_missing():
    request_id = resolve_request_id()
    assert len(request_id) == 32


def test_resolve_replaces_unsafe_id():
    unsafe = "bad id\nINFO fake log line"
    request_id = resolve_request_id(unsafe)
    assert request_id != unsafe
    assert "\n" not in request_id


def test_filter_adds_current_request_id():
    token = request_id_var.set("abc-1")
    try:
        record = logging.LogRecord("test", logging.INFO, __file__, 1, "hello", None, None)
        assert RequestIdFilter().filter(record) is True
        assert record.request_id == "abc-1"
    finally:
        request_id_var.reset(token)


def test_filter_uses_dash_outside_request():
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "hello", None, None)
    RequestIdFilter().filter(record)
    assert record.request_id == "-"
