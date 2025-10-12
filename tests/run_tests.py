#!/usr/bin/env python3
"""
Test runner for integrated_widgets tests.

This script runs all pytest tests in the tests/ directory.
"""

import sys
import pytest


def main() -> int:
    """Run all tests using pytest."""
    # Configure pytest arguments
    args = [
        "tests/",  # Run tests in tests/ directory
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--color=yes",  # Colored output
    ]
    
    # Add any additional arguments passed to this script
    args.extend(sys.argv[1:])
    
    # Run pytest
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(main())

