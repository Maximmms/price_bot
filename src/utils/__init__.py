from src.utils.loggers.bot_logger import BotLogger

backend_logger = BotLogger("backend", log_file="logs/backend.log")
bot_logger = BotLogger("bot", log_file="logs/bot.log")