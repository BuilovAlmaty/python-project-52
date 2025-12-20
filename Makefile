MANAGE := uv run python3 task_manager/manage.py
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
	gunicorn task_manager.wsgi
