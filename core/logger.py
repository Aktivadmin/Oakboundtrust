import logging
import os
import sys

# Create a custom logger for your app
logger = logging.getLogger("upgrowth")

# Set the minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
logger.setLevel(logging.DEBUG)

# Formatter for logs
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# Console handler (logs to stdout)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

# Add handlers if not already added
if not logger.hasHandlers():
    logger.addHandler(console_handler)
    # Vercel's filesystem is read-only, so only write app.log when not deployed there
    if not os.getenv("VERCEL"):
        file_handler = logging.FileHandler("app.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
