# sopel-wasi-cpython

A [Sopel](https://sopel.chat/) plugin for evaluating small Python programs in
a genuine copy of CPython, the reference implementation of Python.

**NOTE:** The included copy of CPython and its standard library are used under
the terms given in [python/sopel_wasi_cpython/CPython-WASI/license.rst](./python/sopel_wasi_cpython/CPython-WASI/license.rst).
These components retain their original license. All other software in this
repository is licensed under the Eiffel Forum License v2, see [LICENSE](./LICENSE).


## Installation

```bash
$ pip install git+https://github.com/SnoopJ/sopel-wasi-cpython
```

## Usage

Use the `py` command with a Python program that fits in an IRC message. Note
that many [compound statements](https://docs.python.org/3/reference/compound_stmts.html)
do not fit on a single line, so this plugin is not capable of executing _all_
possible Python programs.

If the program does not contain any `print()` calls, the `repr()` of the last
expression (if there is one) will be printed as the plugin output.

```irc
<SnoopJ> !py [2**n for n in range(1, 32)]
<terribot> [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608, 16777216, 33554432, 67108864, 134217728, 268435456, 536870912, 1073741824, 2147483648]
```

The included Python is a nearly complete CPython, although some functionality
is not present. A good example of missing functionality is the `ctypes` library:

```
<SnoopJ> !py import ctypes
<terribot> Exited with code 1
<terribot> Traceback (most recent call last): ⏎   File "<string>", line 1, in <module> ⏎     import ctypes ⏎   File "/opt/CPython-WASI/wasm-site-packages/ctypes/__init__.py", line 8, in <module> ⏎     from _ctypes import Union, Structure, Array ⏎ ModuleNotFoundError: No module named '_ctypes'
```

## Notes

### Implementation

This plugin runs an isolated copy of the CPython interpreter in [WebAssembly](https://webassembly.org/)
(in the [wasmtime](https://github.com/bytecodealliance/wasmtime-py) runtime)
using the [WebAssembly System Interface (WASI)](https://github.com/WebAssembly/WASI)
to handle (most) system calls.

A pre-built copy of the WASI build of CPython (against commit [`bc93923`](https://github.com/python/cpython/commit/bc93923a2dee00751e44da58b6967c63e3f5c392))
is included in deal this repository, but it can be replaced with a different
version produced by following the [build instructions](https://devguide.python.org/getting-started/setup-building/#wasi)
for the `wasm32-wasi` build of CPython by replacing the `python.wasm` file.
(tl;dr, I built mine with: `WASI_SDK_PATH=/path/to/wasi-sdk-21.0 python3.12 Tools/wasm/wasi.py build`)

### Security

This plugin tries to provide Python evaluation to IRC users _without_ posing a
security risk to the host system. There are a few mechanisms to prevent untoward
behavior:

* The WASM guest has read-only access to the Python stdlib using the "preopened directory" feature
* The number of (WASM) instructions executed by the WASM guest is controlled using the `wasmtime` "fuel" functionality
  * Most WASM instructions consume 1 fuel. Because these instructions are what is used to implement the Python interpreter
    itself, there is not a direct relationship to the amount of Python execution that can occur. The default fuel limit
    of `1_000_000_000` was tuned by hand to allow a broad range of interesting programs while also stopping malicious
    time-wasting programs before they have run for "too long".
