from typing import Any

import pytest
from pytest import Config, Parser

from atlas_assistant.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings()


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests that require an LLM",
    )


def pytest_collection_modifyitems(config: Config, items: Any) -> None:
    if config.getoption("--integration"):
        return
    skip_integration = pytest.mark.skip(reason="need --integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
