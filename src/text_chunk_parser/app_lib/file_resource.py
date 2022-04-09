"""
A front end to a collection of file resources.

The AppResourceStore provides a front end to a collection of file resources
found in a directory.
"""
from pathlib import Path
from typing import Any, Dict, Optional


class AppResourceStore:
    def __init__(
        self, base_dir: Path, resource_manifest: Optional[Dict[str, Any]]
    ) -> None:
        self.base_dir = base_dir
        self.resource_manifest = resource_manifest

    def resource_path(self, resource_key: str, **kwargs):
        pass
