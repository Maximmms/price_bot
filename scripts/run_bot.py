"""Entry point для запуска Telegram бота."""

import sys
import os

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.frontend.bot import Bot


def main():
    """Запуск бота."""
    Bot().run()


if __name__ == '__main__':
    main()
