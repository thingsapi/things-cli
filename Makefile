MAIN=cli
APP=things-cli
SRC_CORE=things_cli
SRC_TEST=tests
PYTHON=python3
PYDOC=pydoc3
PIP=pip3
PIPENV=pipenv

DATE:=$(shell date +"%Y-%m-%d")
VERSION=$(shell $(PYTHON) -c 'import things_cli; print(things_cli.__version__)')
SHELL := /usr/bin/env bash -euo pipefail -c

help: ## Print help for each target
	$(info Things low-level Python CLI.)
	$(info ============================)
	$(info )
	$(info Available commands:)
	$(info )
	@grep '^[[:alnum:]_-]*:.* ##' $(MAKEFILE_LIST) \
		| sort | awk 'BEGIN {FS=":.* ## "}; {printf "%-25s %s\n", $$1, $$2};'

run: ## Run the code
	@$(PYTHON) -m $(SRC_CORE).$(MAIN)

install: ## Install the code
	@$(PYTHON) setup.py install

uninstall: ## Uninstall the code
	@$(PIP) uninstall -y things-cli

test: ## Test the code
	@type coverage >/dev/null 2>&1 || (echo "Run '$(PIP) install coverage' first." >&2 ; exit 1)
	@coverage erase
	@coverage run -a -m $(SRC_TEST).test_things_cli
	@coverage report
	@coverage html

.PHONY: doc
doc: ## Document the code
	@$(PYDOC) $(SRC_CORE).cli

.PHONY: clean
clean: ## Cleanup
	@rm -f $(DEST)
	@find . -name \*.pyc -delete
	@find . -name __pycache__ -delete
	@rm -rf htmlcov
	@rm -rf build dist *.egg-info .eggs
	@rm -rf $(SRC_CORE)/.mypy_cache .mypy_cache
	@rm -f .coverage

auto-style: ## Style the code
	@echo "isort..."
	@if type isort >/dev/null 2>&1 ; then isort -rc . ; \
	 else echo "SKIPPED. Run '$(PIP) install isort' first." >&2 ; fi
	@echo "autoflake..."
	@if type autoflake >/dev/null 2>&1 ; then autoflake -r --in-place --remove-unused-variables . ; \
	 else echo "SKIPPED. Run '$(PIP) install isort' first." >&2 ; fi
	@echo "black..."
	@if type black >/dev/null 2>&1 ; then black $(SRC_CORE) ; \
	 else echo "SKIPPED. Run '$(PIP) install black' first." >&2 ; fi

code-style: ## Test the code style
	@echo PyCodestyle...
	@if type pycodestyle >/dev/null 2>&1 ; then pycodestyle $(SRC_CORE) ; \
	 else echo "SKIPPED. Run '$(PIP) install pycodestyle' first." >&2 ; fi

code-count: ## Count the code
	@if type cloc >/dev/null 2>&1 ; then cloc $(SRC_CORE) ; \
	 else echo "SKIPPED. Run 'brew install cloc' first." >&2 ; fi

code-lint: ## Lint the code
	@echo Pylama...
	@if type pylama >/dev/null 2>&1 ; then pylama $(SRC_CORE) ; \
	 else echo "SKIPPED. Run '$(PIP) install pylama' first." >&2 ; fi
	@echo Pylint...
	@if type pylint >/dev/null 2>&1 ; then pylint $(SRC_CORE) ; \
	 else echo "SKIPPED. Run '$(PIP) install pylint' first." >&2 ; fi
	@echo Flake...
	@if type flake8 >/dev/null 2>&1 ; then flake8 $(SRC_CORE) ; \
	 else echo "SKIPPED. Run '$(PIP) install flake8' first." >&2 ; fi
	@echo Pyright...
	@if type pyright >/dev/null 2>&1 ; then pyright $(SRC_CORE) ; \
	 else echo "SKIPPED. Run 'npm install -f pyright' first." >&2 ; fi
	@echo MyPy...
	@if type mypy >/dev/null 2>&1 ; then mypy --ignore-missing-imports $(SRC_CORE) ; \
	 else echo "SKIPPED. Run '$(PIP) install mypy' first." >&2 ; fi

lint: code-style code-lint  ## Lint everything

deps-install: ## Install the dependencies
	@#type $(PIPENV) >/dev/null 2>&1 || (echo "Run '$(PIP) install pipenv' first." >&2 ; exit 1)
	@#$(PIPENV) install
	@$(PIP) install -r requirements.txt

feedback: ## Give feedback
	@open https://github.com/thingsapi/things-cli/issues

release: build ## Create a new release
	@type gh >/dev/null 2>&1 || (echo "Run e.g. 'brew install gh' first." >&2 ; exit 1)
	@gh release create "v$(VERSION)" -t "Release $(VERSION) ($(DATE))" 'dist/$(APP)-$(VERSION).tar.gz'

build: clean ## Build the code
	@$(PYTHON) setup.py sdist bdist_wheel

upload: build ## Upload the code
	@type twine >/dev/null 2>&1 || (echo "Run e.g. 'pip install twine' first." >&2 ; exit 1)
	@echo "########################"
	@echo "Using ~/.pypirc or environment variables TWINE_USERNAME and TWINE_PASSWORD"
	@echo "See: https://packaging.python.org/specifications/pypirc/#using-a-pypi-token"
	@echo "########################"
	@twine upload dist/$(APP)*

db-to-things:
	@cp tests/main.sqlite* ~/Library/Group\ Containers/JLMPQHK86H.com.culturedcode.ThingsMac/Things\ Database.thingsdatabase/

db-from-things:
	@cp ~/Library/Group\ Containers/JLMPQHK86H.com.culturedcode.ThingsMac/Things\ Database.thingsdatabase/main.sqlite* tests/
