"""
Create one or more hashes from the same input.

[extended_summary]
"""
from typing import Any, Dict, List


class HashFactory:
    def __init__(self, hash_names: List[str]) -> None:
        self.hash_names = hash_names
        self.hashers: Dict[str, Any] = {}
        # check hash_names resolve to valid hashers
        # init self.hashers with hashers

    def update_hashes(self, input: Any):
        # update hashers with input
        pass

    def get_hashes(self) -> Dict[str, str]:
        # return dict of hashed values.
        return {"foo": "bar"}
