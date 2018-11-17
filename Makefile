.PHONY: env
env:
	virtualenv -p python2 env --no-site-packages

.PHONY: version
version:
	sed --in-place --expression="s/.\..\../$(tag)/" README.md
	sed --in-place --expression="s/version='.*'/version='$(tag)'/" setup.py
	sed --in-place --expression="s/__version__ = '.*'/__version__ = '$(tag)'/" src/kaml/__init__.py

ifneq "$(VIRTUAL_ENV)" ""

.PHONY: setup
setup:
	python setup.py develop
	pip install --editable .[tools]

.PHONY: clean
clean:
	find src/ -type f -name '*.pyc' -delete

.PHONY: test
test: clean
	nose2 tests


.PHONY: debug
debug: clean
	nose2 -D tests


.PHONY: lint
lint: clean
	pylint setup.py src/kaml/ tests/

endif
