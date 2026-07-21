import logging

from app.core.logging import _CorrelationIdFilter


def test_correlation_filter_supplies_default_for_third_party_logs() -> None:
    record = logging.LogRecord(
        name="httpx",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request completed",
        args=(),
        exc_info=None,
    )

    assert _CorrelationIdFilter().filter(record) is True
    assert record.__dict__["correlation_id"] == "-"


def test_correlation_filter_preserves_request_value() -> None:
    record = logging.LogRecord(
        name="salesforce_etl",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="workflow completed",
        args=(),
        exc_info=None,
    )
    record.__dict__["correlation_id"] = "corr-test"

    assert _CorrelationIdFilter().filter(record) is True
    assert record.__dict__["correlation_id"] == "corr-test"
