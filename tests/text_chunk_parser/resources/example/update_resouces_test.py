"""These tests are not meant to be run during normal testing.

This is a convenience to regenerate dynamic test data on demand.
Set REFRESH_RESOURCES to True and run tests to generate data.
"""

import json
from pathlib import Path

import yaml

REFRESH_RESOURCES = False

DATA_1 = [
    {
        "average": 6.29,
        "date": "2020-02-01",
        "highest": 6.48,
        "lowest": 6.24,
        "order_count": 2175,
        "volume": 5885496148,
    },
    {
        "average": 6.46,
        "date": "2020-02-02",
        "highest": 6.47,
        "lowest": 6.24,
        "order_count": 2375,
        "volume": 7427198727,
    },
    {
        "average": 6.29,
        "date": "2020-02-03",
        "highest": 6.4,
        "lowest": 5.89,
        "order_count": 1921,
        "volume": 8216531633,
    },
    {
        "average": 6.45,
        "date": "2020-02-04",
        "highest": 6.45,
        "lowest": 6.44,
        "order_count": 1952,
        "volume": 8332152060,
    },
]

DATA_2 = {
    "average": 6.45,
    "date": "2020-02-04",
    "highest": 6.45,
    "lowest": 6.44,
    "order_count": 1952,
    "volume": 8332152060,
}


def test_example_resources():
    if not REFRESH_RESOURCES:
        assert True
        return
    resource_parent_path = Path(__file__).parent

    # json resources
    resource_subpath = resource_parent_path / "json_resources"
    resource_subpath.mkdir(parents=True, exist_ok=True)
    init = resource_subpath / Path("__init__.py")
    init.touch()
    data_file_1 = resource_subpath / Path("data_1.json")
    data_file_1.write_text(json.dumps(DATA_1, indent=2))
    data_file_2 = resource_subpath / Path("data_2.json")
    data_file_2.write_text(json.dumps(DATA_2, indent=2))

    # yaml resources
    resource_subpath = resource_parent_path / "yaml_resources"
    resource_subpath.mkdir(parents=True, exist_ok=True)
    init = resource_subpath / Path("__init__.py")
    init.touch()
    data_file_1 = resource_subpath / Path("data_1.yaml")
    data_file_1.write_text(yaml.safe_dump(DATA_1, indent=2))
    data_file_2 = resource_subpath / Path("data_2.yaml")
    data_file_2.write_text(yaml.safe_dump(DATA_2, indent=2))
