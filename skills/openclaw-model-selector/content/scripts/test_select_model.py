#!/usr/bin/env python3
"""
Test script for select_model.py
Tests the model selection logic
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from select_model import analyze_task, select_best_model, MODEL_CAPABILITIES


def test_task_analysis():
    """Test task analysis function"""
    test_cases = [
        # (input, expected_primary_task)
        ("Help me write a Python quicksort function", "code-programming"),
        ("Write an essay about spring", "creative-writing"),
        ("Explain what machine learning is", "technical-analysis"),
        ("What's the weather like today", "quick-qa"),
        ("Calculate 2+2 equals what", "math-calculation"),
        ("Translate this paragraph to English", "translation"),
        ("Help me analyze sales data", "data-processing"),
        ("Design a user login system", "system-design"),
    ]

    print("Testing task analysis...")
    all_passed = True

    for task, expected in test_cases:
        result = analyze_task(task)
        status = "PASS" if result["primary_task"] == expected else "FAIL"
        if result["primary_task"] != expected:
            all_passed = False
        print(f"  {status} '{task}' -> {result['primary_task']} (expected: {expected})")

    return all_passed


def test_model_selection():
    """Test model selection function"""
    test_cases = [
        # (task, expected_models)
        ("Help me write a Python function", ["claude-code", "sonnet", "opus", "gpt-4"]),
        ("Write a creative story", ["gpt-4", "sonnet", "opus"]),
        # Quantum computing is complex technical explanation, opus is a reasonable choice
        ("What is quantum computing", ["opus", "sonnet", "haiku", "gpt-4"]),
        ("Help me design a distributed system", ["opus", "sonnet", "gpt-4"]),
    ]

    print("\nTesting model selection...")
    all_passed = True

    for task, expected_models in test_cases:
        analysis = analyze_task(task)
        selected = select_best_model(analysis)

        # Check if selected model is in expected list
        status = "PASS" if selected in expected_models else "FAIL"
        if selected not in expected_models:
            all_passed = False
        print(f"  {status} '{task}' -> {selected}")

    return all_passed


def test_model_capabilities():
    """Test that all models have required attributes"""
    print("\nTesting model capabilities...")

    required_attrs = ["name", "strengths", "speed", "context_window", "best_for"]
    all_passed = True

    for model_id, model in MODEL_CAPABILITIES.items():
        missing = [attr for attr in required_attrs if attr not in model]
        if missing:
            print(f"  FAIL {model_id}: missing attributes {missing}")
            all_passed = False
        else:
            print(f"  PASS {model_id}: all attributes present")

    return all_passed


def main():
    print("=" * 60)
    print("OpenClaw Model Selector - Test Report")
    print("=" * 60)
    print()

    results = []

    results.append(("Task Analysis", test_task_analysis()))
    results.append(("Model Selection", test_model_selection()))
    results.append(("Model Capabilities", test_model_capabilities()))

    print()
    print("=" * 60)
    print("Summary:")
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
