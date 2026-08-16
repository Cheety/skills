#!/usr/bin/env node
// @ts-check
/**
 * install.mjs — writes the harness into a project, for one stack only.
 *
 * The `skills` CLI installs this whole directory into .claude/skills/ (or the
 * equivalent for your agent). It does not know about stacks, so the stack
 * selection happens here: only the chosen profile, its fixtures and its tool
 * configuration are copied into the project.
 *
 *   node install.mjs --stack laravel
 *   node install.mjs --stack typescript --forge github
 *   node install.mjs --stack python --forge gitlab --force
 *   node install.mjs --list
 *
 * Files already present are never overwritten unless --force is given. That is
 * deliberate: after `npx skills update` the skill directory is fresh, but the
 * copies in your project are yours. The installer reports what it skipped so
 * the difference is visible rather than silent.
 */

import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const ASSETS = join(HERE, "assets");
const STACKS = join(ASSETS, "stacks");

// ── arguments ───────────────────────────────────────────────────────────────

const argv = process.argv.slice(2);
const flag = (name, fallback = null) => {
  const i = argv.indexOf(`--${name}`);
  if (i === -1) return fallback;
  const next = argv[i + 1];
  return next && !next.startsWith("--") ? next : true;
};

const stack = flag("stack");
const forge = String(flag("forge", "forgejo"));
const FORGES = ["forgejo", "github", "gitlab", "none"];
if (!FORGES.includes(forge)) {
  console.error(`Unknown forge '${forge}'. Available: ${FORGES.join(", ")}`);
  process.exit(1);
}
const target = resolve(String(flag("target", process.cwd())));
const force = argv.includes("--force");
const dryRun = argv.includes("--dry-run");

const available = readdirSync(STACKS, { withFileTypes: true })
  .filter((d) => d.isDirectory())
  .map((d) => d.name);

if (argv.includes("--list") || !stack) {
  console.log("Available stacks:");
  for (const s of available) {
    const profile = join(STACKS, s, `${s}.json`);
    let count = "?";
    try {
      count = String(JSON.parse(readFileSync(profile, "utf8")).rules.length);
    } catch {
      /* profile unreadable — reported as ? */
    }
    console.log(`  ${s.padEnd(12)} ${count} rules`);
  }
  console.log("\nUsage: node install.mjs --stack <name> [--forge forgejo|github|gitlab|none] [--force]");
  process.exit(stack ? 0 : 1);
}

if (!available.includes(String(stack))) {
  console.error(`Unknown stack '${stack}'. Available: ${available.join(", ")}`);
  process.exit(1);
}

// ── copy helpers ────────────────────────────────────────────────────────────

const written = [];
const skipped = [];

function put(from, to) {
  const dest = join(target, to);
  if (existsSync(dest) && !force) {
    skipped.push(to);
    return;
  }
  written.push(to);
  if (dryRun) return;
  mkdirSync(dirname(dest), { recursive: true });
  if (statSync(from).isDirectory()) {
    cpSync(from, dest, { recursive: true, force: true });
  } else {
    cpSync(from, dest, { force: true });
  }
}

/** Same skip/force/dry-run semantics as put(), for generated content. */
function putText(content, to) {
  const dest = join(target, to);
  if (existsSync(dest) && !force) {
    skipped.push(to);
    return;
  }
  written.push(to);
  if (dryRun) return;
  mkdirSync(dirname(dest), { recursive: true });
  writeFileSync(dest, content);
}

/**
 * @param {string} from
 * @param {string} toDir
 * @param {(relativePath: string) => boolean} [accept] decides per source file
 *   whether it belongs in the project; directories are always descended into.
 */
function putTree(from, toDir, accept) {
  for (const entry of readdirSync(from, { withFileTypes: true })) {
    const child = join(from, entry.name);
    const rel = join(toDir, entry.name);
    if (entry.isDirectory()) putTree(child, rel, accept);
    else if (!accept || accept(rel)) put(child, rel);
  }
}

