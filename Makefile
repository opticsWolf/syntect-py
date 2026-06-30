SUBMODULES = testdata/Packages/.git

info:
	$(info Targets)
	$(info -----------------------------------------------------------------------)
	$(info assets      | generate default theme packs and syntax)
	$(info - OTHER TARGETS -------------------------------------------------------)
	$(info themes      | generate default theme pack)
	$(info packs       | generate default syntax pack)
	$(info syntest     | run syntax test summary)


$(SUBMODULES):
	git submodule update --init --recursive

assets: packs themes

packs: $(SUBMODULES)
	cargo run --features=metadata --example gendata -- synpack testdata/Packages assets/default_newlines.packdump assets/default_nonewlines.packdump assets/default_metadata.packdump testdata/DefaultPackage

themes: $(SUBMODULES)
	cargo run --example gendata -- themepack testdata assets/default.themedump

syntest: $(SUBMODULES)
	@echo Tip: Run make update-known-failures to update the known failures file.
	cargo run --release --example syntest -- testdata/Packages testdata/Packages --summary | diff -U 1000000 testdata/known_syntest_failures.txt -
	@echo No new failures!

syntest-fancy: $(SUBMODULES)
	@echo Tip: Run make update-known-failures to update the known failures file.
	cargo run --features default-fancy --no-default-features --release --example syntest -- testdata/Packages testdata/Packages --summary | diff -U 1000000 testdata/known_syntest_failures_fancy.txt -
	@echo No new failures!

update-known-failures: $(SUBMODULES)
	cargo run --release --example syntest -- testdata/Packages testdata/Packages --summary | tee testdata/known_syntest_failures.txt

update-known-failures-fancy: $(SUBMODULES)
	cargo run --features default-fancy --no-default-features --release --example syntest -- testdata/Packages testdata/Packages --summary | tee testdata/known_syntest_failures_fancy.txt

# Python targets
.PHONY: test lint format precommit benchmark build

test:
	cd pyext && $(PYTEST) tests/ -v --tb=short

lint:
	cd pyext && $(MYPY) syntect.pyi --ignore-missing-imports

format:
	cd pyext && $(BLACK) --line-length 100 src/ examples/ tests/
	cd pyext && $(ISORT) --line-length 100 src/ examples/ tests/

precommit:
	pre-commit run --all-files

benchmark:
	cd pyext && $(PYTHON) examples/benchmark.py --iterations 100

build:
	cd pyext && maturin build --release
