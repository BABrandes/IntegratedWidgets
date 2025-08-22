"""
Utilities for demo applications.

This module provides common utilities and helpers used across all demo applications,
including logging configuration and other shared functionality.
"""

import logging
import sys


# Create a console logger for demo applications
demo_logger = logging.getLogger("demo_logger")
demo_logger.setLevel(logging.DEBUG)

# Avoid duplicate handlers if logger already exists
if not demo_logger.handlers:
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Create formatter
    format_string = "[%(asctime)s] %(name)s - %(levelname)s: %(message)s"
    formatter = logging.Formatter(
        fmt=format_string,
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    demo_logger.addHandler(console_handler)


# Create a debug logger for detailed troubleshooting
debug_logger = logging.getLogger("debug_logger")
debug_logger.setLevel(logging.DEBUG)

# Avoid duplicate handlers if logger already exists
if not debug_logger.handlers:
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Create formatter with more detailed information
    debug_format = "[%(asctime)s] %(name)s - %(levelname)s [%(filename)s:%(lineno)d]: %(message)s"
    formatter = logging.Formatter(
        fmt=debug_format,
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    debug_logger.addHandler(console_handler)
