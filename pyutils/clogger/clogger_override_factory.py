from .clogger import *

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

