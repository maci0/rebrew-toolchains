# Static analysis for this repo.  The analyzers read their settings from
# .shellcheckrc and pyproject.toml; `make lint` is the one entry point that
# must stay green before any push.
SHELL_SCRIPTS := $(shell git ls-files '*.sh')

.PHONY: lint
lint:
	shellcheck $(SHELL_SCRIPTS)
	ruff check .
	ruff format --check .
	mypy
