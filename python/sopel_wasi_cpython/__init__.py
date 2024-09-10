from __future__ import annotations
import itertools
import logging
import re
import signal

from sopel import plugin

from .run import run_python
from .transform import maybe_print_last


LOGGER = logging.getLogger(__name__)


# TODO: add setup(), configuration


VERBOSE_SUFFIXES = [":v", ":verbose"]
PY_COMMANDS = [
    "py",
    "cpy",
    "cpython",
]
PY_VERBOSE_COMMANDS = [f"{cmd}{suffix}" for cmd, suffix in itertools.product(PY_COMMANDS, VERBOSE_SUFFIXES)]
PY_COMMANDS += PY_VERBOSE_COMMANDS

DEFAULT_INITIAL_FUEL = 1_000_000_000


@plugin.commands(*PY_COMMANDS)
def exec_py(bot, trigger):
    """Run the specified program in CPython (WASI)"""
    verbose = trigger.group(1) in PY_VERBOSE_COMMANDS

    if not trigger.group(2):
        bot.say(f'Must pass a Python program, try: {bot.config.core.prefix}py print("Hello world!")')
        return False

    user_program = maybe_print_last(trigger.group(2))

    if trigger.admin:
        fuel_limit = None
    else:
        fuel_limit = DEFAULT_INITIAL_FUEL

    # TODO: re-introduce timeout, memory limit, exit code

    wasm_result = run_python(
        user_program,
        fuel_limit=fuel_limit,
    )
    wasm_stdout = wasm_result["stdout"].decode()
    wasm_stderr = wasm_result["stderr"].decode()

    # NOTE:2024-08-02:snoopj:The WASI build of CPython puts out these messages. They're benign and expected, so we can strip them
    benign_error = "Could not find platform independent libraries <prefix>\nCould not find platform dependent libraries <exec_prefix>\n"
    if wasm_stderr.startswith(benign_error):
        wasm_stderr = wasm_stderr[len(benign_error):]

    wasm_fuel = wasm_result["fuel_remaining"]
    wasm_error = wasm_result["error"]
    wasm_trap = wasm_result["trapType"]
    if wasm_error:
        if m := re.match(r"Exited with i32 exit status (?P<exitcode>-?\d+)", wasm_error):
            bot.say(f'WASM guest exited with non-zero code {m.group("exitcode")}')
        elif wasm_trap:
            bot.say(f"WASM trap {wasm_trap} occurred: {wasm_error}")
        else:
            bot.say(f"WASM error occurred: {wasm_error}")
        if wasm_stderr:
            bot.say(f"stderr: {wasm_stderr}", truncation="…")

    bot.say(wasm_stdout, truncation="…")
    if verbose and fuel_limit:
        bot.say(f"Fuel consumed: {fuel_limit - wasm_fuel} out of {fuel_limit}")
    elif verbose and not fuel_limit:
        bot.say("No fuel limit")



