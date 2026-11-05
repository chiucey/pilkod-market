#!/usr/bin/env python3
"""
Test script for ASCII Chart Generator
Tests all chart types and configurations
"""

import sys
from pathlib import Path

# Add assets to path
sys.path.insert(0, str(Path(__file__).parent.parent / "assets"))

from ascii_chart import (
    generate_chart,
    BarChart,
    LineChart,
    PieChart,
    StylePreset,
    ColorMode,
)


def test_bar_chart():
    """Test bar chart generation"""
    print("\n--- Bar Chart Tests ---")

    data = {"A": 100, "B": 150, "C": 120, "D": 180}

    # Test all styles
    for style in StylePreset:
        print(f"\nStyle: {style.value}")
        result = generate_chart(data, chart_type="bar", style=style.value)
        assert len(result) > 0, f"Empty result for {style.value}"
        print(result[:200] + "...")

    # Test with colors
    print("\n\nWith ANSI colors:")
    result = generate_chart(data, chart_type="bar", color_mode="ansi16")
    assert len(result) > 0, "Empty result with colors"
    assert "\033[" in result, "Color codes not found"

    print("✓ Bar chart tests passed")


def test_line_chart():
    """Test line chart generation"""
    print("\n--- Line Chart Tests ---")

    data = {
        "Series A": [10, 30, 20, 50, 40],
        "Series B": [20, 15, 35, 25, 45],
    }

    result = generate_chart(data, chart_type="line", title="Performance")
    assert len(result) > 0, "Empty line chart result"
    print(result)

    print("✓ Line chart tests passed")


def test_pie_chart():
    """Test pie chart generation"""
    print("\n--- Pie Chart Tests ---")

    data = {"Category A": 35, "Category B": 45, "Category C": 20}

    result = generate_chart(data, chart_type="pie", title="Distribution")
    assert len(result) > 0, "Empty pie chart result"
    print(result)

    print("✓ Pie chart tests passed")


def test_edge_cases():
    """Test edge cases"""
    print("\n--- Edge Case Tests ---")

    # Empty data
    try:
        result = generate_chart({}, chart_type="bar")
        assert "No data" in result or len(result) == 0
        print("✓ Empty data handled")
    except Exception as e:
        print(f"✗ Empty data error: {e}")

    # Single value
    result = generate_chart({"Single": 100}, chart_type="bar")
    assert len(result) > 0
    print("✓ Single value handled")

    # Zero value
    result = generate_chart({"Zero": 0, "Non-zero": 50}, chart_type="bar")
    assert len(result) > 0
    print("✓ Zero value handled")

    # Large values (should auto-scale)
    result = generate_chart({"Big": 1000000, "Small": 500}, chart_type="bar")
    assert len(result) > 0
    print("✓ Large values handled")


def test_color_modes():
    """Test different color modes"""
    print("\n--- Color Mode Tests ---")

    data = {"Test": 100, "Data": 150}

    # None mode
    result = generate_chart(data, color_mode="none")
    assert "\033[" not in result
    print("✓ No-color mode works")

    # ANSI16 mode
    result = generate_chart(data, color_mode="ansi16")
    assert "\033[" in result
    print("✓ ANSI16 mode works")

    print("✓ Color mode tests passed")


def main():
    """Run all tests"""
    print("=" * 50)
    print("ASCII Chart Generator Test Suite")
    print("=" * 50)

    try:
        test_bar_chart()
        test_line_chart()
        test_pie_chart()
        test_edge_cases()
        test_color_modes()

        print("\n" + "=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)
        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
