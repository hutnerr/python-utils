from examples.clogger_example import test_clogger
from examples.clogobj_example import test_clogobj

from pyutils import get_env
from pyutils import Clogger, CloggerColor, LogLevel, CloggerOverrideFactory, CloggerSetting, Clogobj, CloggerConfig

if __name__ == "__main__":
    # test = Clogger.make_log(
    #     tag="TEST",
    #     color=CloggerColor.GREEN,
    #     level=LogLevel.ERROR,
    #     settings_override=CloggerOverrideFactory.combine(
    #         CloggerOverrideFactory.clean(),
    #         { 
    #             CloggerSetting.USE_TAG : False,
    #             CloggerSetting.DISABLE_COLORS : True
    #         }
    #     )
    # )
    
    # test("This is a test message.")
    # print("This is a test message.")
    
    # Clogger.log("TEST", "This is a clean test message", settings_override=CloggerOverrideFactory.clean())
    # Clogger.log("TEST", "This is a print test message", settings_override=CloggerOverrideFactory.print_output())
    
    Clogger.warn("This is a warning.", settings_override={ CloggerSetting.DISABLE_COLORS: True })
    
    
    obj = Clogobj()
    
    obj.log("log", "This is a log message.")
    obj.error("This is a test message.")
    
    