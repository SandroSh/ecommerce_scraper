"""
Logging Utilities Module

This module provides centralized logging functionality for the ecommerce scraper project.
It includes a factory function for creating configured logger instances with both
console and file output capabilities.

The module ensures consistent logging configuration across all components
of the scraper system, including proper formatting, encoding, and handler management.

Features:
- Console and file logging
- UTF-8 encoding support
- Consistent formatting across all loggers
- Handler deduplication prevention
- Configurable log levels and formats
"""

import logging
import os
import sys

def get_logger(name: str = "scraper", log_file: str = "scraper.log") -> logging.Logger:
    """
    Create and configure a logger instance with both console and file output.
    
    This function creates a logger with the specified name and configures it
    with both stream (console) and file handlers. It prevents duplicate
    handlers from being added when the function is called multiple times
    with the same logger name.
    
    Args:
        name (str): The name of the logger. Defaults to "scraper".
        log_file (str): The filename for the log file. Defaults to "scraper.log".
    
    Returns:
        logging.Logger: A configured logger instance with both console and file output.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
