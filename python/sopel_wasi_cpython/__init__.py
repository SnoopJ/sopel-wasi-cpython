from __future__ import annotations
import time

from .cpython_wasi_wrapper import run_cpython


DEFAULT_INITIAL_FUEL = 1_000_000_000

def run_python(src: str, fuel: int|None = DEFAULT_INITIAL_FUEL) -> tuple[str, str]:
    stdout, stderr = run_cpython(["-c", src], fuel=fuel)

    # TODO:allow stripping the expected "Could not find" messages on stderr

    return (stdout, stderr)
