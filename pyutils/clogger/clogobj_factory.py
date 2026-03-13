from .clogobj import Clogobj
from .clogger import CloggerConfig, LogLevel


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
        logger.info("User logged in")  # [AuthService][INFO] | User logged in
    """

    @staticmethod
    def default() -> Clogobj:
        """Standard logger with all defaults."""
        return Clogobj()

    @staticmethod
    def verbose() -> Clogobj:
        """Full timestamps, source file shown."""
        return Clogobj(
            settings=CloggerConfig(simplify_timestamps=False, show_source_file=True),
        )

    @staticmethod
    def quiet() -> Clogobj:
        """No terminal output — writes to clogger.log only."""
        return Clogobj(
            settings=CloggerConfig(print_disabled=True, write_to_file=True),
        )

    @staticmethod
    def debug() -> Clogobj:
        """Debug-focused logger with simplified timestamps."""
        return Clogobj(
            settings=CloggerConfig(debug_enabled=True, simplify_timestamps=True),
        )

    @staticmethod
    def silent() -> Clogobj:
        """No output at all. Useful for tests or temporarily muting a logger."""
        return Clogobj(
            settings=CloggerConfig(print_disabled=True),
        )

    @staticmethod
    def errors_only() -> Clogobj:
        """Only WARN and above."""
        return Clogobj(
            settings=CloggerConfig(min_log_level=LogLevel.WARN),
        )

    @staticmethod
    def file_only(path: str = "clogger.log") -> Clogobj:
        """Suppresses terminal output, writes everything to a specific file."""
        return Clogobj(
            settings=CloggerConfig(print_disabled=True, write_to_file=True, log_file_path=path),
        )

    @staticmethod
    def for_module(module_name: str) -> Clogobj:
        """
        Logger pre-tagged with a module or component name.
        The name will appear before the level tag on every log line.

        Example:
            logger = ClogobjFactory.for_module("Database")
            logger.info("Connection established")  # [Database][INFO] | Connection established
        """
        return Clogobj(name=module_name)

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
        name: str = None,
        show_name: bool = True,
    ) -> Clogobj:
        """
        Fully custom logger — pass in whatever config and name you want.

        Example:
            logger = ClogobjFactory.custom(
                settings=CloggerConfig(debug_enabled=False),
                name="BOOT",
            )
        """
        return Clogobj(
            settings=settings,
            name=name,
            show_name=show_name,
        )