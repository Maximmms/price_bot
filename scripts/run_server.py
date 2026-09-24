"""Entry point для запуска FastAPI сервера."""

import sys
import os

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn


def main():
    """Запуск сервера."""
    uvicorn.run(
        "app.backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )


if __name__ == '__main__':
    main()
