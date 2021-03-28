VERSION=0.0.1
MAIN=cli
SRC_CORE=things_cli
SRC_TEST=tests
PYTHON=python3
PYDOC=pydoc3
PIP=pip3
PIPENV=pipenv

help: ## Print help for each target
	$(info Things low-level Python API.)
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
	@$(PIP) uninstall -y things

test: ## Test the code
	@type coverage >/dev/null 2>&1 || (echo "Run '$(PIP) install coverage' first." >&2 ; exit 1)
	@coverage erase
	@coverage run -a -m $(SRC_TEST).test_things_cli
	@coverage report
	@coverage html

.PHONY: doc
doc: ## Document the code
	@$(PYDOC) $(SRC_CORE).things

.PHONY: clean
clean: ## Cleanup
	@rm -f $(DEST)
	@find . -name \*.pyc -delete
	@find . -name __pycache__ -delete
	@rm -rf htmlcov
	@rm -rf build dist *.egg-info
	@rm -rf .mypy_cache/
	@rm -f .coverage

auto-style: ## Style the code
	@if type black >/dev/null 2>&1 ; then black $(SRC_CORE) ; \
	 else echo "SKIPPED. Run '$(PIP) install black' first." >&2 ; fi

code-style: ## Test the code style
	@echo PyCodestyle...
	@if type pycodestyle >/dev/null 2>&1 ; then pycodestyle --max-line-length=88 --ignore=E203,W503 $(SRC_CORE) ; \
	 else echo "SKIPPED. Run '$(PIP) install pycodestyle' first." >&2 ; fi

code-count: ## Count the code
	@if type cloc >/dev/null 2>&1 ; then cloc $(SRC_CORE) ; \
	 else echo "SKIPPED. Run 'brew install cloc' first." >&2 ; fi

code-lint: ## Lint the code
	@echo Pylama...
	@if type pylama >/dev/null 2>&1 ; then pylama --ignore E501,E203,W503 $(SRC_CORE) ; \
	 else echo "SKIPPED. Run '$(PIP) install pylama' first." >&2 ; fi
	@echo Pylint...
	@if type pylint >/dev/null 2>&1 ; then pylint $(SRC_CORE) ; \
	 else echo "SKIPPED. Run '$(PIP) install pylint' first." >&2 ; fi
	@echo Flake...
	@if type flake8 >/dev/null 2>&1 ; then flake8 --max-complexity 10 $(SRC_CORE) ; \
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

upload: clean ## Upload the code
	@python3 setup.py sdist bdist_wheel
	@python3 -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/things*
