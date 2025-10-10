import pytest

import atlas_assistant.tools.choose_dataset
from atlas_assistant.settings import Settings

pytestmark = pytest.mark.integration


def test_query_datasets(settings: Settings) -> None:
    datasets = atlas_assistant.tools.choose_dataset.query_datasets(
        "Deforestation", settings
    )
    assert datasets
