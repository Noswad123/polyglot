"""Native Hello contracts. Every mutation and native run uses disposable copies."""

import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from active_fixture import (HELLO_EXAMPLE_PATHS, LANGUAGES,
                            solve, tool_overrides)
import test_rust_cli as cli_fixture


NEW_LANGUAGES = LANGUAGES[2:]
HARNESSES = {"typescript": "check_hello.cjs", "go": "hello_test.go",
             "bash": "check_hello.sh", "lua": "check_hello.lua"}


class AdditionalHelloTests(unittest.TestCase):
    setUpClass = classmethod(cli_fixture.RustCliTests.setUpClass.__func__)
    setUp = cli_fixture.RustCliTests.setUp
    directory = cli_fixture.RustCliTests.directory
    answer = cli_fixture.RustCliTests.answer
    sources = cli_fixture.RustCliTests.sources
    git_files = cli_fixture.RustCliTests.git_files
    execute = cli_fixture.RustCliTests.execute
    assert_code = cli_fixture.RustCliTests.assert_code
    cli = cli_fixture.RustCliTests.cli

    def tools(self, language):
        available = dict(zip(tool_overrides()[::2], tool_overrides()[1::2]))
        required = ("node", "tsc") if language == "typescript" else (language,)
        missing = [name for name in required if "--" + name not in available]
        if missing:
            self.skipTest(f"{language} native check needs host tools: {', '.join(missing)}")
        return {name.removeprefix("--"): path for name, path in available.items()}

    def check(self, language, source=None, code=0, globals=()):
        self.tools(language)
        if source is not None:
            self.answer(language).write_text(source)
        return self.cli("check", language + "/hello", code=code, globals=globals)

    def harness(self, language):
        return self.directory(language) / "tests" / HARNESSES[language]

    def direct(self, language):
        tools = self.tools(language)
        with tempfile.TemporaryDirectory(prefix="polyglot native contract ", dir=self.base) as temporary:
            scratch = Path(temporary)
            report = scratch / "report.json"
            env = {**self.env, "GO111MODULE": "off", "GOWORK": "off", "GOPROXY": "off",
                   "GOSUMDB": "off", "GOTOOLCHAIN": "local", "GOENV": "off"}
            env.pop("GOFLAGS", None)
            if language == "typescript":
                directory = self.directory(language)
                compiler = Path(tools["tsc"]).parent.parent / "lib/typescript.js"
                command = [tools["node"], self.harness(language), compiler, directory,
                           directory / "tests/hello.tsconfig.json", self.answer(language),
                           directory / "tests/hello_api.ts", scratch, report]
            else:
                source = scratch / self.answer(language).name
                harness = scratch / self.harness(language).name
                shutil.copy2(self.answer(language), source)
                shutil.copy2(self.harness(language), harness)
                if language == "go":
                    command = [tools["go"], "test", "-json", "-count=1", "-run", "^TestHello$",
                               source.name, harness.name]
                else:
                    command = [tools[language], harness, source, report]
                    if language == "bash":
                        command.append(scratch / "stdout")
            if language in ("typescript", "lua"):
                capture = scratch / "stdout"
                with capture.open("xb") as stdout:
                    result = subprocess.run([str(arg) for arg in command], cwd=scratch, env=env,
                                            stdin=subprocess.DEVNULL, stdout=stdout,
                                            stderr=subprocess.PIPE, text=True, timeout=90)
                output = capture.read_bytes()
                result.stdout = output.decode()
            else:
                result = self.execute(command, cwd=scratch, env=env)
                output = result.stdout.encode()
                if language == "bash":
                    self.assertEqual(output, b"")
                    output = (scratch / "stdout").read_bytes()
            self.assert_code(result, 0)
            if language == "go":
                events = [json.loads(line) for line in result.stdout.splitlines()]
                self.assertTrue(any(event.get("Test") == "TestHello" and event["Action"] == "run"
                                    for event in events), result.stdout)
                self.assertTrue(any(event.get("Test") == "TestHello" and event["Action"] == "pass"
                                    for event in events), result.stdout)
            else:
                self.assertEqual(output, b"Hello, World!\n")
                state = report.read_text()
                self.assertEqual(json.loads(state)["outcome"] if language == "typescript" else state,
                                 "passed" if language == "typescript" else "passed\n")

    def test_four_blanks_fail_and_copied_examples_pass_direct_and_cli(self):
        for language in NEW_LANGUAGES:
            with self.subTest(language=language):
                self.check(language, code=1)
                solve(self.root, language)
                self.assertEqual(self.answer(language).read_text(), HELLO_EXAMPLE_PATHS[language].read_text())
                self.direct(language)
                self.check(language)
                self.cli("check", language)

    def test_registry_help_menu_and_language_switch_are_tool_free_and_read_only(self):
        missing = self.base / "missing native tool"
        overrides = ("--python", missing, "--cargo", missing, *tool_overrides(missing))
        before, metadata = self.sources(), self.git_files()
        output = self.cli("--help", globals=overrides).stdout
        for flag in ("--node", "--tsc", "--go", "--bash", "--lua"):
            self.assertIn(flag, output)
        for language in NEW_LANGUAGES:
            self.assertIn(language + "/hello", output)
            shown = self.cli("show", language + "/hello", globals=overrides).stdout
            self.assertIn(str(self.answer(language)), shown)
            self.assertNotIn("helloWorld", shown)
            self.assertEqual(self.cli("list", "--language", language, globals=overrides).stdout.split("\t")[0],
                             language + "/hello")
        # Reuse only command/CLI mechanics, not another TestCase's test methods.
        for index, language in enumerate(LANGUAGES, 1):
            with self.subTest(language=language):
                command = [str(self.binary), "--root", str(self.root), *map(str, overrides), "practice"]
                result = subprocess.run(command, cwd=self.cwd, env=self.env, input=f"{index}\nq\n",
                                        capture_output=True, text=True, timeout=45)
                self.assert_code(result, 0)
                self.assertIn("Exercise: " + language + "/hello", result.stdout)
        switches = "".join("language " + language + "\nprompt\n" for language in LANGUAGES)
        command = [str(self.binary), "--root", str(self.root), *map(str, overrides), "practice", "python"]
        result = subprocess.run(command, cwd=self.cwd, env=self.env, input=switches + "q\n",
                                capture_output=True, text=True, timeout=45)
        self.assert_code(result, 0)
        for language in LANGUAGES:
            self.assertIn("Exercise: " + language + "/hello", result.stdout)
        self.assertEqual(self.sources(), before)
        self.assertEqual(self.git_files(), metadata)

    def test_missing_tools_block_with_no_install_or_source_writes(self):
        missing = self.base / "missing tool with spaces"
        for language in NEW_LANGUAGES:
            for tool in (("node", "tsc") if language == "typescript" else (language,)):
                with self.subTest(language=language, tool=tool):
                    before, metadata = self.sources(), self.git_files()
                    result = self.cli("check", language + "/hello", code=2, globals=("--" + tool, missing))
                    self.assertIn("Blocked:", result.stderr)
                    if language == "typescript":
                        self.assertIn("npm ci --prefix practice/typescript", result.stderr)
                    self.assertEqual(self.sources(), before)
                    self.assertEqual(self.git_files(), metadata)
                    self.assertFalse((self.directory("typescript") / "node_modules").exists())

    def test_typescript_rejects_static_wrong_signatures_exports_and_syntax(self):
        cases = [
            'export function hello(): string { console.log("Hello, World!"); return "x"; }',
            'export function hello(name: string): void { console.log("Hello, World!"); }',
            'export async function hello(): Promise<void> { console.log("Hello, World!"); }',
            'export const hello = (() => console.log("Hello, World!")) as any;',
            'export default function hello(): void { console.log("Hello, World!"); }',
            'function hello(): void { console.log("Hello, World!"); }',
            'export function hello(): void { const broken = ; }',
        ]
        for source in cases:
            with self.subTest(source=source):
                self.check("typescript", source, code=1)

    def test_typescript_config_probe_and_harness_faults_are_blocked(self):
        self.tools("typescript")
        solve(self.root, "typescript")
        paths = {self.directory("typescript") / "tests/hello.tsconfig.json": '{"compilerOptions": {"module": "invalid"}}',
                 self.directory("typescript") / "tests/hello_api.ts": "type Broken = ;\n",
                 self.harness("typescript"): "const = ;\n"}
        for path, source in paths.items():
            with self.subTest(path=path):
                original = path.read_bytes()
                try:
                    path.write_text(source)
                    self.check("typescript", code=2)
                finally:
                    path.write_bytes(original)

    def test_typescript_runtime_returns_top_level_output_and_early_exit(self):
        cases = [
            ('export function hello(): void { console.log("Hello, World!"); return "wrong" as never; }', 1),
            ('console.log("Hello, World!"); export function hello(): void {}', 1),
            ('declare function require(name: string): { writeSync(fd: number, text: string): number }; require("node:fs").writeSync(1, "Hello, World!\\n"); export function hello(): void {}', 1),
            ('setTimeout(() => console.log("Hello, World!"), 0); export function hello(): void {}', 1),
            ('Promise.resolve().then(() => console.log("Hello, World!")); export function hello(): void {}', 1),
            ('console.log("extra"); export function hello(): void { console.log("Hello, World!"); }', 1),
            ('export function hello(): void { throw new Error("learner panic"); }', 1),
            ('declare const process: { exit(n: number): never }; export function hello(): void { process.exit(0); }', 3),
            ('declare const process: { exit(n: number): never }; console.log(\'{"outcome":"passed","stage":"runtime","reason":"spoof"}\'); process.exit(0); export function hello(): void {}', 3),
        ]
        for source, code in cases:
            with self.subTest(source=source):
                result = self.check("typescript", source, code=code)
                self.assertNotIn("does not satisfy the static contract", result.stdout + result.stderr)
        (self.root / "package.json").write_text('{"type":"module"}\n')
        solve(self.root, "typescript")
        self.check("typescript")

    def test_output_comparison_preserves_case_and_every_newline(self):
        for language in ("typescript", "bash", "lua"):
            for output in ("Hello, World!", "Hello, World!\n\n", "hello, world!\n"):
                with self.subTest(language=language, output=repr(output)):
                    literal = json.dumps(output)
                    source = {
                        "typescript": ('declare const process: { stdout: { write(s: string): void } }; '
                                       f'export function hello(): void {{ process.stdout.write({literal}); }}\n'),
                        "bash": f"hello() {{ printf '%s' '{output}'; }}\n",
                        "lua": f"function hello() io.write({literal}) end\n",
                    }[language]
                    result = self.check(language, source, code=1)
                    combined = result.stdout + result.stderr
                    self.assertIn("Your output:", combined)
                    self.assertIn("Expected output:", combined)
                    self.assertIn(r"Hello, World!\n", combined)

    def test_bash_function_status_api_syntax_and_early_exit(self):
        for source, code in (
            ("hello() { printf 'Hello, World!\\n'; return 7; }\n", 1),
            ("hello() {\n", 1),
            ("other() { printf 'Hello, World!\\n'; }\n", 1),
            ("hello() { printf 'Hello, World!\\n'; exit 0; }\n", 3),
            ("printf 'passed\\n'; exit 0\n", 3),
        ):
            with self.subTest(source=source):
                self.check("bash", source, code=code)

    def test_lua_return_arity_api_syntax_runtime_and_early_exit(self):
        for returns in ("", "return nil", "return true", 'return "Hello, World!"', "return nil, nil"):
            with self.subTest(returns=returns):
                self.check("lua", f'function hello() print("Hello, World!"); {returns} end\n',
                           code=0 if returns in ("", "return nil") else 1)
        for source, code in (
            ("function hello( end\n", 1),
            ("local function hello() print('Hello, World!') end\n", 1),
            ("function hello() error('learner panic') end\n", 1),
            ("function hello() os.exit(0) end\n", 3),
            ("print('passed'); os.exit(0)\n", 3),
        ):
            with self.subTest(source=source):
                self.check("lua", source, code=code)
        self.check("lua", 'local output = io.stdout\nfunction hello() output:write("Hello, World!\\n") end\n')
        self.direct("lua")

    def test_bash_deferred_stdout_cannot_supply_or_extend_greeting(self):
        for bash in (self.tools("bash")["bash"], "/bin/bash"):
            for source, code in (
                ('hello() { :; }\ntrap \'printf "Hello, World!\\n"\' EXIT\n', 1),
                ('hello() { printf "Hello, World!\\n"; }\ntrap \'printf "extra\\n"\' EXIT\n', 1),
                ('exec 3>&1\nhello() { :; }\ntrap \'printf "Hello, World!\\n" >&3\' EXIT\n', 1),
                ('exec 3>&1\nhello() { printf "Hello, World!\\n" >&3; }\ntrap \'printf "extra\\n" >&3\' EXIT\n', 1),
                ('hello() { trap \'printf "Hello, World!\\n"\' EXIT; exit 0; }\n', 3),
                ('exec 3>&1\nhello() { printf "Hello, World!\\n" >&3; }\n', 0),
                ('set -e\nfunction hello { printf "Hello, World!\\n"; }\n', 0),
            ):
                with self.subTest(bash=bash, source=source):
                    self.check("bash", source, code=code, globals=("--bash", bash))

    def test_go_type_and_uninstantiated_generic_api_are_learner_failures(self):
        for source in (
            'package exercises\ntype Hello string\n',
            'package exercises\nfunc Hello[T any]() string { return "Hello, World!" }\n',
        ):
            with self.subTest(source=source):
                self.check("go", source, code=1)

    def test_go_inference_error_in_broken_harness_stays_blocked(self):
        self.tools("go")
        self.harness("go").write_text(
            'package exercises\nimport "testing"\n'
            'var FUNCTION func() string = broken // polyglot:api\n'
            'func TestHello(t *testing.T) {}\n')
        self.check("go", 'package exercises\n'
                   'func broken[T any]() string { return "Hello, World!" }\n', code=2)

    def test_shell_harness_syntax_faults_are_blocked(self):
        for language, broken in (("bash", "if then\n"), ("lua", "local =\n")):
            with self.subTest(language=language):
                self.tools(language)
                solve(self.root, language)
                self.harness(language).write_text(broken)
                self.check(language, code=2)

    def test_shell_greeting_must_come_from_function_not_top_level_demo(self):
        for language, source in (
            ("bash", "printf 'Hello, World!\\n'\nhello() { :; }\n"),
            ("lua", "print('Hello, World!')\nfunction hello() end\n"),
        ):
            with self.subTest(language=language):
                self.check(language, source, code=1)

    def test_go_source_package_signature_syntax_and_panic_are_learner_failures(self):
        for source in (
            'package wrong\nfunc Hello() string { return "Hello, World!" }',
            'package exercises\nfunc Hello() int { return 0 }',
            'package exercises\nfunc Hello(name string) string { return "Hello, World!" }',
            'package exercises\nfunc Hello() interface{} { return "Hello, World!" }',
            'package exercises\nfunc hello() string { return "Hello, World!" }',
            'package exercises\nfunc Hello() string { return "Hello, World!\\n" }',
            'package exercises\nfunc Hello() string { panic("learner panic") }',
            'package exercises\nfunc Hello( {',
        ):
            with self.subTest(source=source):
                self.check("go", source, code=1)

    def test_go_broken_zero_skipped_tests_and_init_exit_never_pass(self):
        self.tools("go")
        solve(self.root, "go")
        path = self.harness("go")
        original = path.read_text()
        for source in ("package exercises\nfunc broken( {\n",
                       original.replace("TestHello", "TestRenamed"),
                       original.replace("func TestHello(t *testing.T) {", 'func TestHello(t *testing.T) { t.Skip("not checked");')):
            with self.subTest(source=source):
                path.write_text(source)
                self.check("go", code=2)
        path.write_text(original)
        self.check("go", 'package exercises\nimport "os"\nfunc init() { os.Exit(0) }\nfunc Hello() string { return "Hello, World!" }', code=3)

    def test_go_backend_sets_offline_environment_and_copies_only_selected_files(self):
        tools = self.tools("go")
        solve(self.root, "go")
        shim = self.base / "go wrapper with spaces"
        log = self.base / "go invocation.jsonl"
        shim.write_text(f'#!{self.python}\nimport json, os, pathlib, sys\n'
                        f'with open({str(log)!r}, "a") as stream:\n'
                        '    stream.write(json.dumps({"args": sys.argv[1:], "files": sorted(p.name for p in pathlib.Path.cwd().iterdir()), "env": dict(os.environ)}) + "\\n")\n'
                        f'os.execv({tools["go"]!r}, [{tools["go"]!r}, *sys.argv[1:]])\n')
        shim.chmod(0o755)
        self.check("go", globals=("--go", shim))
        invocation = next(row for row in map(json.loads, log.read_text().splitlines()) if row["args"][0] == "test")
        self.assertEqual(invocation["files"], ["hello.go", "hello_test.go"])
        for key, value in {"GO111MODULE": "off", "GOWORK": "off", "GOPROXY": "off",
                           "GOSUMDB": "off", "GOTOOLCHAIN": "local", "GOENV": "off"}.items():
            self.assertEqual(invocation["env"][key], value)
        self.assertIn("-json", invocation["args"])
        self.assertIn("^TestHello$", invocation["args"])

    def test_explicit_interpreter_paths_with_spaces_and_unsupported_versions(self):
        for language, tool in (("typescript", "node"), ("bash", "bash"), ("lua", "lua"), ("go", "go")):
            with self.subTest(language=language):
                tools = self.tools(language)
                solve(self.root, language)
                wrapper = self.base / (tool + " interpreter with spaces")
                wrapper.write_text(f'#!{self.python}\nimport os, sys\nos.execv({tools[tool]!r}, [{tools[tool]!r}, *sys.argv[1:]])\n')
                wrapper.chmod(0o755)
                self.check(language, globals=("--" + tool, wrapper))
                for version in ({"node": ("v17.9.0", "garbage"), "go": ("go version go1.19.9 darwin/arm64", "garbage"),
                                 "bash": ("3.1", "garbage"), "lua": ("Lua 5.0", "garbage")}[tool]):
                    wrapper.write_text(f'#!{self.python}\nprint({version!r})\n')
                    self.check(language, code=2, globals=("--" + tool, wrapper))
        with self.subTest(tool="typescript compiler API"):
            self.tools("typescript")
            solve(self.root, "typescript")
            package = self.base / "old compiler with spaces/typescript"
            (package / "bin").mkdir(parents=True)
            (package / "lib").mkdir()
            (package / "package.json").write_text('{"name":"typescript","version":"4.9.5"}\n')
            compiler = package / "bin/tsc"
            compiler.write_text('#!/usr/bin/env node\nconsole.log("Version 4.9.5");\n')
            compiler.chmod(0o755)
            (package / "lib/typescript.js").write_text('exports.version = "4.9.5"; exports.createProgram = () => {};\n')
            self.check("typescript", code=2, globals=("--tsc", compiler))
            # A version-printing executable is not an npm compiler entry.
            fake = self.base / "fake tsc shim"
            fake.write_text('#!/bin/sh\nprintf "Version 5.9.3\\n"\n')
            fake.chmod(0o755)
            self.check("typescript", code=2, globals=("--tsc", fake))

    @unittest.skipUnless(Path("/bin/bash").is_file(), "system Bash is unavailable")
    def test_system_bash_32_compatible_harness(self):
        solve(self.root, "bash")
        self.cli("check", "bash/hello", globals=("--bash", "/bin/bash"))

    def test_new_hello_checks_ignore_unrelated_broken_legacy_programs(self):
        for language, legacy in (("typescript", "twoSum.ts"), ("go", "helloWorld.go"),
                                 ("bash", "hello_world.sh"), ("lua", "helloWorld.lua")):
            with self.subTest(language=language):
                self.tools(language)
                solve(self.root, language)
                (self.directory(language) / legacy).write_text("not valid source !!!\n")
                self.check(language)

    def test_new_sources_reset_to_main_without_touching_index_siblings_or_examples(self):
        for language in NEW_LANGUAGES:
            with self.subTest(language=language):
                example = self.directory(language) / "solutions/curated" / HELLO_EXAMPLE_PATHS[language].name
                example.parent.mkdir(parents=True)
                shutil.copy2(HELLO_EXAMPLE_PATHS[language], example)
                path = self.answer(language)
                baseline = path.read_bytes()
                solve(self.root, language)
                learner = path.read_bytes()
                relative = str(path.relative_to(self.root))
                self.assert_code(self.execute(["git", "add", relative], cwd=self.root), 0)
                before, metadata = self.sources(), self.git_files()
                command = [str(self.binary), "--root", str(self.root), "reset", language + "/hello"]
                result = subprocess.run(command, cwd=self.cwd, env=self.env, input="yes\n",
                                        capture_output=True, text=True, timeout=45)
                self.assert_code(result, 0)
                self.assertEqual(path.read_bytes(), baseline)
                match = re.search(r"Backup: ([^\r\n]+)", result.stdout)
                self.assertIsNotNone(match, result.stdout)
                self.assertEqual(Path(match[1]).read_bytes(), learner)
                for name, contents in before.items():
                    if name != relative:
                        self.assertEqual((self.root / name).read_bytes(), contents)
                self.assertEqual(self.git_files(), metadata)
                self.assertEqual(HELLO_EXAMPLE_PATHS[language].read_bytes(), learner)


if __name__ == "__main__":
    unittest.main()
