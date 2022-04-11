from typing import Dict

from tests.text_chunk_parser.conftest import FileResource


def test_example_resource(json_resources: Dict[str, FileResource]):
    """Check that the example resource was loaded correctly."""
    print(json_resources)
    assert len(json_resources["data_1.json"].data) == 4
    assert json_resources["data_2.json"].data["average"] == 6.45