/**
 * Every forge ships a CI pipeline per stack, but a project runs exactly one.
 * Copying the whole forge directory would install all of them, and each would
 * start failing against a project that does not have that toolchain — so the
 * pipelines of the other stacks are filtered out here.
 */
function isForeignStackPipeline(relPath) {
  const parts = relPath.split(/[\\/]/);
  const name = parts.pop() ?? "";
  // Only pipeline directories are filtered; issue templates keep their names.
  if (!parts.includes("workflows") && !parts.includes("ci")) return false;
  const match = /^(?:ci-)?(.+)\.ya?ml$/.exec(name);
  if (!match) return false;
  const base = match[1];
  return available.includes(base) && base !== stack;
}

// ── 1. stack-independent core ───────────────────────────────────────────────

putTree(join(ASSETS, "tools"), "tools");
if (existsSync(join(ASSETS, "commands"))) putTree(join(ASSETS, "commands"), ".claude/commands");
put(join(ASSETS, "AGENTS.md"), "AGENTS.md");
put(join(ASSETS, "Makefile"), "Makefile");

// ── 2. the chosen stack only ────────────────────────────────────────────────

const src = join(STACKS, String(stack));
put(join(src, `${stack}.json`), `tools/arch-check/profiles/${stack}.json`);
put(join(src, "PROFILE.md"), `profiles/${stack}/PROFILE.md`);
put(join(src, "fixtures"), `tools/arch-check/fixtures/${stack}`);
if (existsSync(join(src, "tooling"))) putTree(join(src, "tooling"), ".");

// ── 3. forge integration ────────────────────────────────────────────────────

if (forge === "forgejo" || forge === "github") {
  putTree(join(ASSETS, forge), `.${forge}`, (rel) => !isForeignStackPipeline(rel));
  put(join(ASSETS, "FORGES.md"), "FORGES.md");
} else if (forge === "gitlab") {
  putTree(join(ASSETS, "gitlab", "ci"), ".gitlab/ci", (rel) => !isForeignStackPipeline(rel));
  putTree(join(ASSETS, "gitlab", "issue_templates"), ".gitlab/issue_templates");
  putTree(join(ASSETS, "gitlab", "merge_request_templates"), ".gitlab/merge_request_templates");
  put(join(ASSETS, "FORGES.md"), "FORGES.md");

  // GitLab reads exactly one pipeline file, so the stack cannot be a separate
  // workflow file as on Forgejo and GitHub — the include has to be written.
  const stackPipeline = existsSync(join(ASSETS, "gitlab", "ci", `${stack}.yml`))
    ? `  - local: '.gitlab/ci/${stack}.yml'`
    : `  # no pipeline shipped for stack '${stack}' — add one under .gitlab/ci/`;
  putText(
    readFileSync(join(ASSETS, "gitlab", "gitlab-ci.yml"), "utf8").replace("__STACK_INCLUDE__", stackPipeline),
    ".gitlab-ci.yml",
  );
}

// ── 4. pin the stack so later runs and CI agree ─────────────────────────────

const configPath = join(target, ".harness.json");
if (!existsSync(configPath) || force) {
  written.push(".harness.json");
  if (!dryRun) {
    writeFileSync(
      configPath,
      `${JSON.stringify({ stack, forge, installed: new Date().toISOString().slice(0, 10) }, null, 2)}\n`,
    );
  }
}

// ── report ──────────────────────────────────────────────────────────────────

console.log(`\nHarness — stack '${stack}', forge '${forge}'`);
console.log(`  target : ${relative(process.cwd(), target) || "."}`);
console.log(`  written: ${written.length} file(s)${dryRun ? " (dry run)" : ""}`);
if (skipped.length) {
  console.log(`  skipped: ${skipped.length} file(s) that already exist — re-run with --force to overwrite`);
  for (const s of skipped.slice(0, 10)) console.log(`     ${s}`);
  if (skipped.length > 10) console.log(`     … and ${skipped.length - 10} more`);
}
console.log(`
Next:
  python3 tools/arch-check/eval.py --profile ${stack}      # rules self-test
  python3 tools/arch-check/arch_check.py . --profile ${stack}
  make pruefe PROFILE=${stack}
`);
