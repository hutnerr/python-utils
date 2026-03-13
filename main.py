from pyutils import Clogger, CloggerColor, ClogobjFactory, LogLevel, CloggerOverrideFactory, CloggerSetting, Clogobj, CloggerConfig


# ─── Clogger: basic log levels ───────────────────────────────────────────────

Clogger.info("Server started.")
Clogger.warn("High memory usage.")
Clogger.debug("Request payload: {...}")
Clogger.action("User clicked submit.")
Clogger.log("BOOT", "Config loaded.")

try:
    Clogger.error("Failed to connect.", exc=KeyError)
except KeyError:
    pass


# ─── Clogger: global config swapping ─────────────────────────────────────────

Clogger.config = CloggerConfig(min_log_level=LogLevel.WARN)
Clogger.info("This will be suppressed — below WARN.")
Clogger.warn("This prints — at WARN level.")

Clogger.config = CloggerConfig(disable_colors=True, use_tag=False)
Clogger.info("No colors, no tag.")

Clogger.config = CloggerConfig()  # reset to defaults


# ─── Clogger: per-call overrides ─────────────────────────────────────────────

Clogger.info("Verbose trace.", settings_override=CloggerOverrideFactory.verbose())
Clogger.error("Saved quietly.", settings_override=CloggerOverrideFactory.file_only("errors.log"))
Clogger.debug("Dict dump.", settings_override=CloggerOverrideFactory.pretty())

Clogger.info("Verbose and saved.", settings_override=CloggerOverrideFactory.combine(
    CloggerOverrideFactory.verbose(),
    CloggerOverrideFactory.write_to_file("verbose.log"),
    {CloggerSetting.DISABLE_COLORS: True},
))


# ─── Clogger: make_log ───────────────────────────────────────────────────────

log_boot = Clogger.make_log("BOOT", color=CloggerColor.CYAN, level=LogLevel.INFO)
log_boot("App starting up.")

log_trace = Clogger.make_log(
    "TRACE",
    color=CloggerColor.MAGENTA,
    settings_override={CloggerSetting.SIMPLIFY_TIMESTAMPS: False},
)
log_trace("Deep trace.")
log_trace("Deep trace, no source.", settings_override={CloggerSetting.SHOW_SOURCE_FILE: False})


# ─── Clogobj: presets ────────────────────────────────────────────────────────

verbose_logger = ClogobjFactory.verbose()
silent_logger  = ClogobjFactory.silent()
file_logger    = ClogobjFactory.file_only("run.log")

verbose_logger.info("Full timestamps and source shown.")
silent_logger.error("No output at all.")
file_logger.warn("Written to run.log only.")


# ─── Clogobj: named module logger ────────────────────────────────────────────

db_logger = ClogobjFactory.for_module("Database")
db_logger.info("Connection established.")
db_logger.warn("Slow query detected.")


# ─── Clogobj: make_log on an instance ────────────────────────────────────────

auth = Clogobj(
    settings=CloggerConfig(simplify_timestamps=False),
    name="Auth",
)

log_token = auth.make_log("TOKEN", color=CloggerColor.YELLOW, level=LogLevel.WARN)
log_token("Invalid token.")
log_token("Suppressed.", settings_override={CloggerSetting.PRINT_DISABLED: True})


# ─── Clogobj: log_errors decorator ───────────────────────────────────────────

db = ClogobjFactory.for_module("Database")

@db.log_errors
def connect():
    raise ConnectionError("timeout")

try:
    connect()
except ConnectionError:
    pass


# ─── Clogobj: fully custom ───────────────────────────────────────────────────

boot = ClogobjFactory.custom(
    settings=CloggerConfig(simplify_timestamps=False, show_source_file=True),
    name="BOOT",
)
boot.info("App starting up.")
boot.log("INIT", "Config loaded.")