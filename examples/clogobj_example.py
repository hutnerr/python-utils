from pyutils import Clogger, CloggerConfig, LogLevel, Clogobj, ClogobjFactory, CloggerSetting


def demo_default():
    # --- default: behaves like plain Clogger.info ---
    logger = ClogobjFactory.default()
    logger.info("Default info message.")
    logger.debug("Default debug message.")
    logger.warn("Default warning.")
    logger.error("Default error.")
    logger.log("Delegates to Clogger.info by default.")


def demo_verbose():
    # --- verbose: full timestamps, source file shown ---
    logger = ClogobjFactory.verbose()
    logger.info("Full timestamp and source file shown.")
    logger.debug("Verbose debug line.")
    logger.log("log() also uses full verbosity.")


def demo_debug():
    # --- debug: log() delegates to Clogger.debug ---
    logger = ClogobjFactory.debug()
    logger.log("This is routed through Clogger.debug.")
    logger.debug("Explicit debug call.")
    logger.info("Info still works independently.")


def demo_errors_only():
    # --- errors_only: filters below WARN, log() routes to Clogger.error ---
    logger = ClogobjFactory.errors_only()
    logger.debug("Filtered — below WARN threshold.")
    logger.info("Also filtered.")
    logger.warn("Prints — at the threshold.")
    logger.error("Prints — above the threshold.")
    logger.log("log() routes to Clogger.error.")


def demo_silent():
    # --- silent: no output at all, useful for tests ---
    logger = ClogobjFactory.silent()
    logger.info("You won't see this.")
    logger.error("Or this.")
    print("(silent logger produced no output above)")


def demo_file_only():
    # --- file_only: no terminal output, writes to disk ---
    logger = ClogobjFactory.file_only("demo.log")
    logger.info("Written to demo.log only — not printed.")
    logger.error("Error also silently saved.")
    print("(file_only logger wrote to demo.log — check the file)")


def demo_for_module():
    # --- for_module: pre-tagged with a component name ---
    db_logger   = ClogobjFactory.for_module("Database")
    auth_logger = ClogobjFactory.for_module("AuthService", log_func=Clogger.warn)
    api_logger  = ClogobjFactory.for_module("API", log_func=Clogger.debug)

    db_logger.tagged("Connection established")       # [Database] ...
    db_logger.tagged("Query timeout", tag="SLOW")    # one-off tag override: [SLOW] ...

    auth_logger.tagged("User logged in")             # [AuthService] as WARNING
    auth_logger.log("Delegates to Clogger.warn.") 

    api_logger.tagged("GET /users 200")              # [API] as DEBUG
    api_logger.tagged("POST /login 401", tag="WARN") # one-off: [WARN]


def demo_for_file():
    # --- for_file: always writes to a specific file, optionally also prints ---
    both_logger  = ClogobjFactory.for_file("output.log", also_print=True)
    quiet_logger = ClogobjFactory.for_file("output.log", also_print=False)

    both_logger.info("Printed and saved to output.log.")
    quiet_logger.info("Saved to output.log only — not printed.")


def demo_custom():
    # --- custom: full control over config, tag, and default log func ---
    boot_logger = ClogobjFactory.custom(
        settings=CloggerConfig(simplify_timestamps=False, show_source_file=True),
        default_tag="BOOT",
        default_log_func=Clogger.info,
    )
    boot_logger.log("App is starting up.")
    boot_logger.tagged("Config loaded.")
    boot_logger.tagged("DB connected.", tag="DB")

    error_logger = ClogobjFactory.custom(
        settings=CloggerConfig(min_log_level=LogLevel.WARN, write_to_file=True, log_file_path="errors.log"),
        default_tag="ERR",
        default_log_func=Clogger.error,
    )
    error_logger.log("Critical failure — routed to Clogger.error, saved to errors.log.")
    error_logger.tagged("Unhandled exception.")


def demo_per_call_override():
    # --- per-call overrides still work on top of instance settings ---
    logger = ClogobjFactory.verbose()
    logger.info("Normal verbose output.")
    logger.info("Timestamp hidden just for this call.",
                settings_override={CloggerSetting.TIMESTAMPS_ENABLED: False})
    logger.info("Back to normal verbose output.")


def test_clogobj():
    demo_default()
    demo_verbose()
    demo_debug()
    demo_errors_only()
    demo_silent()
    demo_file_only()
    demo_for_module()
    demo_for_file()
    demo_custom()
    demo_per_call_override()

if __name__ == "__main__":
    test_clogobj()