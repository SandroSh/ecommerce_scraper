"""
Unit tests for logger module.
"""

import unittest
import tempfile
import os
import logging
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.logger import get_logger


class TestLogger(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_default_logger(self):
        """Test default logger creation."""
        logger = get_logger()
        
        self.assertEqual(logger.name, "scraper")
        self.assertEqual(logger.level, logging.INFO)
        self.assertEqual(len(logger.handlers), 2)
    
    def test_custom_logger(self):
        """Test custom logger creation."""
        logger = get_logger("test_logger", self.log_file)
        
        self.assertEqual(logger.name, "test_logger")
        self.assertEqual(len(logger.handlers), 2)
        
        # Check file handler
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        self.assertEqual(len(file_handlers), 1)
    
    def test_logger_deduplication(self):
        """Test logger handler deduplication."""
        logger1 = get_logger("test_logger")
        initial_count = len(logger1.handlers)
        
        logger2 = get_logger("test_logger")
        
        self.assertIs(logger1, logger2)
        self.assertEqual(len(logger2.handlers), initial_count)
    
    def test_logging_functionality(self):
        """Test actual logging."""
        logger = get_logger("test_logger", self.log_file)
        
        test_message = "Test log message"
        logger.info(test_message)
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
            self.assertIn(test_message, log_content)
            self.assertIn("INFO", log_content)
    
    def test_multiple_loggers(self):
        """Test creating multiple loggers."""
        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")
        
        self.assertIsNot(logger1, logger2)
        self.assertEqual(logger1.name, "logger1")
        self.assertEqual(logger2.name, "logger2")


if __name__ == '__main__':
    unittest.main() 