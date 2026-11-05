#!/usr/bin/env python3
"""
Test suite for Stata Simulator
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stata_simulator import StataEngine
import pandas as pd
import numpy as np


def create_sample_data():
    """Create sample data for testing."""
    np.random.seed(42)
    n = 100

    data = pd.DataFrame({
        'id': range(1, n + 1),
        'price': np.random.uniform(5000, 50000, n),
        'mpg': np.random.uniform(15, 45, n),
        'weight': np.random.uniform(1500, 5000, n),
        'length': np.random.uniform(150, 250, n),
        'foreign': np.random.choice([0, 1], n),
        'rep78': np.random.choice([1, 2, 3, 4, 5], n),
    })

    return data


def test_local_macros():
    """Test local macro functionality."""
    print("Testing local macros...")
    engine = StataEngine()

    result = engine._cmd_local("myvar = 42")
    assert result.success, f"Local macro failed: {result.error}"

    result = engine._cmd_display("Testing macro: `myvar'")
    assert result.success, f"Display failed: {result.error}"

    print("  PASS: Local macros")


def test_data_commands():
    """Test data manipulation commands."""
    print("Testing data commands...")
    engine = StataEngine()

    # Create sample data
    engine.data = create_sample_data()

    # Test describe
    result = engine._cmd_describe("")
    assert result.success, f"Describe failed: {result.error}"
    assert "Variables: 7" in result.output

    # Test summarize
    result = engine._cmd_summarize("")
    assert result.success, f"Summarize failed: {result.error}"
    assert "Mean" in result.output

    # Test correlate
    result = engine._cmd_correlate("price mpg weight")
    assert result.success, f"Correlate failed: {result.error}"

    print("  PASS: Data commands")


def test_generate_replace():
    """Test generate and replace commands."""
    print("Testing generate and replace...")
    engine = StataEngine()
    engine.data = create_sample_data()

    # Test generate
    result = engine._cmd_generate("log_price = log(price)")
    assert result.success, f"Generate failed: {result.error}"
    assert "log_price" in engine.data.columns

    # Test replace
    result = engine._cmd_replace("price = price * 1.1")
    assert result.success, f"Replace failed: {result.error}"

    print("  PASS: Generate and replace")


def test_rename_drop():
    """Test rename and drop commands."""
    print("Testing rename and drop...")
    engine = StataEngine()
    engine.data = create_sample_data()

    # Test rename
    result = engine._cmd_rename("price car_price")
    assert result.success, f"Rename failed: {result.error}"
    assert "car_price" in engine.data.columns
    assert "price" not in engine.data.columns

    # Test drop
    result = engine._cmd_drop("mpg")
    assert result.success, f"Drop failed: {result.error}"
    assert "mpg" not in engine.data.columns

    print("  PASS: Rename and drop")


def test_sort():
    """Test sort command."""
    print("Testing sort...")
    engine = StataEngine()
    engine.data = create_sample_data()

    result = engine._cmd_sort("price")
    assert result.success, f"Sort failed: {result.error}"
    assert engine.data['price'].iloc[0] <= engine.data['price'].iloc[1]

    print("  PASS: Sort")


def test_tabulate():
    """Test tabulate command."""
    print("Testing tabulate...")
    engine = StataEngine()
    engine.data = create_sample_data()

    result = engine._cmd_tabulate("foreign")
    assert result.success, f"Tabulate failed: {result.error}"
    assert "Freq" in result.output

    print("  PASS: Tabulate")


def test_display():
    """Test display command."""
    print("Testing display...")
    engine = StataEngine()

    result = engine._cmd_display("Hello, Stata!")
    assert result.success, f"Display failed: {result.error}"
    assert "Hello, Stata!" in result.output

    print("  PASS: Display")


def test_count():
    """Test count command."""
    print("Testing count...")
    engine = StataEngine()
    engine.data = create_sample_data()

    result = engine._cmd_count("")
    assert result.success, f"Count failed: {result.error}"
    assert "100" in result.output

    print("  PASS: Count")


def test_mean():
    """Test mean command."""
    print("Testing mean...")
    engine = StataEngine()
    engine.data = create_sample_data()

    result = engine._cmd_mean("price mpg")
    assert result.success, f"Mean failed: {result.error}"
    assert "Mean estimation" in result.output

    print("  PASS: Mean")


def test_multiline_code():
    """Test multiline code execution."""
    print("Testing multiline code...")
    engine = StataEngine()
    engine.data = create_sample_data()

    code = """
    generate log_price = log(price)
    generate price_category = 1 if price < 15000
    replace price_category = 2 if price >= 15000 & price < 30000
    replace price_category = 3 if price >= 30000
    summarize price log_price price_category
    """

    results = engine.execute(code)
    success_count = sum(1 for r in results if r.success)
    assert success_count >= 3, f"Expected at least 3 successful commands, got {success_count}"

    print("  PASS: Multiline code")


def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("Stata Simulator Test Suite")
    print("=" * 50)
    print()

    tests = [
        test_local_macros,
        test_data_commands,
        test_generate_replace,
        test_rename_drop,
        test_sort,
        test_tabulate,
        test_display,
        test_count,
        test_mean,
        test_multiline_code,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

    print()
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
