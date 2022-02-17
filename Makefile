lint:
	@poetry run isort .
	@poetry run black .
	@poetry run pylint --rcfile=.pylint.cfg throttled
	@poetry run pylint --rcfile=.pylint.cfg --disable=redefined-outer-name tests

mypy:
	@poetry run mypy .

test:
	@poetry run pytest tests

checks: lint mypy test

git-hooks:
	@pre-commit run --all-files --hook-stage merge-commit

push:
	@poetry build
	@git push && git push --tags
