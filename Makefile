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

new-version:
	@cz bump --increment PATCH
	@poetry build
	@git push && git push --tags
