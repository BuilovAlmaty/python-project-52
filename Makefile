MANAGE := uv run python3 manage.py
PORT := 8000

.PHONY: dev
dev:
	$(MANAGE) runserver 127.0.0.1:$(PORT)

.PHONY: kill
kill:
	@PT=$(PT); for pid in $$(lsof -ti :$${PT:-$(PORT)}); do echo "kill pin: $$pid"; kill -9 "$$pid"; done

.PHONY: lint
lint:
	uv run ruff check .

build:
	./build.sh

render-start:
	python -m gunicorn task_manager.asgi:application -k uvicorn.workers.UvicornWorker

install:
	uv sync

collectstatic:
	$(MANAGE) collectstatic --noinput

migrate:
	$(MANAGE) makemigrations && $(MANAGE) migrate

test:
	uv run manage.py test

po:
	uv run manage.py compilemessages

lint-fix:
	uv run ruff check . --fix

sq_test:
	coverage run -m pytest \
		task_manager/labels/tests.py \
		task_manager/statuses/tests.py \
		task_manager/tasks/tests.py \
		task_manager/users/tests.py
	coverage xml

install_ci:
	uv venv
	uv pip install -e .[dev]
