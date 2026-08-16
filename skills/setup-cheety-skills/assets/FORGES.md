# Forges

The harness ships for three forges. The installer writes exactly one of them —
`node install.mjs --stack <stack> --forge forgejo|github|gitlab`.

Syntax is verified by `make forge` (`tools/forge_check.py`). The checker knows all
three dialects and reports the ones it finds in the repository, so a file that
migrated from one forge to the next is caught rather than silently ignored.

```
.forgejo/                        .github/                       .gitlab-ci.yml
├── workflows/                   ├── workflows/                 .gitlab/
│   ├── harness.yaml             │   ├── harness.yml            ├── ci/
│   ├── ci-laravel.yaml          │   ├── ci-laravel.yml         │   ├── harness.yml
│   ├── ci-typescript.yaml       │   ├── ci-typescript.yml      │   ├── laravel.yml
│   └── ci-python.yaml           │   └── ci-python.yml          │   ├── typescript.yml
├── issue_template/              ├── ISSUE_TEMPLATE/            │   └── python.yml
│   ├── bug.yaml                 │   ├── bug.yml                ├── issue_templates/
│   ├── feature.yaml             │   ├── feature.yml            │   ├── Bug.md
│   ├── chore.yaml               │   ├── chore.yml              │   ├── Feature.md
│   └── config.yaml              │   └── config.yml             │   └── Chore.md
└── pull_request_template.md     └── pull_request_template.md   └── merge_request_templates/
                                                                    └── Default.md
```

One CI file per stack, and the harness check beside it. Forgejo and GitHub read every
workflow in the directory, so delete the ones for stacks this repository does not use;
GitLab loads only what `.gitlab-ci.yml` includes.

The stack pipelines expect the tooling their profile documents — `requirements-dev.txt`
for Python, `composer.lock` for Laravel, `package-lock.json` for TypeScript. The
dependency-install line is marked in each file and is the usual one to adjust.

The issue and pull-request templates are written in German, because the artifacts they
produce are tickets — see `AGENTS.md`, section *Language*. Everything else here is
English.

---

## Forgejo and GitHub: five differences that fail silently

Forgejo Actions is very close to GitHub Actions. That is exactly what makes the
differences dangerous — a file copied over often *almost* works.

### 1. Directory

Workflows live in `.forgejo/workflows/`. If that directory is absent, Forgejo falls back
to `.github/workflows/`, so one repository can serve both. As soon as `.forgejo/` exists,
`.github/` is **ignored** for workflows.

### 2. `uses:` without a full URL is not portable

```yaml
uses: actions/checkout@v4                              # GitHub; on Forgejo instance-dependent
uses: https://data.forgejo.org/actions/checkout@v4     # Forgejo; on GitHub not resolvable at all
```

On Forgejo the short form is prefixed with the instance's `DEFAULT_ACTIONS_URL`. The
default is `https://data.forgejo.org`, but administrators can change it. What runs on your
instance may not resolve on a fork elsewhere. Third-party actions are not mirrored on
`data.forgejo.org` — reference them by their full URL, e.g.
`https://github.com/shivammathur/setup-php@v2`.

GitHub goes the other way: it resolves `owner/repo@ref` and cannot fetch a URL.

### 3. Runner labels are assigned locally

`ubuntu-latest` is not a Forgejo convention; it names a GitHub-hosted runner. What is
available depends on whoever registered the runner. The documentation uses `docker`; your
instance may use something else.

The Forgejo workflows here use `runs-on: docker`. **That is the one line you have to adjust
when adopting them.** The GitHub workflows use `ubuntu-latest` and need no adjustment.

### 4. `concurrency` is redundant on Forgejo, not on GitHub

With nothing declared, Forgejo already cancels running invocations of the same workflow on
`push` and `pull_request`. GitHub does not — there the block is what stops the previous run:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### 5. Issue templates use `about:`, not `description:`

```yaml
name: Bug
about: Behaviour deviates from expectation     # Forgejo
description: Behaviour deviates from expectation  # GitHub
```

The field types are the same (`markdown`, `input`, `textarea`, `dropdown`, `checkboxes`),
as is `validations.required`. Forgejo reads `.forgejo/issue_template/`, GitHub reads
`.github/ISSUE_TEMPLATE/` — the upper case is not cosmetic on a case-sensitive checkout.

A `config` file with `blank_issues_enabled: false` prevents issues without a template.
That is not cosmetic here: an issue without acceptance criteria and non-goals will be
guessed at during implementation.

### Services on GitHub-hosted runners

A job on `ubuntu-latest` runs on the host, not inside a container, so services are reached
on `127.0.0.1` through their published port — **not** under their service name. Inside a
`container:` job (as on Forgejo) it is the service name. Getting this wrong produces a
connection error that reads like a broken database.

---

## GitLab: it is not Actions at all

### 1. One pipeline file

GitLab reads exactly one file, `.gitlab-ci.yml` at the repository root. Everything else is
pulled in with `include: - local:`. The installer wrote the include for the stack you
chose; add a second `local:` line if the repository carries more than one.

### 2. No `jobs:`, no `steps:`, no `uses:`

A job is a top-level key with `stage`, `image` and `script`. There are no composable
actions — what `setup-php` or `setup-node` do on Actions is either a base image or a line
in `before_script`. Keys GitLab does not know are **ignored without error**, which is why
`tools/forge_check.py` fails a GitLab pipeline that still carries `runs-on:`, `uses:` or
`steps:`.

### 3. A job whose stage is not declared never runs

`stages:` in `.gitlab-ci.yml` is the complete list. A job with `stage: harness` while
`harness` is missing from that list fails the pipeline at parse time; a job with no
`stage:` at all silently lands in `test`.

### 4. `rules:` instead of `on:`

```yaml
rules:
  - if: $CI_PIPELINE_SOURCE == 'merge_request_event'
  - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

Without the second rule nothing runs on the default branch; without the first, nothing runs
on a merge request. The same pair sits in the root `workflow:` block so no duplicate
pipeline is created for a branch that has an open MR.

### 5. Superseded pipelines keep running

`interruptible: true` per job, plus *Settings → CI/CD → General pipelines → Auto-cancel
redundant pipelines*. Only both together give what Forgejo does by default.

### 6. Services are reached by alias

`postgres:16` with `alias: postgres` is reachable as `postgres`, never as `localhost` — the
job runs in its own container.

### 7. Issue templates are Markdown, and nothing is required

GitLab has no issue forms. `.gitlab/issue_templates/*.md` are plain Markdown, chosen from a
dropdown when opening an issue, and no field can be enforced. What Forgejo and GitHub
express as `validations.required` is therefore a comment in the template — and the reason
`Nicht-Ziele` is checked mechanically as a heading.

There is also no `blank_issues_enabled`. The closest equivalent is
*Settings → General → Default description template for issues*, which preselects a
template but does not force it.

---

## What to adjust when adopting

1. **Forgejo only: `runs-on:`** in every workflow — set a label your runner offers
2. **`config.yaml` / `config.yml`** — point the two `example.invalid` links at your
   repository. On GitLab there is no such file; put the links in the templates themselves
3. **`STACK_PROFILE`** in the matching CI workflow, or delete the workflows you do not need
4. **Forgejo only: `services:`** needs a runner with Docker access. Without it: use a
   `container:` block with the service preinstalled, or start the database inside the step

## Running two forges from one repository

Forgejo prefers `.forgejo/workflows/` and GitHub never sees it, so those two can live side
by side; only the issue and pull-request templates have to be maintained twice, because of
the `about:` / `description:` difference. GitLab shares nothing with either — its pipeline
and its templates are separate files in any case.
