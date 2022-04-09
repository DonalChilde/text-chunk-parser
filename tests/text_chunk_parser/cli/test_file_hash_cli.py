"""Tests for `file_hash_cli` package."""

import hashlib
import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from tests.text_chunk_parser.conftest import FileResource

from text_chunk_parser.cli.file_hash_cli import main as cli

DATA_2 = {
    "average": 6.45,
    "date": "2020-02-04",
    "highest": 6.45,
    "lowest": 6.44,
    "order_count": 1952,
    "volume": 8332152060,
}
ENCODING = "utf-8"


@pytest.fixture(scope="module", name="test_data")
def test_data_(test_app_data_dir: Path) -> FileResource:
    test_string = json.dumps(DATA_2, indent=2)
    test_file = test_app_data_dir / "test_data.json"
    test_file.write_text(test_string)
    resource = FileResource(test_file, test_string)
    return resource


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert "File Hash" in result.output
    help_result = runner.invoke(cli, ["--help"])
    assert help_result.exit_code == 0
    assert "Show this message and exit." in help_result.output


def test_hash_file_with_md5(test_data: FileResource):
    """Test hashing a file with md5."""
    hash_name = "md5"
    hash_the_test_file(hash_name, test_data)


def hash_the_test_file(hash_name: str, resource: FileResource):
    hasher = hashlib.new(hash_name)
    hasher.update(resource.data.encode(ENCODING))
    hash_hex = hasher.hexdigest()
    runner = CliRunner()
    result = runner.invoke(cli, ["hash", hash_name, "-f", str(resource.file_path)])
    assert result.exit_code == 0
    assert hash_hex in result.output
    assert str(resource.file_path) in result.output


def hash_the_test_string(hash_name: str, resource: FileResource):
    hasher = hashlib.new(hash_name)
    hasher.update(resource.data.encode(ENCODING))
    hash_hex = hasher.hexdigest()
    runner = CliRunner()
    result = runner.invoke(cli, ["hash", hash_name, "-s", resource.data])
    assert result.exit_code == 0
    assert hash_hex in result.output


def test_hash_a_string_with_md5(test_data: FileResource):
    hash_name = "md5"
    hash_the_test_string(hash_name, test_data)


def test_hash_all_the_files():
    pass


def test_hash_with_multiple_methods():
    pass
