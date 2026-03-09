# Python Utilities

A small personal Python utility library containing code I frequently use across my personal projects.

Licensed under the MIT License.

## Installation

Install directly from GitHub:

```
pip install pyutils @ git+https://github.com/hunterbaker/python-utils.git
```

Or add it to your `requirements.txt`:

```
pyutils @ git+https://github.com/hunterbaker/python-utils.git
```

Then install:

```
pip install -r requirements.txt
```

## What's Inside

- `Clogger`: A static utility class for enhanced logging with timestamps, source tracking, colors, and custom log types. Intended for more useful print/debug statements.
- `get_env()`: Attempts to safely retrieve an environment variable.
- `check_response()`: Performs basic validation on a requests.Response object.

```python
from pyutils import Clogger, get_env, check_response
import requests

Clogger.info("Starting application")
Clogger.warn("Warning message")
Clogger.error("Error message")
Clogger.debug("Debug message")
Clogger.log("TAG", "Some custom log type")

API_KEY = get_env("API_KEY")

response = requests.get("https://api.example.com/data")

if check_response(response):
    data = response.json()
```

## Dependencies
- colorama
- python-dotenv
- requests
