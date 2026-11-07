'use strict';

// argv: absolute compilerLib, workspaceDir, configPath, sourcePath, apiPath,
// outDir, reportPath. The Rust adapter owns outDir and reportPath in private scratch.
// stdout must be an initially empty private regular file owned by the adapter.
const fs = require('node:fs');
const path = require('node:path');
const [compilerLib, workspaceDir, configPath, sourcePath, apiPath, outDir, reportPath] =
  process.argv.slice(2);
const writeFile = fs.writeFileSync.bind(fs);
const stringify = JSON.stringify;
let stage = 'compiler';

function report(outcome, reason) {
  process.stderr.write(`${reason}\n`);
  writeFile(reportPath, stringify({ outcome, stage, reason }));
}

function main() {
  const ts = require(compilerLib);
  if (Number(ts.version.split('.')[0]) < 5 || typeof ts.createProgram !== 'function') {
    report('blocked', 'TypeScript >=5 compiler API is required; run npm ci --prefix practice/typescript.');
    return;
  }
  const formatHost = {
    getCanonicalFileName: file => file,
    getCurrentDirectory: () => workspaceDir,
    getNewLine: () => '\n',
  };
  const printDiagnostics = diagnostics => {
    process.stderr.write(ts.formatDiagnostics(diagnostics, formatHost));
  };
  stage = 'config';
  const config = ts.readConfigFile(configPath, ts.sys.readFile);
  if (config.error) {
    printDiagnostics([config.error]);
    report('blocked', 'TypeScript check configuration could not be read.');
    return;
  }
  const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, path.dirname(configPath), undefined, configPath);
  if (parsed.errors.length) {
    printDiagnostics(parsed.errors);
    report('blocked', 'TypeScript check configuration is invalid.');
    return;
  }
  const expected = [sourcePath, apiPath].map(file => path.resolve(file)).sort();
  const actual = parsed.fileNames.map(file => path.resolve(file)).sort();
  if (actual.length !== 2 || actual.some((file, index) => file !== expected[index])) {
    report('blocked', 'TypeScript config must select exactly the exercise and its API probe, not legacy files.');
    return;
  }
  if (parsed.options.module !== ts.ModuleKind.CommonJS) {
    report('blocked', 'TypeScript check configuration must use module CommonJS.');
    return;
  }
  const options = {
    ...parsed.options,
    outDir,
    rootDir: workspaceDir,
    noEmit: false,
    noEmitOnError: true,
    incremental: false,
    composite: false,
    declaration: false,
    declarationMap: false,
    emitDeclarationOnly: false,
    sourceMap: false,
    inlineSourceMap: false,
    tsBuildInfoFile: undefined,
    outFile: undefined,
    declarationDir: undefined,
  };
  stage = 'compile';
  const program = ts.createProgram(parsed.fileNames, options);
  const classify = diagnostics => {
    const errors = diagnostics.filter(diagnostic => diagnostic.category === ts.DiagnosticCategory.Error);
    if (!errors.length) return false;
    printDiagnostics(diagnostics);
    const kinds = errors.map(diagnostic => {
      if (!diagnostic.file) return 'blocked';
      const file = path.resolve(diagnostic.file.fileName);
      if (file === path.resolve(sourcePath)) return 'failed';
      if (file === path.resolve(apiPath)) {
        const line = diagnostic.start === undefined ? '' : diagnostic.file.text.split(/\r?\n/)[
          diagnostic.file.getLineAndCharacterOfPosition(diagnostic.start).line
        ];
        const contractCodes = [2305, 2306, 2322, 2344, 2459, 2614, 2724];
        return line.includes('//polyglot:api') && contractCodes.includes(diagnostic.code)
          ? 'failed' : 'blocked';
      }
      if (file === path.resolve(configPath) || file.includes(`${path.sep}typescript${path.sep}lib${path.sep}`)) {
        return 'blocked';
      }
      return 'indeterminate';
    });
    const outcome = kinds.includes('indeterminate') ? 'indeterminate'
      : kinds.includes('blocked') ? 'blocked' : 'failed';
    report(outcome, outcome === 'failed' ? 'TypeScript exercise does not satisfy the static contract.'
      : 'TypeScript compiler diagnostics could not be attributed solely to the exercise.');
    return true;
  };
  if (classify(ts.getPreEmitDiagnostics(program))) return;
  const emitted = program.emit(undefined, (file, text, bom) => {
    const relative = path.relative(outDir, file);
    if (relative.startsWith(`..${path.sep}`) || relative === '..' || path.isAbsolute(relative)) {
      throw new Error('Compiler attempted to emit outside private scratch.');
    }
    fs.mkdirSync(path.dirname(file), { recursive: true });
    writeFile(file, (bom ? '\uFEFF' : '') + text);
  });
  if (classify(emitted.diagnostics)) return;
  if (emitted.emitSkipped) {
    report('blocked', 'TypeScript compiler skipped emission.');
    return;
  }
  writeFile(path.join(outDir, 'package.json'), '{"type":"commonjs"}\n');
  const artifact = path.join(outDir, path.relative(workspaceDir, sourcePath)).replace(/\.ts$/, '.js');
  if (!fs.statSync(artifact).isFile()) {
    report('blocked', 'TypeScript compiler did not produce the selected exercise artifact.');
    return;
  }
  const stdoutStat = fs.fstatSync.bind(fs);
  const initialOutput = stdoutStat(1);
  if (!initialOutput.isFile() || initialOutput.size !== 0) {
    report('blocked', 'TypeScript runtime requires an empty private regular-file stdout capture.');
    return;
  }
  stage = 'runtime';
  try {
    const exercise = require(artifact);
    const hello = exercise.hello;
    if (stdoutStat(1).size !== 0) {
      report('failed', 'The exercise must not print during module loading; print inside hello().');
      return;
    }
    if (typeof hello !== 'function') {
      report('failed', 'The exercise must export a function named hello.');
      return;
    }
    const returned = hello();
    const invocationBytes = stdoutStat(1).size;
    if (returned !== undefined) {
      report('failed', 'hello() must return undefined.');
      return;
    }
    // Regular-file stdout makes both console writes and direct fd writes
    // synchronous. Delayed output cannot substitute for this invocation.
    if (invocationBytes !== Buffer.byteLength('Hello, World!\n')) {
      report('failed', 'hello() must synchronously print exactly Hello, World! followed by one newline.');
      return;
    }
  } catch (error) {
    process.stderr.write(`${error && error.stack || error}\n`);
    report('failed', 'The exercise threw a runtime error.');
    return;
  }
  report('passed', 'Static contract and synchronous hello() execution completed.');
}

try {
  main();
} catch (error) {
  process.stderr.write(`${error && error.stack || error}\n`);
  report('blocked', `TypeScript check infrastructure failed during ${stage}.`);
}
