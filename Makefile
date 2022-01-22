lint:
	@poetry run isort .
	@poetry run black .
	@poetry run pylint throttled
	@poetry run pylint tests

mypy:
	@poetry run mypy .

test:
	@poetry run pytest tests

checks: lint mypy test

push:
	@poetry build
	@git push && git push --tags
