#!/usr/bin/env python3
"""
Main test runner that executes all test suites.
"""

import sys
import os
from pathlib import Path
import time
import subprocess

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def run_test_file(test_file, image_path=None):
    """
    Run a test file and return (success, output).
    """
    try:
        cmd = [sys.executable, test_file]
        if image_path and ("image_parser" in test_file or "grid_detection" in test_file or 
                          "piece_detection" in test_file or "constraint_detection" in test_file or 
                          "solver_integration" in test_file or "visual_debug" in test_file):
            cmd.append(image_path)
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def run_all_tests(image_path=None, include_visual=False):
    """
    Run all test suites and generate comprehensive report.
    """
    print("🎯 TANGO SOLVER - TEST")
    print("=" * 70)
    print("Running all test modules")
    print()
    
    # Test files to run
    test_files = [
        ("Image Parser", "test_image_parser.py"),
        ("Grid Detection", "test_grid_detection.py"), 
        ("Piece Detection", "test_piece_detection.py"),
        ("Constraint Detection", "test_constraint_detection.py"),
        ("Constraint Classifier", "test_constraint_classifier.py"),
        ("Solver Integration", "test_solver_integration.py"),
    ]
    
    # Visual debug tests
    visual_tests = [
        ("Visual Debug", "test_visual_debug.py"),
    ]
    
    results = []
    
    print("📋 Running standard tests...")
    print()
    
    for test_name, test_file in test_files:
        print(f"🔄 Running {test_name} tests...")
        
        test_path = Path(__file__).parent / test_file
        if not test_path.exists():
            print(f"❌ Test file not found: {test_file}")
            results.append((test_name, False, f"File not found: {test_file}"))
            continue
        
        success, stdout, stderr = run_test_file(str(test_path), image_path)
        
        if success:
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
            if stderr:
                print(f"   Error: {stderr.strip()}")
        
        results.append((test_name, success, stderr if stderr else ""))
        print()
    
    # Run visual tests if requested
    if include_visual and image_path:
        print("🎨 Running visual debugging tests...")
        print()
        
        for test_name, test_file in visual_tests:
            print(f"🔄 Running {test_name} tests...")
            
            test_path = Path(__file__).parent / test_file
            if not test_path.exists():
                print(f"❌ Test file not found: {test_file}")
                results.append((test_name, False, f"File not found: {test_file}"))
                continue
            
            success, stdout, stderr = run_test_file(str(test_path), image_path)
            
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                if stderr:
                    print(f"   Error: {stderr.strip()}")
            
            results.append((test_name, success, stderr if stderr else ""))
            print()
    elif image_path:
        print("🎨 Visual debugging tests available!")
        print("   These generate PNG visualizations of grid detection and constraints.")
        print("   Run with --visual flag to include visual tests")
        print("   Or run manually: python3 tests/test_visual_debug.py [image_path]")
        print()
    
    # Generate final report
    print("📊 FINAL TEST REPORT")
    print("=" * 60)
    print(f"Image analyzed: {image_path if image_path else 'N/A'}")
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for test_name, success, error in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status:12} {test_name}")
        if error and not success:
            print(f"             Error: {error.strip()}")



if __name__ == "__main__":
    # Parse command line arguments
    include_visual = "--visual" in sys.argv
    if include_visual:
        sys.argv.remove("--visual")
    
    # Determine image to use
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = None
        if not image_path:
            print("❌ No image found. Please provide image path as argument.")
            print("Usage: python3 -m tests.test_runner [image_path] [--visual]")
            print("  --visual: Include visual debugging tests (generates PNG files)")
            sys.exit(1)
    
    # Run all tests
    success = run_all_tests(image_path, include_visual)
    sys.exit(0 if success else 1)
