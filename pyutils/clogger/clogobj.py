from .clogger import *
from .clogger_override_factory import CloggerOverrideFactory

class Clogobj:
    def __init__(
        self,
        settings: CloggerConfig = None,
        default_tag: str = "LOG",
        default_log_func: callable = None,
    ):
        self.settings = settings or CloggerConfig()
        self.default_tag = default_tag
        self.default_log_func = default_log_func or Clogger.info

    def _resolve_override(self, settings_override):
        if settings_override is None:
            return self.settings.to_dict()
        return {**self.settings.to_dict(), **settings_override}

    def log(self, message, settings_override=None):
        """Uses default_log_func if no custom tag is set, otherwise uses Clogger.log with default_tag."""
        self.default_log_func(message, settings_override=self._resolve_override(settings_override))

    def tagged(self, message, tag: str = None, settings_override=None):
        """Logs with a tag — uses default_tag if none provided."""
        Clogger.log(tag or self.default_tag, message, settings_override=self._resolve_override(settings_override))

    def debug(self, message, settings_override=None):
        Clogger.debug(message, settings_override=self._resolve_override(settings_override))

    def info(self, message, settings_override=None):
        Clogger.info(message, settings_override=self._resolve_override(settings_override))

    def warn(self, message, settings_override=None):
        Clogger.warn(message, settings_override=self._resolve_override(settings_override))

    def error(self, message, settings_override=None):
        Clogger.error(message, settings_override=self._resolve_override(settings_override))

    def action(self, message, settings_override=None):
        Clogger.action(message, settings_override=self._resolve_override(settings_override))

    @classmethod
    def factory(cls, preset: str) -> "Clogobj":
        presets = {
            "verbose": cls(CloggerConfig(simplify_timestamps=False, show_source_file=True)),
            "quiet":   cls(CloggerConfig(print_disabled=True, write_to_file=True)),
            "debug":   cls(CloggerConfig(debug_enabled=True, simplify_timestamps=True), default_log_func=Clogger.debug),
            "silent":  cls(CloggerConfig(print_disabled=True)),
            "errors":  cls(CloggerConfig(min_log_level=LogLevel.WARN), default_log_func=Clogger.error),
        }
        if preset not in presets:
            raise ValueError(f"Unknown preset '{preset}'. Choose from: {list(presets)}")
        return presets[preset]