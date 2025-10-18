#!/usr/bin/env python3
"""
Test runner for integrated_widgets tests.

This script runs all pytest tests in the tests/ directory with enhanced visualization.
"""

import sys
import os
import pytest
import time
from typing import Any, List


class TestProgressPlugin:
    """Pytest plugin to track test progress and provide visualization."""
    
    def __init__(self) -> None:
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        self.error_tests = 0
        self.current_test = ""
        self.start_time: float | None = None
        self.test_times: List[float] = []
        self.result_chars: List[str] = []  # Store the result characters
        
    def pytest_collection_modifyitems(self, config: Any, items: Any) -> None:
        """Called after test collection."""
        self.total_tests = len(items)
        self.start_time = time.time()
        print(f"\n{'='*80}")
        print(f"🧪 INTEGRATED WIDGETS TEST SUITE")
        print(f"{'='*80}")
        print(f"📊 Collected {self.total_tests} tests")
        print(f"⏰ Started at {time.strftime('%H:%M:%S')}")
        print(f"{'='*80}\n")
        
    def pytest_runtest_logstart(self, nodeid: str, location: Any) -> None:
        """Called when a test starts running."""
        self.current_test = os.path.basename(nodeid)
        
    def pytest_runtest_logreport(self, report: Any) -> None:
        """Called when a test report is generated."""
        if report.when == "call":  # Only count actual test execution
            if report.outcome == "passed":
                self.passed_tests += 1
                status = "."
                color = "\033[92m"  # Green
            elif report.outcome == "failed":
                self.failed_tests += 1
                status = "F"
                color = "\033[91m"  # Red
            elif report.outcome == "skipped":
                self.skipped_tests += 1
                status = "s"
                color = "\033[93m"  # Yellow
            else:
                self.error_tests += 1
                status = "E"
                color = "\033[95m"  # Magenta
                
            # Calculate progress
            completed = self.passed_tests + self.failed_tests + self.skipped_tests + self.error_tests
            progress_percent = (completed / self.total_tests) * 100 if self.total_tests > 0 else 0
            
            # Add the result character to our list
            self.result_chars.append(f"{color}{status}\033[0m")
            
            # Calculate elapsed time
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            
            # Print progress with accumulated result characters
            result_display = "".join(self.result_chars)
            print(f"\r{result_display} {progress_percent:5.1f}% "
                  f"({completed}/{self.total_tests}) | ⏱️  {elapsed_time:.1f}s | "
                  f"{self.current_test[:60]:<60}", end="", flush=True)
            
            # Print newline for failed tests to show details
            if report.outcome in ["failed", "error"]:
                print()  # New line for failed tests
                
    def pytest_sessionfinish(self, session: Any, exitstatus: int) -> None:
        """Called when the test session finishes."""
        total_time = time.time() - self.start_time if self.start_time else 0
        
        print(f"\n\n{'='*80}")
        print(f"📈 TEST RESULTS SUMMARY")
        print(f"{'='*80}")
        
        # Results breakdown
        print(f"✅ Passed:  {self.passed_tests:3d} ({self.passed_tests/self.total_tests*100:5.1f}%)")
        print(f"❌ Failed:  {self.failed_tests:3d} ({self.failed_tests/self.total_tests*100:5.1f}%)")
        print(f"⏭️  Skipped: {self.skipped_tests:3d} ({self.skipped_tests/self.total_tests*100:5.1f}%)")
        print(f"💥 Errors:  {self.error_tests:3d} ({self.error_tests/self.total_tests*100:5.1f}%)")
        print(f"📊 Total:   {self.total_tests:3d} tests")
        
        print(f"\n⏱️  Total time: {total_time:.2f} seconds")
        print(f"⚡ Average: {total_time/self.total_tests:.3f} seconds per test")
        
        # Success rate visualization
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100.0:
            print("🎉 ALL TESTS PASSED! 🎉")
        elif success_rate >= 90.0:
            print("👍 Great job! Almost all tests passing.")
        elif success_rate >= 75.0:
            print("⚠️  Some tests need attention.")
        else:
            print("🚨 Multiple test failures detected!")
            
        print(f"{'='*80}\n")


def main() -> int:
    """Run all tests using pytest with enhanced visualization."""
    # Add the project root to Python path so 'tests' module can be imported
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Create progress plugin
    progress_plugin = TestProgressPlugin()
    
    # Configure pytest arguments
    args = [
        "tests/",  # Run tests in tests/ directory
        "--tb=short",  # Short traceback format
        "--color=yes",  # Colored output
        "-q",  # Quiet mode to reduce noise
    ]
    
    # Add any additional arguments passed to this script
    args.extend(sys.argv[1:])
    
    # Run pytest with our plugin
    return pytest.main(args, plugins=[progress_plugin])


if __name__ == "__main__":
    sys.exit(main())

