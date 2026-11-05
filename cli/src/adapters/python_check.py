"""Native unittest execution; a separate report keeps learner stdout out of protocol."""
import importlib.util
import json
from pathlib import Path
import sys
import traceback
import types
import unittest

report_path, *selectors = sys.argv[1:]
answer_path = Path("answers.py").resolve()


def in_answer(error):
    _, exception, tb = error
    if isinstance(exception, SyntaxError):
        return Path(exception.filename or "").resolve() == answer_path
    while tb is not None:
        if Path(tb.tb_frame.f_code.co_filename).resolve() == answer_path:
            return True
        tb = tb.tb_next
    return False


def flatten(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from flatten(test)
        else:
            yield test


def load_source(name, path):
    # -B prevents cache writes, not reads. Execute current source directly and
    # register it before execution so normal imports see this same module.
    code = compile(path.read_bytes(), str(path), "exec")
    spec = importlib.util.spec_from_file_location(name, path)
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__spec__ = spec
    module.__loader__ = spec.loader
    module.__package__ = spec.parent
    module.__cached__ = None
    sys.modules[name] = module
    exec(code, module.__dict__)


def check():
    # Compile before loading the harness so answer syntax failures cannot be
    # confused with unittest's synthetic loader-error tests.
    try:
        load_source("answers", answer_path)
    except Exception:
        error = sys.exc_info()
        traceback.print_exc()
        return {"outcome": "failed" if in_answer(error) else "indeterminate",
                "reason": "answer import failed"}

    loader = unittest.TestLoader()
    try:
        load_source("test_exercises", Path("test_exercises.py").resolve())
        suite = loader.loadTestsFromNames(selectors)
    except Exception:
        traceback.print_exc()
        return {"outcome": "blocked", "reason": "unittest harness could not be imported"}
    if loader.errors:
        for error in loader.errors:
            print(error, file=sys.stderr)
        return {"outcome": "blocked", "reason": "unittest harness/selector could not be loaded"}
    ids = [test.id() for test in flatten(suite)]
    if not selectors or sorted(ids) != sorted(selectors):
        return {"outcome": "blocked", "reason": "intended unittest tests were not selected"}

    class Result(unittest.TextTestResult):
        uncertain = False

        def addError(self, test, error):
            if not in_answer(error):
                self.uncertain = True
            super().addError(test, error)

        def addSubTest(self, test, subtest, error):
            if error and not issubclass(error[0], AssertionError) and not in_answer(error):
                self.uncertain = True
            super().addSubTest(test, subtest, error)

    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    if result.testsRun != len(selectors) or result.skipped or result.expectedFailures or result.unexpectedSuccesses:
        return {"outcome": "indeterminate", "reason": "not all intended tests ran normally"}
    if result.uncertain:
        return {"outcome": "indeterminate", "reason": "test error could not be attributed to answers"}
    return {"outcome": "passed" if result.wasSuccessful() else "failed", "ran": result.testsRun}


try:
    report = check()
except BaseException:
    traceback.print_exc()
    report = {"outcome": "indeterminate", "reason": "Python check interrupted or harness failed"}
with open(report_path, "w", encoding="utf-8") as report_file:
    json.dump(report, report_file)
