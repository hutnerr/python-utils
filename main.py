from examples.clogger_example import test_clogger
from examples.clogobj_example import test_clogobj

from pyutils import get_env
from pyutils import Clogger

if __name__ == "__main__":
    # test_clogger()
    # test_clogobj()

    path = get_env("PATH")
    if path:
        print(f"PATH: {path}")

    key = get_env("NON_EXISTENT_KEY")
    if key:
        Clogger.error(f"Key found: {key}")
    else:
        Clogger.error("Key not found", exc=KeyError)