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


@dataclass
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

    Examples:
        Clogger.config = CloggerConfig(disabled=True)
        Clogger.config = CloggerConfig.from_dict({"disabled": True, "force_flush": False})
        Clogger.config = CloggerConfig.from_dict({CloggerSetting.DISABLED: True})
    """
    disabled:            bool     = False
    debug_enabled:       bool     = True
    timestamps_enabled:  bool     = True
    simplify_timestamps: bool     = True
    show_source_file:    bool     = True
    force_flush:         bool     = True
    pprint_enabled:      bool     = False
    write_to_file:       bool     = False
    log_file_path:       str      = "clogger.log"
    min_log_level:       LogLevel = LogLevel.DEBUG
    print_disabled:      bool     = False  # if True, suppresses terminal output but still writes to file if write_to_file is enabled

    @classmethod
    def from_dict(cls, settings: dict) -> "CloggerConfig":
        """
        Create a CloggerConfig from a dict using CloggerSetting enum keys, plain strings, or both.

        Examples:
            CloggerConfig.from_dict({CloggerSetting.DISABLED: True})
            CloggerConfig.from_dict({"disabled": True, "force_flush": False})
            CloggerConfig.from_dict({CloggerSetting.DISABLED: True, "force_flush": False})
        """
        normalized = {}
        for k, v in settings.items():
            key = k.value if isinstance(k, CloggerSetting) else k
            if key in cls.__dataclass_fields__:
                normalized[key] = v
        return cls(**normalized)


class CloggerOverrideFactory:
    """
    Factory for building common settings_override dicts to pass into any Clogger log method.
    
    Might also be useful to pass to Clogger.config.from_dict() for quick config changes. 

    These are convenience helpers — you can always pass a raw dict instead.

    Example:
        Clogger.info("clean output", settings_override=CloggerOverrideFactory.clean())
        Clogger.debug("no source", settings_override=CloggerOverrideFactory.no_source())
    """
    
    @staticmethod
    def combine(*overrides: dict) -> dict:
        """
        Merge multiple override dicts into one. Later dicts take priority on conflicts.

        Example:
            CloggerOverrideFactory.combine(
                CloggerOverrideFactory.verbose(),
                CloggerOverrideFactory.write_to_file()
            )
        """
        result = {}
        for override in overrides:
            result.update(override)
        return result

    @staticmethod
    def clean() -> dict:
        """no timestamps, no source file. plain readable output."""
        return {
            CloggerSetting.TIMESTAMPS_ENABLED: False,
            CloggerSetting.SHOW_SOURCE_FILE:   False,
        }

    @staticmethod
    def silent() -> dict:
        """disables output entirely for this call."""
        return {
            CloggerSetting.DISABLED: True,
        }

    @staticmethod
    def verbose() -> dict:
        """full timestamps, source file shown, debug enabled. Useful for detailed tracing."""
        return {
            CloggerSetting.TIMESTAMPS_ENABLED:  True,
            CloggerSetting.SIMPLIFY_TIMESTAMPS: False,
            CloggerSetting.SHOW_SOURCE_FILE:    True,
            CloggerSetting.DEBUG_ENABLED:       True,
        }

    @staticmethod
    def no_source() -> dict:
        """hides the source file and line number for this call."""
        return {
            CloggerSetting.SHOW_SOURCE_FILE: False,
        }

    @staticmethod
    def no_timestamp() -> dict:
        """hides the timestamp for this call."""
        return {
            CloggerSetting.TIMESTAMPS_ENABLED: False,
        }

    @staticmethod
    def write_to_file(path: str = "clogger.log") -> dict:
        """enables file writing for this call, optionally to a specific path."""
        return {
            CloggerSetting.WRITE_TO_FILE: True,
            CloggerSetting.LOG_FILE_PATH: path,
        }

    @staticmethod
    def print_output() -> dict:
        """strips all decorations (timestamps, source, colors via force_flush) for clean
        print-style output. Useful when logging a final result meant to be read as plain text."""
        return {
            CloggerSetting.TIMESTAMPS_ENABLED: False,
            CloggerSetting.SHOW_SOURCE_FILE:   False,
            CloggerSetting.FORCE_FLUSH:        True,
        }

    @staticmethod
    def file_only(path: str = "clogger.log") -> dict:
        """silences terminal output and writes only to a file.
        unlike disabled, the log still happens — just not printed to the terminal."""
        return {
            CloggerSetting.PRINT_DISABLED: True,
            CloggerSetting.WRITE_TO_FILE:  True,
            CloggerSetting.LOG_FILE_PATH:  path,
        }

    @staticmethod
    def pretty() -> dict:
        """enables pretty-printing for complex objects like dicts and lists."""
        return {
            CloggerSetting.PPRINT_ENABLED: True,
        }


class Clogger:
    config: CloggerConfig = CloggerConfig()

    @staticmethod
    def _resolve_config(settings_override: dict | None) -> CloggerConfig:
        """Merge global config with a per-call override dict, returning a fresh CloggerConfig."""
        if not settings_override:
            return Clogger.config
        
        base = Clogger.config.__dict__.copy()
        override = CloggerConfig.from_dict(settings_override).__dict__

        # only apply keys that were explicitly passed in the override
        normalized_keys = {
            (k.value if isinstance(k, CloggerSetting) else k)
            for k in settings_override.keys()
        }
        merged = {k: (override[k] if k in normalized_keys else v) for k, v in base.items()}
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
    def _log(tag: str, msg: str, color: str = "", level: LogLevel = LogLevel.DEBUG, cfg: CloggerConfig = None):
        cfg = cfg or Clogger.config

        if cfg.disabled:
            return
        if level.value > cfg.min_log_level.value:
            return

        # if pprint is enabled and msg is a complex object, pretty-print it below the tag line
        if cfg.pprint_enabled and isinstance(msg, (dict, list, tuple, set)):
            if not cfg.print_disabled:
                timestamp = Clogger._getTimestamp(cfg)
                source = f" {Fore.WHITE}{Style.DIM}{Clogger._getCaller()}{Style.RESET_ALL} |" if cfg.show_source_file else ""
                print(f"{timestamp}{color}{tag:<8}{Style.RESET_ALL} |{source}", flush=cfg.force_flush)
                pprint(msg)
            if cfg.write_to_file:
                buf = io.StringIO()
                pprint(msg, stream=buf)
                source_part = f" {Clogger._getCaller()} |" if cfg.show_source_file else ""
                with open(cfg.log_file_path, "a") as f:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {tag:<8} |{source_part}\n{buf.getvalue()}")
            return

        timestamp = Clogger._getTimestamp(cfg)

        if cfg.show_source_file:
            caller = Clogger._getCaller()
            source = f" {Fore.WHITE}{Style.DIM}{caller}{Style.RESET_ALL} |"
        else:
            source = ""

        if not cfg.print_disabled:
            line = f"{timestamp}{color}{tag:<8}{Style.RESET_ALL} |{source} {msg}"
            print(line, flush=cfg.force_flush)

        if cfg.write_to_file:
            source_part = f" {Clogger._getCaller()} |" if cfg.show_source_file else ""
            clean_line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {tag:<8} |{source_part} {msg}"
            with open(cfg.log_file_path, "a") as f:
                f.write(clean_line + "\n")

    @staticmethod
    def log(tag: str, msg: str, settings_override: dict | None = None):
        """Log with a custom tag. Equal log level to INFO."""
        cfg = Clogger._resolve_config(settings_override)
        Clogger._log(f"[{tag.upper()}]", msg, Fore.CYAN, LogLevel.INFO, cfg)

    @staticmethod
    def error(msg: str, settings_override: dict | None = None):
        """Log an error message."""
        cfg = Clogger._resolve_config(settings_override)
        Clogger._log("[ERROR]", msg, Fore.RED, LogLevel.ERROR, cfg)

    @staticmethod
    def warn(msg: str, settings_override: dict | None = None):
        """Log a warning message."""
        cfg = Clogger._resolve_config(settings_override)
        Clogger._log("[WARN]", msg, Fore.YELLOW, LogLevel.WARN, cfg)

    @staticmethod
    def info(msg: str, settings_override: dict | None = None):
        """Log an info message."""
        cfg = Clogger._resolve_config(settings_override)
        Clogger._log("[INFO]", msg, Fore.BLUE, LogLevel.INFO, cfg)

    @staticmethod
    def action(msg: str, settings_override: dict | None = None):
        """Log an action message."""
        cfg = Clogger._resolve_config(settings_override)
        Clogger._log("[ACTION]", msg, Fore.GREEN, LogLevel.ACTION, cfg)

    @staticmethod
    def debug(msg: str, settings_override: dict | None = None):
        """Log a debug message. Respects both debug_enabled and min_log_level."""
        cfg = Clogger._resolve_config(settings_override)
        if cfg.debug_enabled:
            Clogger._log("[DEBUG]", msg, Fore.MAGENTA, LogLevel.DEBUG, cfg)

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


def demo_pprint(sample_dict, sample_list):
    # --- pprint: pretty-printing complex objects ---
    Clogger.config = CloggerConfig(pprint_enabled=True)
    Clogger.debug(sample_dict)
    Clogger.info(sample_list)
    Clogger.config = CloggerConfig()  # reset

    # per-call pprint via override
    Clogger.debug(sample_dict, settings_override=CloggerOverrideFactory.pretty())

    # combined: pretty-print and save to file
    Clogger.info(sample_dict, settings_override=CloggerOverrideFactory.combine(
        CloggerOverrideFactory.pretty(),
        CloggerOverrideFactory.write_to_file("pretty.log")
    ))

    # pprint vs no pprint
    Clogger.info(sample_dict, settings_override=CloggerOverrideFactory.pretty())
    Clogger.info(sample_dict)


def demo_basics():
    # --- basics ---
    Clogger.info("This is an info message.")
    Clogger.warn("This is a warning.")
    Clogger.error("This is an error.")
    Clogger.debug("This is a debug message.")
    Clogger.action("User clicked the button.")
    Clogger.log("BOOT", "Custom tag example.")


def demo_single_overrides():
    # --- single overrides ---
    Clogger.info("No timestamp or source.", settings_override=CloggerOverrideFactory.clean())
    Clogger.debug("This will not print at all.", settings_override=CloggerOverrideFactory.silent())
    Clogger.info("Full date and source shown.", settings_override=CloggerOverrideFactory.verbose())
    Clogger.warn("Source hidden.", settings_override=CloggerOverrideFactory.no_source())
    Clogger.error("Timestamp hidden.", settings_override=CloggerOverrideFactory.no_timestamp())
    Clogger.info("Written to default log file too.", settings_override=CloggerOverrideFactory.write_to_file())
    Clogger.error("Written to a specific file.", settings_override=CloggerOverrideFactory.write_to_file("errors.log"))
    Clogger.info("Plain print-style output.", settings_override=CloggerOverrideFactory.print_output())


def demo_file_only():
    # --- file_only: no terminal output, still writes to disk ---
    Clogger.info("Silent but saved to disk.", settings_override=CloggerOverrideFactory.file_only())
    Clogger.error("Error saved quietly to errors.log.", settings_override=CloggerOverrideFactory.file_only("errors.log"))
    Clogger.debug("Debug trace saved, not printed.", settings_override=CloggerOverrideFactory.file_only("debug.log"))


def demo_combined_overrides():
    # --- combining overrides ---
    Clogger.debug("Verbose output also saved to file.", settings_override=CloggerOverrideFactory.combine(
        CloggerOverrideFactory.verbose(),
        CloggerOverrideFactory.write_to_file("verbose.log")
    ))
    Clogger.info("Clean output also saved to file.", settings_override=CloggerOverrideFactory.combine(
        CloggerOverrideFactory.print_output(),
        CloggerOverrideFactory.write_to_file("output.log")
    ))
    Clogger.error("No source, but written to disk.", settings_override=CloggerOverrideFactory.combine(
        CloggerOverrideFactory.no_source(),
        CloggerOverrideFactory.write_to_file("errors.log")
    ))
    Clogger.debug("Verbose but completely silent — only saved to file.", settings_override=CloggerOverrideFactory.combine(
        CloggerOverrideFactory.verbose(),
        CloggerOverrideFactory.file_only("verbose.log")
    ))
    Clogger.info("Print-style output also saved quietly to file.", settings_override=CloggerOverrideFactory.combine(
        CloggerOverrideFactory.print_output(),
        CloggerOverrideFactory.file_only("output.log")
    ))


def demo_raw_override():
    # --- raw dict override (no factory needed) ---
    Clogger.info("One-off tweak without factory.", settings_override={
        CloggerSetting.SIMPLIFY_TIMESTAMPS: False,
        CloggerSetting.SHOW_SOURCE_FILE: False,
    })


def demo_global_config():
    # --- changing global config mid-run ---
    Clogger.config = CloggerConfig(debug_enabled=False, simplify_timestamps=False)
    Clogger.debug("This won't print — debug is now off globally.")
    Clogger.info("Full timestamps globally from here on.")
    Clogger.config = CloggerConfig()  # reset


def demo_min_log_level():
    # --- min_log_level filtering ---
    Clogger.config = CloggerConfig(min_log_level=LogLevel.WARN)
    Clogger.debug("Filtered out — below WARN.")
    Clogger.info("Also filtered out.")
    Clogger.warn("This prints — at the threshold.")
    Clogger.error("This prints — above the threshold.")
    Clogger.config = CloggerConfig()  # reset


def demo_print_disabled():
    # --- global print_disabled: file-only mode for the whole run ---
    Clogger.config = CloggerConfig(print_disabled=True, write_to_file=True, log_file_path="silent_run.log")
    Clogger.info("Nothing on screen — all going to silent_run.log.")
    Clogger.error("Same here.")
    Clogger.config = CloggerConfig()  # reset


def demo_decorator():
    # --- decorator ---
    @Clogger.log_errors
    def risky():
        raise ValueError("something went wrong")

    try:
        risky()
    except ValueError:
        pass  # error was already logged by the decorator


if __name__ == "__main__":
    sample_dict = {
        "users": {
            "alice": {
                "age": 30,
                "emails": ["alice@example.com", "alice.work@example.com"],
                "active": True,
                "preferences": {
                    "theme": "dark",
                    "notifications": {"email": True, "sms": False},
                },
            },
            "bob": {
                "age": 25,
                "emails": ["bob@example.com"],
                "active": False,
                "preferences": {
                    "theme": "light",
                    "notifications": {"email": False, "sms": True},
                },
            },
            "carol": {
                "age": 28,
                "emails": [],
                "active": True,
                "preferences": {
                    "theme": "dark",
                    "notifications": {"email": True, "sms": True},
                },
            },
        }
    }
    sample_list = [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]

    # demo_pprint(sample_dict, sample_list)
    demo_basics()
    demo_single_overrides()
    demo_file_only()
    demo_combined_overrides()
    demo_raw_override()
    demo_global_config()
    demo_min_log_level()
    demo_print_disabled()
    demo_decorator()