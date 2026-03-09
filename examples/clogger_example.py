from pyutils import Clogger, CloggerConfig, CloggerOverrideFactory, CloggerSetting, LogLevel

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


def test_clogger():
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

    demo_pprint(sample_dict, sample_list)
    demo_basics()
    demo_single_overrides()
    demo_file_only()
    demo_combined_overrides()
    demo_raw_override()
    demo_global_config()
    demo_min_log_level()
    demo_print_disabled()
    demo_decorator()


if __name__ == "__main__":
    test_clogger()