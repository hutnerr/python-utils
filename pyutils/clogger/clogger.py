import sys
import io
import time
import inspect
import os
import enum
from pprint import pprint
from dataclasses import dataclass
from colorama import Fore, Style, Back, init
from functools import wraps

init(autoreset=True)  # this is for colorama


class LogLevel(enum.Enum):
    MUTE   = 0 # sentinel level
    ERROR  = 1 # for genuine errors that need attention
    WARN   = 2 # for potential issues or important notices that aren't necessarily errors
    INFO   = 3 # general purpose information about program execution
    ACTION = 4 # actions or steps that a user has taken 
    DEBUG  = 5 # alternative to print debugging


class CloggerSetting(enum.Enum):
    """
    Keys for use in settings dicts when creating a CloggerConfig or passing a
    settings_override to any log method. Can be used as enum keys or plain strings.

    Example:
        Clogger.info("msg", settings_override={CloggerSetting.TIMESTAMPS_ENABLED: False})
        Clogger.info("msg", settings_override={"timestamps_enabled": False})
    """
    DISABLED            = "disabled"
    DEBUG_ENABLED       = "debug_enabled"
    TIMESTAMPS_ENABLED  = "timestamps_enabled"
    SIMPLIFY_TIMESTAMPS = "simplify_timestamps"
    SHOW_SOURCE_FILE    = "show_source_file"
    FORCE_FLUSH         = "force_flush"
    PPRINT_ENABLED      = "pprint_enabled"
    WRITE_TO_FILE       = "write_to_file"
    LOG_FILE_PATH       = "log_file_path"
    MIN_LOG_LEVEL       = "min_log_level"
    PRINT_DISABLED      = "print_disabled"
    USE_TAG             = "use_tag"
    DISABLE_COLORS      = "disable_colors"

class CloggerColor(enum.Enum):
    RED     = Fore.RED
    GREEN   = Fore.GREEN
    YELLOW  = Fore.YELLOW
    BLUE    = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN    = Fore.CYAN
    RESET   = Style.RESET_ALL

class CloggerConfig:
    """
    Configuration class for Clogger. Assign an instance to Clogger.config to change
    global settings, or pass a settings_override dict to any log method for a
    single-call override without affecting global state.

    Settings:
    - `disabled`:            completely disables all logging when True
    - `debug_enabled`:       if True, debug messages will be printed; otherwise ignored
    - `timestamps_enabled`:  if True, prepends a timestamp to every log line
    - `simplify_timestamps`: if True, shows HH:MM:SS only; if False, shows full date + timezone
    - `show_source_file`:    if True, appends the caller's filename and line number
    - `force_flush`:         if True, flushes stdout after every print (useful when piping output)
    - `pprint_enabled`:      if True, enables pretty-printing of complex objects (dicts, lists)
    - `write_to_file`:       if True, also writes logs to the file at log_file_path
    - `log_file_path`:       path to the log file (default: clogger.log)
    - `min_log_level`:       minimum log level to print — messages below this level are ignored
    - `print_disabled`:      if True, suppresses terminal output but still writes to file if write_to_file is enabled
    - `use_tag`:             if True, prepends the level tag (e.g. [INFO]) to each log line
    - `disable_colors`:      if True, suppresses all ANSI color codes in terminal output

    Examples:
        Clogger.config = CloggerConfig(disabled=True)
        Clogger.config = CloggerConfig.from_dict({"disabled": True, "force_flush": False})
        Clogger.config = CloggerConfig.from_dict({CloggerSetting.DISABLED: True})
    """

    def __init__(
        self,
        disabled:            bool     = False,
        debug_enabled:       bool     = True,
        timestamps_enabled:  bool     = True,
        simplify_timestamps: bool     = True,
        show_source_file:    bool     = True,
        force_flush:         bool     = True,
        pprint_enabled:      bool     = False,
        write_to_file:       bool     = False,
        log_file_path:       str      = "clogger.log",
        min_log_level:       LogLevel = LogLevel.DEBUG,
        print_disabled:      bool     = False,
        use_tag:             bool     = True,
        disable_colors:      bool     = False,
    ):
        self.disabled            = disabled
        self.debug_enabled       = debug_enabled
        self.timestamps_enabled  = timestamps_enabled
        self.simplify_timestamps = simplify_timestamps
        self.show_source_file    = show_source_file
        self.force_flush         = force_flush
        self.pprint_enabled      = pprint_enabled
        self.write_to_file       = write_to_file
        self.log_file_path       = log_file_path
        self.min_log_level       = min_log_level
        self.print_disabled      = print_disabled
        self.use_tag             = use_tag
        self.disable_colors      = disable_colors

    @classmethod
    def from_dict(cls, settings: dict[CloggerSetting | str, any]) -> "CloggerConfig":
        """
        Create a CloggerConfig from a dict using CloggerSetting enum keys, plain strings, or both.
        Unknown keys are ignored.

        Examples:
            CloggerConfig.from_dict({CloggerSetting.DISABLED: True})
            CloggerConfig.from_dict({"disabled": True, "force_flush": False})
            CloggerConfig.from_dict({CloggerSetting.DISABLED: True, "force_flush": False})
        """
        valid_keys = cls.__init__.__code__.co_varnames
        normalized = {}
        for k, v in settings.items():
            key = k.value if isinstance(k, CloggerSetting) else k
            if key in valid_keys:
                normalized[key] = v
        return cls(**normalized)

    def to_dict(self) -> dict:
        """Convert this CloggerConfig instance to a plain dict."""
        return {
            "disabled":            self.disabled,
            "debug_enabled":       self.debug_enabled,
            "timestamps_enabled":  self.timestamps_enabled,
            "simplify_timestamps": self.simplify_timestamps,
            "show_source_file":    self.show_source_file,
            "force_flush":         self.force_flush,
            "pprint_enabled":      self.pprint_enabled,
            "write_to_file":       self.write_to_file,
            "log_file_path":       self.log_file_path,
            "min_log_level":       self.min_log_level,
            "print_disabled":      self.print_disabled,
            "use_tag":             self.use_tag,
            "disable_colors":      self.disable_colors,
        }


