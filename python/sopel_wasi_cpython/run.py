from __future__ import annotations
import time

from typing import Optional, TypedDict

from .cpython_wasi_wrapper import run_cpython


class WASMResult(TypedDict):
    fuel_remaining: int
    stdout: bytes
    stderr: bytes

    error: Optional[str]
    trapType: Optional[str]


def run_python(src: str, fuel_limit: int|None = None) -> dict:
    result = run_cpython(["-c", src], fuel_limit=fuel_limit)

    # TODO:allow stripping the expected "Could not find" messages on stderr

    return result
