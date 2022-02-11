lint:
	@poetry run isort .
	@poetry run black .
	@poetry run pylint --rcfile=.pylint.cfg throttled
	@poetry run pylint --rcfile=.pylint.cfg tests

mypy:
	@poetry run mypy .

test:
	@poetry run pytest tests

checks: lint mypy test

push:
	@poetry build
	@git push && git push --tags
