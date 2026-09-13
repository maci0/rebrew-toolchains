# Static analysis and behavioral tests for this repo.  The analyzers read
# their settings from .shellcheckrc and pyproject.toml; `make lint` is the
# one entry point that must stay green before any push, `make test` pins
# the wrapper-common.sh runner/watchdog contract with stub runners, the
# Quantum extractor's numeric contracts with unit tests, and the generated
# toolchain catalog against the manifest.
#
# `make docs` regenerates docs/TOOLCHAINS.md from sources.json + the
# Dockerfiles; `make test` fails when the committed copy is stale.
# Every .sh in the repo, tracked or not: a freshly added wrapper must be
# linted before it is committed, not after (git ls-files alone would skip it).
# --others --exclude-standard keeps the .gitignore'd trees out.
SHELL_SCRIPTS := $(shell git ls-files --cached --others --exclude-standard '*.sh')

.PHONY: lint test docs smoke pins
lint:
	shellcheck $(SHELL_SCRIPTS)
	ruff check .
	ruff format --check .
	mypy

test:
	sh tests/run-wrapper-tests.sh
	uv run python -m unittest discover -s tests -p 'test_*.py'

docs:
	uv run python catalog.py

# Docker-requiring check: builds one image per runtime class and compiles with
# it (see tests/smoke.sh).  Not part of `test` — it needs network for the first
# build of each image, and /dev/kvm for the dosemu2 family.
smoke:
	sh tests/smoke.sh

# Network check: every pinned download URL must still resolve (see
# tests/check_pins.py).  Scheduled in CI rather than run per-push, so a
# transient upstream outage cannot block a change.
pins:
	uv run python tests/check_pins.py
