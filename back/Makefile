.venv:
	@python3 -m venv .venv
	@(. .venv/bin/activate; \
	pip install -q -r configs/requirements.txt;)

.PHONY: clean
clean:
	@rm -rf */__pycache__ */*/__pycache__ */*/*/__pycache__ */*/*/*/__pycache__ src/*.sqlite .coverage \
	 */.*_cache coverage.xml .*_cache htmlcov/ site/ .report/

clean_db:
	@rm -rf database_test.sqlite */database_test.sqlite */*/database_test.sqlite */*/*/database_test.sqlite */*/*/*/database_test.sqlite

run: .venv
	@(. .venv/bin/activate; \
		python3 src/main.py)
		
test: .venv
	@(. .venv/bin/activate; \
		cd tests && ls test_* | xargs -I {} sh -c 'echo "Running {}..."; pytest -p no:warnings -q --tb=short {}' && \
		cd core_test && ls test_* | xargs -I {} sh -c 'echo "Running {}..."; pytest -p no:warnings -q --tb=short {}' && \
		cd game_logic_tests && ls test_* | xargs -I {} sh -c 'echo "Running {}..."; pytest -p no:warnings -q --tb=short {}')

coverage: .venv
	@(. .venv/bin/activate; \
		echo "Running coverage..."; \
		coverage run -m pytest > /dev/null 2>&1; \
		echo "Running report..."; \
		coverage html)
