from .clogobj import Clogobj
from .clogger import Clogger, CloggerConfig, LogLevel


class ClogobjFactory:
    """
    Factory class for creating pre-configured Clogobj instances.

    Each method returns a ready-to-use Clogobj tailored for a specific
    logging purpose. All instances are independent and do not affect
    global Clogger.config.

    Examples:
        logger = ClogobjFactory.verbose()
        logger.info("Detailed output with full timestamps.")

        logger = ClogobjFactory.for_module("AuthService")
        logger.tagged("User logged in")   # [AuthService] User logged in
    """

    @staticmethod
    def default() -> Clogobj:
        """Standard logger with all defaults."""
        return Clogobj()

    @staticmethod
    def verbose() -> Clogobj:
        """Full timestamps, source file shown, delegates log() to info."""
        return Clogobj(
            settings=CloggerConfig(simplify_timestamps=False, show_source_file=True),
            default_log_func=Clogger.info,
        )

    @staticmethod
    def quiet() -> Clogobj:
        """No terminal output — writes to clogger.log only."""
        return Clogobj(
            settings=CloggerConfig(print_disabled=True, write_to_file=True),
        )

    @staticmethod
    def debug() -> Clogobj:
        """Debug-focused logger — log() delegates to Clogger.debug."""
        return Clogobj(
            settings=CloggerConfig(debug_enabled=True, simplify_timestamps=True),
            default_log_func=Clogger.debug,
        )

    @staticmethod
    def silent() -> Clogobj:
        """No output at all. Useful for tests or temporarily muting a logger."""
        return Clogobj(
            settings=CloggerConfig(print_disabled=True),
        )

    @staticmethod
    def errors_only() -> Clogobj:
        """Only WARN and above — log() delegates to Clogger.error."""
        return Clogobj(
            settings=CloggerConfig(min_log_level=LogLevel.WARN),
            default_log_func=Clogger.error,
        )

    @staticmethod
    def file_only(path: str = "clogger.log") -> Clogobj:
        """Suppresses terminal output, writes everything to a specific file."""
        return Clogobj(
            settings=CloggerConfig(print_disabled=True, write_to_file=True, log_file_path=path),
        )

    @staticmethod
    def for_module(module_name: str, log_func: callable = None) -> Clogobj:
        """
        Logger pre-tagged with a module or component name.
        tagged() calls will use the module name automatically.

        Example:
            logger = ClogobjFactory.for_module("Database")
            logger.tagged("Connection established")  # [Database] Connection established
        """
        return Clogobj(
            default_tag=module_name,
            default_log_func=log_func or Clogger.info,
        )

    @staticmethod
    def for_file(path: str, also_print: bool = True) -> Clogobj:
        """
        Logger that always writes to a specific file.
        Optionally also prints to terminal (default: True).
        """
        return Clogobj(
            settings=CloggerConfig(
                write_to_file=True,
                log_file_path=path,
                print_disabled=not also_print,
            ),
        )

    @staticmethod
    def custom(
        settings: CloggerConfig = None,
        default_tag: str = "LOG",
        default_log_func: callable = None,
    ) -> Clogobj:
        """
        Fully custom logger — pass in whatever config, tag, and log func you want.

        Example:
            logger = ClogobjFactory.custom(
                settings=CloggerConfig(debug_enabled=False),
                default_tag="BOOT",
                default_log_func=Clogger.warn,
            )
        """
        return Clogobj(
            settings=settings,
            default_tag=default_tag,
            default_log_func=default_log_func,
        )