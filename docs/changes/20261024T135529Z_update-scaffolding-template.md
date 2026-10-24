---
type: Change Record
title: Update copier-UvScaffolding template to v0.5.14
description: Applies copier-UvScaffolding v0.5.14, which drops Python 3.10, adds Python 3.14, and hardens the CI/CD and release workflows.
tags:
  - scaffolding
  - ci
  - release
  - python-versions
status: stable
generated:
  by: claude-opus-5-5
  at: 2026-10-24T13:55:29Z
sources:
  - id: template
    resource: https://github.com/gt-csse/copier-UvScaffolding
    title: copier-UvScaffolding
  - id: copier-answers
    resource: .copier-answers.yml
  - id: workflows
    resource: .github/workflows/CICD_impl.yml
  - id: release-action
    resource: .github/actions/release_impl/action.yml
  - id: versioning
    resource: src/AutoGitSemVer/Lib.py
---

# Summary

Updates the project scaffolding from copier-UvScaffolding `v0.5.11` to `v0.5.14`[^template][^copier-answers]. The supported Python versions change from 3.10–3.13 to 3.11–3.144, and the CI/CD and release workflows are hardened.

# Motivation

- Python 3.10 reaches end of life in October 2026. Python 3.14 is the current releases and needs to be tested and declared.
- The previous release action interpolated `${{ }}` expressions directly into shell scripts, wrote the minisign private key to a fixed `/tmp` path, and failed outright on transient network errors. Workflow runs also had no concurrency control or timeouts.
- Keeping the project on the shared template means future template fixes can be applied mechanically.

# Changes

## Python support

- `requires-python` changes from `>= 3.10` to `>= 3.11`. Classifiers drop 3.10 and add 3.14.
- The CI test matrix is now `3.14, 3.13, 3.12, 3.11`. The package build uses 3.11.
- `uv.lock` drops `exceptiongroup`, which was needed only on 3.10.
- `uv_build` changes from `>=0.11.19,<0.12.0` to `>=0.13.5,<0.14.0`.

## CI/CD workflow (`CICD.yml`, `CICD_impl.yml`)[^workflows]

- Adds a concurrency group. Superseded pull-request runs are cancelled. Each push gets its own group, so a pending push run is never cancelled and its release is never skipped.
- Adds `timeout-minutes` to every job.
- Renames the `python_package_version` input to `build_python_version` and the `package_coverage` job to `postprocess_coverage`. The `package_name` output becomes `wheel_filename`, which matches what it holds.
- Removes redundant `uv sync --frozen` steps, since `uv run` syncs implicitly.
- Fails the build unless exactly one wheel is produced.
- Moves expression values into environment variables instead of interpolating them into scripts.

## Release action (`release_impl/action.yml`, `retry.sh`)[^release-action]

- Passes the wheel filename, package version, and coverage total as explicit inputs instead of inherited job `env`.
- Adds `retry.sh`, which retries tag pushes and GitHub release creation up to 3 times, 15 seconds apart.
- Makes release creation idempotent. If the release already exists, artifacts are uploaded with `--clobber` so a rerun can recover.
- Writes the signing key to a `mktemp` file under `RUNNER_TEMP` and removes it with an `EXIT` trap. All artifacts are signed in one Python invocation. The trusted comment now uses the wheel filename and tag.
- Skips the coverage badge when no coverage total is available.
- Passes the PyPI token through `UV_PUBLISH_TOKEN`.

## Documentation and configuration

- `README.md` names the signature extension correctly (`.minisig`, not `.minisign`).
- `DEVELOPMENT.md` documents the signing command and adds a Semantic Versioning section.
- `src/AutoGitSemVer.yaml` and `.github/release_sources.yaml` note that the two files must stay in sync.
- `pyproject.toml` is reformatted, and pytest also produces an HTML coverage report.

# Versioning impact

Users on Python 3.10 can no longer install new releases. The commit subject therefore includes the `+minor` token, which `DefaultCommitDataExtractor` uses to increment the minor version[^versioning]. The token goes in the subject because squash merges to `main` keep only the subject line.

# Compatibility

- The runtime library and CLI are unchanged.
- Consumers on Python 3.10 will resolve to the last release that supports 3.10.

[^template]: https://github.com/gt-csse/copier-UvScaffolding
[^copier-answers]: `.copier-answers.yml`
[^workflows]: `.github/workflows/CICD.yml`, `.github/workflows/CICD_impl.yml`
[^release-action]: `.github/actions/release_impl/action.yml`, `.github/actions/release_impl/retry.sh`
[^versioning]: `src/AutoGitSemVer/Lib.py`, `DefaultCommitDataExtractor`
