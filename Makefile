build:
	@poetry build

publish: build
	@poetry publish -u '${PYPI_USERNAME}' -p '${PYPI_PASSWORD}'

lint:
	@poetry run isort .
	@poetry run pylint throttled
	@poetry run pylint tests
	@poetry run black .

mypy:
	@poetry run mypy .

test:
	@poetry run pytest tests

checks: lint mypy test
