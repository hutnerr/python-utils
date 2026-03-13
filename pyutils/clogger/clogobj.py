from .clogger import *

class Clogobj:
    def __init__(
        self,
        settings: CloggerConfig = None,
        name: str = None,
        show_name: bool = True,
    ):
        self.settings = settings or CloggerConfig()
        self.name = name
        self.show_name = show_name

    def _resolve_override(self, settings_override: dict | None) -> CloggerConfig:
        """Merge instance settings with a per-call override, returning a CloggerConfig."""
        return Clogger._resolve_config(settings_override, base=self.settings)

    def _tag(self, tag: str) -> str:
        """Prepend the instance name to a tag if name is set and show_name is True."""
        if self.name and self.show_name:
            return f"[{self.name}]{tag}"
        return tag

    def _call(self, tag: str, msg: str, color: CloggerColor, level: LogLevel, settings_override: dict | None):
        """Internal dispatch — injects name into tag and resolves config."""
        cfg = self._resolve_override(settings_override)
        Clogger._log(self._tag(tag), msg, color, level, cfg)

    def log(self, tag: str, message: str, settings_override: dict | None = None):
        self._call(f"[{tag.upper()}]", message, CloggerColor.CYAN, LogLevel.INFO, settings_override)

    def debug(self, message: str, settings_override: dict | None = None):
        self._call("[DEBUG]", message, CloggerColor.MAGENTA, LogLevel.DEBUG, settings_override)

    def info(self, message: str, settings_override: dict | None = None):
        self._call("[INFO]", message, CloggerColor.BLUE, LogLevel.INFO, settings_override)

    def warn(self, message: str, settings_override: dict | None = None):
        self._call("[WARN]", message, CloggerColor.YELLOW, LogLevel.WARN, settings_override)

    def error(self, message: str, settings_override: dict | None = None, exc: type[Exception] | None = None):
        self._call("[ERROR]", message, CloggerColor.RED, LogLevel.ERROR, settings_override)
        if exc:
            raise exc(message)

    def action(self, message: str, settings_override: dict | None = None):
        self._call("[ACTION]", message, CloggerColor.GREEN, LogLevel.ACTION, settings_override)

    def make_log(
        self,
        tag: str,
        color: CloggerColor = CloggerColor.CYAN,
        level: LogLevel = LogLevel.INFO,
        settings_override: dict | None = None,
    ):
        """
        Returns a logger function bound to this instance's settings and name.

        settings_override sets a baseline for every call of the returned function.
        The returned function accepts its own settings_override that layers on top.

        The returned function has the signature:
            logger(msg: str, settings_override: dict | None = None)
        """
        formatted_tag = f"[{tag.upper()}]"
        baseline_cfg = self._resolve_override(settings_override)

        def logger(msg: str, settings_override: dict | None = None):
            cfg = Clogger._resolve_config(settings_override, base=baseline_cfg)
            Clogger._log(self._tag(formatted_tag), msg, color, level, cfg)

        return logger

    def log_errors(self, func):
        """Decorator that logs exceptions via this instance before re-raising them."""
        from functools import wraps
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.error(f"{func.__name__} failed: {e}")
                raise
        return wrapper