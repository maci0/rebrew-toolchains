# Static analysis and behavioral tests for this repo.  The analyzers read
# their settings from .shellcheckrc and pyproject.toml; `make lint` is the
# one entry point that must stay green before any push, `make test` pins the
# wrapper-common.sh runner/watchdog contract with stub runners.
SHELL_SCRIPTS := $(shell git ls-files '*.sh')

.PHONY: lint test
lint:
	shellcheck $(SHELL_SCRIPTS)
	ruff check .
	ruff format --check .
	mypy

test:
	sh tests/run-wrapper-tests.sh
