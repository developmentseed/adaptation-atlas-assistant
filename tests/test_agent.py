import pytest

import atlas_assistant.agent
from atlas_assistant.settings import Settings

pytestmark = pytest.mark.integration


async def test_create_graph(settings: Settings) -> None:
    await atlas_assistant.agent.create_graph(settings)