class Clogger:
    config: CloggerConfig = CloggerConfig()

    @staticmethod
    def _resolve_config(settings_override: dict | CloggerConfig | None, base: CloggerConfig | None = None) -> CloggerConfig:
        """Merge a base config (or global config) with a per-call override dict or CloggerConfig."""
        base = base or Clogger.config
        if not settings_override:
            return base
        if isinstance(settings_override, CloggerConfig):
            settings_override = settings_override.to_dict()

        base_dict = base.__dict__.copy()
        override = CloggerConfig.from_dict(settings_override).__dict__

        normalized_keys = {
            (k.value if isinstance(k, CloggerSetting) else k)
            for k in settings_override.keys()
        }
        merged = {k: (override[k] if k in normalized_keys else v) for k, v in base_dict.items()}
        return CloggerConfig(**merged)

    @staticmethod
    def _getTimestamp(cfg: CloggerConfig) -> str:
        """Get formatted timestamp based on config."""
        if not cfg.timestamps_enabled:
            return ""
        
        if cfg.simplify_timestamps:
            ts = time.strftime('%H:%M:%S', time.localtime())
        else:
            ts = time.strftime('%Y-%m-%d %H:%M:%S EST', time.localtime())

        if cfg.disable_colors:
            return f"{ts} "
        
        return f"{Back.BLACK}{Fore.GREEN}{ts}{Style.RESET_ALL} "

    @staticmethod
    def _getCaller() -> str:
        """Walk up the stack to find the first frame outside of clogger.py."""
        frame = inspect.currentframe()
        while frame:
            filename = os.path.basename(frame.f_code.co_filename)
            if filename != "clogger.py":
                return f"{filename}:{frame.f_lineno}"
            frame = frame.f_back
        return "unknown"

    @staticmethod
    def _log(tag: str, msg: str, color: CloggerColor = CloggerColor.CYAN, level: LogLevel = LogLevel.DEBUG, cfg: CloggerConfig = None):
        cfg = cfg or Clogger.config

        if cfg.disabled:
            return
        
        if level.value > cfg.min_log_level.value:
            return

        # build tag segment — omit entirely (including separator) when use_tag is False
        if cfg.use_tag:
            if cfg.disable_colors:
                tag_part = f"{tag:<8} |"
            else:
                tag_part = f"{color.value}{tag:<8}{Style.RESET_ALL} |"
            clean_tag_part = f"{tag:<8} |"
        else:
            tag_part = ""
            clean_tag_part = ""

        # if pprint is enabled and msg is a complex object, pretty-print it below the tag line
        if cfg.pprint_enabled and isinstance(msg, (dict, list, tuple, set)):
            if not cfg.print_disabled:
                timestamp = Clogger._getTimestamp(cfg)
                source = f" {Fore.WHITE}{Style.DIM}{Clogger._getCaller()}{Style.RESET_ALL} |" if cfg.show_source_file else ""
                print(f"{timestamp}{tag_part}{source}", flush=cfg.force_flush)
                pprint(msg)
            if cfg.write_to_file:
                buf = io.StringIO()
                pprint(msg, stream=buf)
                source_part = f" {Clogger._getCaller()} |" if cfg.show_source_file else ""
                with open(cfg.log_file_path, "a") as f:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {clean_tag_part}{source_part}\n{buf.getvalue()}")
            return

        timestamp = Clogger._getTimestamp(cfg)

        if cfg.show_source_file:
            caller = Clogger._getCaller()
            if cfg.disable_colors:
                source = f" {caller} |"
            else:
                source = f" {Fore.WHITE}{Style.DIM}{caller}{Style.RESET_ALL} |"
        else:
            source = ""

        if not cfg.print_disabled:
            sep = " " if (tag_part or source or timestamp) else ""
            line = f"{timestamp}{tag_part}{source}{sep}{msg}"
            print(line, flush=cfg.force_flush)

        if cfg.write_to_file:
            source_part = f" {Clogger._getCaller()} |" if cfg.show_source_file else ""
            clean_ts = time.strftime('%Y-%m-%d %H:%M:%S')
            clean_sep = " " if (clean_ts or clean_tag_part or source_part) else ""
            clean_line = f"{clean_ts} {clean_tag_part}{source_part}{clean_sep}{msg}"
            with open(cfg.log_file_path, "a") as f:
                f.write(clean_line + "\n")

    @staticmethod
    def make_log(
        tag: str,
        color: CloggerColor = CloggerColor.CYAN,
        level: LogLevel = LogLevel.INFO,
        settings_override: dict | None = None,
    ):
        """
        Returns a logger function that logs with the given tag, color, and level.

        settings_override sets a baseline baked into every call of the returned
        function. The returned function accepts its own settings_override that
        layers on top, with call-time values taking priority.

        The returned function has the signature:
            logger(msg: str, settings_override: dict | None = None)
        """
        formatted_tag = f"[{tag.upper()}]"
        baseline_cfg = Clogger._resolve_config(settings_override)

        def logger(msg: str, settings_override: dict | None = None):
            f"""Log a [{tag.upper()}] message."""
            cfg = Clogger._resolve_config(settings_override, base=baseline_cfg)
            Clogger._log(formatted_tag, msg, color, level, cfg)

        return logger

    @staticmethod
    def log(tag: str, msg: str, settings_override: dict | None = None, color: CloggerColor = CloggerColor.CYAN):
        """Log with a custom tag. Equal log level to INFO."""
        cfg = Clogger._resolve_config(settings_override)
        Clogger._log(f"[{tag.upper()}]", msg, color, LogLevel.INFO, cfg)

    @staticmethod
    def error(msg: str, settings_override: dict | None = None, exc: type[Exception] | None = None):
        """Log an error message and optionally raise an exception."""
        cfg = Clogger._resolve_config(settings_override)
        Clogger._log("[ERROR]", msg, CloggerColor.RED, LogLevel.ERROR, cfg)

        if exc:
            raise exc(msg)  

    @staticmethod
    def warn(msg: str, settings_override: dict | None = None):
        """Log a warning message."""
        cfg = Clogger._resolve_config(settings_override)
        Clogger._log("[WARN]", msg, CloggerColor.YELLOW, LogLevel.WARN, cfg)

    @staticmethod
    def info(msg: str, settings_override: dict | None = None):
        """Log an info message."""
        cfg = Clogger._resolve_config(settings_override)
        Clogger._log("[INFO]", msg, CloggerColor.BLUE, LogLevel.INFO, cfg)

    @staticmethod
    def action(msg: str, settings_override: dict | None = None):
        """Log an action message."""
        cfg = Clogger._resolve_config(settings_override)
        Clogger._log("[ACTION]", msg, CloggerColor.GREEN, LogLevel.ACTION, cfg)

    @staticmethod
    def debug(msg: str, settings_override: dict | None = None):
        """Log a debug message. Respects both debug_enabled and min_log_level."""
        cfg = Clogger._resolve_config(settings_override)
        if cfg.debug_enabled:
            Clogger._log("[DEBUG]", msg, CloggerColor.MAGENTA, LogLevel.DEBUG, cfg)

    @staticmethod
    def log_errors(func):
        """Decorator that logs exceptions before re-raising them."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                Clogger.error(f"{func.__name__} failed: {e}")
                raise
        return wrapper


# disable colors automatically if not in a TTY
if not sys.stdout.isatty():
    Fore.GREEN = Fore.RED = Fore.CYAN = Fore.BLUE = Fore.MAGENTA = Fore.YELLOW = ""
    Back.BLACK = Back.RESET = Style.RESET_ALL = Style.DIM = ""