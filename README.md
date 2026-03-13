# Python Utilities
A small personal Python utility library containing code I frequently use across my personal projects.
Licensed under the MIT License.

More about the package can be seen [here](https://www.hunter-baker.com/pages/projects/pyutils.html)

## Installation
Install directly from GitHub:
```
pip install pyutils @ git+https://github.com/hutnerr/python-utils.git
```
Or add it to your `requirements.txt`:
```
pyutils @ git+https://github.com/hutnerr/python-utils.git
```
Then install:
```
pip install -r requirements.txt
```

## What's Inside
- `Clogger`: A static utility class for enhanced logging with timestamps, source tracking, colors, and custom log types.
- `Clogobj`: A wrapper around Clogger for creating individual logger instances with their own config.
- `get_env()`: Safely retrieves an environment variable.
- `check_response()`: Performs basic validation on a `requests.Response` object.

## Clogger

A static logger with colored output, timestamps, source tracking, and per-call overrides.
```python
from pyutils import Clogger, CloggerConfig, CloggerOverrideFactory, LogLevel

# Basic log levels
Clogger.info("Server started.")
Clogger.warn("High memory usage.")
Clogger.error("Failed to connect to database.")
Clogger.debug("Request payload: {...}")
Clogger.action("User clicked submit.")
Clogger.log("BOOT", "Config loaded.")        # custom tag
```

Adjust global behavior by swapping the config:
```python
# Only print WARN and above
Clogger.config = CloggerConfig(min_log_level=LogLevel.WARN)

# Disable terminal output and write everything to a file instead
Clogger.config = CloggerConfig(print_disabled=True, write_to_file=True, log_file_path="run.log")

# Reset to defaults
Clogger.config = CloggerConfig()
```

Per-call overrides let you deviate from the global config for a single line:
```python
Clogger.info("Detailed trace.", settings_override=CloggerOverrideFactory.verbose())
Clogger.error("Saved quietly.", settings_override=CloggerOverrideFactory.file_only("errors.log"))
Clogger.error("Key not found", exc=KeyError) # also throws exception after logging
Clogger.debug("Pretty printed.", settings_override=CloggerOverrideFactory.pretty())

# Combine overrides
Clogger.info("Verbose and saved.", settings_override=CloggerOverrideFactory.combine(
    CloggerOverrideFactory.verbose(),
    CloggerOverrideFactory.write_to_file("verbose.log")
))
```

## Clogobj

Individual logger instances with their own baked-in config. Useful when different parts of your
app need different logging behavior without touching the global `Clogger.config`.
```python
from pyutils import Clogobj, ClogobjFactory, CloggerConfig

# Pre-built presets
verbose_logger = ClogobjFactory.verbose()
error_logger   = ClogobjFactory.errors_only()
silent_logger  = ClogobjFactory.silent()        # useful in tests

verbose_logger.info("Full timestamps and source shown.")
error_logger.warning("Only WARN and above will print.")
silent_logger.error("No output at all.")
```

Tag a logger to a specific module - no need to pass a tag on every call:
```python
db_logger   = ClogobjFactory.for_module("Database")
auth_logger = ClogobjFactory.for_module("Auth", log_func=Clogger.warning)

db_logger.tagged("Connection established.")      # [Database] Connection established.
db_logger.tagged("Query timeout.", tag="SLOW")   # one-off override: [SLOW] Query timeout.
auth_logger.tagged("Invalid token.")             # [Auth] as WARNING
```

Write a component's logs to its own file:
```python
db_logger = ClogobjFactory.for_file("db.log", also_print=True)
db_logger.info("Printed to terminal and saved to db.log.")
```

Fully custom when nothing else fits:
```python
boot_logger = ClogobjFactory.custom(
    settings=CloggerConfig(simplify_timestamps=False, show_source_file=True),
    default_tag="BOOT",
    default_log_func=Clogger.info,
)
boot_logger.log("App starting up.")
boot_logger.tagged("Config loaded.")
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
