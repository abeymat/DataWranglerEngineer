from collections.abc import Iterator

import pytest
from pytest import MonkeyPatch

from app.core.settings import get_settings


@pytest.fixture(autouse=True)
def disable_live_openai_for_tests(monkeypatch: MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("OPENAI_PLANNING_MODE", "deterministic")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
