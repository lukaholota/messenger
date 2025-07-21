PYTHON_WORKER_COMMAND = python -m workers.regular_message_worker
FRONTEND_DIR = messenger-frontend
NPM_DEV_COMMAND = npm run dev

.PHONY: run-worker run-frontend help

run-worker:
	@echo "Запускаю Python worker..."
	$(PYTHON_WORKER_COMMAND)
	@echo "Python worker завершив роботу."

run-frontend:
	@echo "Переходжу до директорії фронтенду та запускаю dev-сервер..."
	cd $(FRONTEND_DIR) && $(NPM_DEV_COMMAND)
	@echo "Фронтенд dev-сервер запущений."

help:
	@echo "Доступні команди:"
	@echo "  make run-worker    - Запускає Python worker (workers.regular_message_worker)."
	@echo "  make run-frontend  - Переходить до ./messenger-frontend/ та запускає 'npm run dev'."
	@echo "  make help          - Показує цей список команд."