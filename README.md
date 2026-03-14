# Python Utilities
A small personal Python utility library containing code I frequently use across my personal projects.
Licensed under the MIT License.

More about the package can be seen [here](https://www.hunter-baker.com/pages/projects/pyutils.html)

## Installation
Install directly from GitHub:
```bash
pip install "pyutils @ git+https://github.com/hutnerr/python-utils.git"
```
Or add it to your `requirements.txt`:
```
pyutils @ git+https://github.com/hutnerr/python-utils.git
```
Then install:
```bash
pip install -r requirements.txt
```

## What's Inside
- `Clogger`: A static utility class for enhanced logging with timestamps, source tracking, colors, and custom log types.
- `Clogobj`: A wrapper around Clogger for creating individual logger instances with their own config and optional name tagging.
- `CloggerOverrideFactory`: Convenience factory for building per-call settings overrides.
- `ClogobjFactory`: Preset factory for quickly spinning up configured `Clogobj` instances.
- `get_env()`: Safely retrieves an environment variable.
- `check_response()`: Performs basic validation on a `requests.Response` object.

## Clogger

A static logger with colored output, timestamps, source tracking, and per-call overrides.

```python
from pyutils import Clogger, CloggerConfig, CloggerSetting, CloggerOverrideFactory, LogLevel

Clogger.info("Server started.")
Clogger.warn("High memory usage.")
Clogger.error("Failed to connect.", exc=KeyError)  # logs then raises
Clogger.debug("Request payload: {...}")
Clogger.action("User clicked submit.")
Clogger.log("BOOT", "Config loaded.")              # custom tag
```

Swap the global config at any time:
```python
Clogger.config = CloggerConfig(min_log_level=LogLevel.WARN)
Clogger.config = CloggerConfig(disable_colors=True, use_tag=False)
Clogger.config = CloggerConfig(print_disabled=True, write_to_file=True, log_file_path="run.log")
Clogger.config = CloggerConfig()  # reset
```

Per-call overrides let you deviate from global config for a single line:
```python
Clogger.info("Trace.", settings_override=CloggerOverrideFactory.verbose())
Clogger.error("Saved quietly.", settings_override=CloggerOverrideFactory.file_only("errors.log"))
Clogger.debug("Dict dump.", settings_override=CloggerOverrideFactory.pretty())

# combine multiple overrides — later keys win on conflict
Clogger.info("Verbose and saved.", settings_override=CloggerOverrideFactory.combine(
    CloggerOverrideFactory.verbose(),
    CloggerOverrideFactory.write_to_file("verbose.log"),
    {CloggerSetting.DISABLE_COLORS: True}
))
```

Create reusable custom loggers with `make_log`:
```python
log_boot = Clogger.make_log("BOOT", color=CloggerColor.CYAN, level=LogLevel.INFO)
log_boot("App starting up.")   # [BOOT]    | main.py:12 | App starting up.

# bake in a settings baseline — still overridable per call
log_trace = Clogger.make_log(
    "TRACE",
    color=CloggerColor.MAGENTA,
    settings_override={CloggerSetting.SIMPLIFY_TIMESTAMPS: False}
)
log_trace("Deep trace.", settings_override={CloggerSetting.SHOW_SOURCE_FILE: False})
```

## Clogobj

Instance-based loggers with their own baked-in config and optional name. Useful when different
parts of your app need different logging behavior without touching global `Clogger.config`.

```python
from pyutils import Clogobj, ClogobjFactory, CloggerConfig

verbose_logger = ClogobjFactory.verbose()
silent_logger  = ClogobjFactory.silent()   # useful in tests
file_logger    = ClogobjFactory.file_only("run.log")

verbose_logger.info("Full timestamps and source shown.")
silent_logger.error("No output at all.")
```

Name a logger to a module — the name appears before the level tag on every line:
```python
# 17:58:40 [Database][INFO]  | db.py:42 | Connection established.
db_logger = ClogobjFactory.for_module("Database")
db_logger.info("Connection established.")
db_logger.warn("Slow query detected.")
```

`make_log` on an instance returns a bound logger that inherits the instance's settings and name:
```python
auth = Clogobj(
    settings=CloggerConfig(simplify_timestamps=False),
    name="Auth",
)

log_token = auth.make_log("TOKEN", color=CloggerColor.YELLOW, level=LogLevel.WARN)
log_token("Invalid token.")   # 2025-01-01 17:58:40 EST [Auth][TOKEN]  | auth.py:7 | Invalid token.

# per-call overrides still layer on top
log_token("Suppressed.", settings_override={CloggerSetting.PRINT_DISABLED: True})
```

Use `log_errors` as a decorator to automatically route exceptions through the instance:
```python
db = ClogobjFactory.for_module("Database")

@db.log_errors
def connect():
    raise ConnectionError("timeout")

connect()  # [Database][ERROR] | db.py:8 | connect failed: timeout
```

Fully custom when nothing else fits:
```python
boot = ClogobjFactory.custom(
    settings=CloggerConfig(simplify_timestamps=False, show_source_file=True),
    name="BOOT",
)
boot.info("App starting up.")
boot.log("INIT", "Config loaded.")
```

## Option & Result

Rust-inspired types for explicit null and error handling - no bare `None` checks or scattered `try/except`.

```python
from pyutils import Option, Result
```

**Option** wraps a value that may or may not exist. Unlike bare `None`, `Some(None)` is a valid distinct state.

```python
Option.some(42).unwrap()              # 42
Option.none().unwrap_or(0)            # 0
Option.none().unwrap_or_else(fn)      # fn() — only called if None
```

**Result** wraps either a success value or an error. `Ok(None)` and `Err(None)` are both valid and distinguishable.

```python
Result.ok(42).unwrap()                # 42
Result.err("oops").unwrap_err()       # "oops"
Result.err("oops").unwrap_or(0)       # 0
Result.err("oops").expect("failed")   # raises: ValueError: failed: 'oops'
```

Both types support `bool()` coercion, equality, hashing, and iter unpacking:

```python
bool(Option.some(0))     # True  — state-based, not value-based
bool(Option.none())      # False
bool(Result.ok(None))    # True
bool(Result.err("x"))    # False

Option.some(1) == Option.some(1)    # True
(value,) = Option.some("hello")     # unpacking
```

## Other Utilities
```python
from pyutils import get_env, check_response
import requests

API_KEY = get_env("API_KEY")

response = requests.get("https://api.example.com/data")
if check_response(response):
    data = response.json()
```

## Dependencies
- colorama
- python-dotenv
- requests