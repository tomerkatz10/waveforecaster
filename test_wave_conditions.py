#!/usr/bin/env python3
"""
Test file for wave condition assessment functionality
Tests the MarineWeatherExtractor.assess_wave_conditions method
"""

import sys
import os

# Add the current directory to the path so we can import extract_info
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extract_info import MarineWeatherExtractor

def test_wave_conditions():
    """Test the wave condition assessment logic"""
    print("=== Testing Wave Condition Assessment ===")
    
    # Initialize the extractor
    extractor = MarineWeatherExtractor()
    
    # Test cases with expected results
    test_cases = [
        # (wave_height, swell_height, swell_period, expected_result, description)
        (0.1, 0.3, 5.0, 'Bad', 'Too small wave'),
        (0.5, 0.3, 6.0, 'Bad', 'Too small swell'),
        (0.5, 0.6, 5.5, 'OK', 'Acceptable conditions'),
        (0.5, 0.6, 6.0, 'OK', 'Should be OK'),
        (0.6, 0.6, 6.0, 'OK', 'Should be OK'),
        (1.0, 0.8, 7.0, 'OK', 'Acceptable conditions'),
        (1.0, 0.8, 7.5, 'Good', 'Should be Good'),
        (2.0, 1.5, 10.0, 'Good', 'Should be Good'),
        (3.0, 2.0, 12.0, 'Good', 'Should be Good'),
        (3.2, 2.5, 15.0, 'Good', 'At upper limit of Good'),
        (4.0, 3.0, 18.0, 'OK', 'Should be OK'),
        (4.5, 3.5, 19.0, 'Bad', 'Too high wave height'),
        (5.0, 4.0, 20.0, 'Bad', 'Too high wave'),
        
        # Additional edge cases for Israeli Mediterranean conditions
        (0.4, 0.4, 4.5, 'Bad', 'Too small wave and swell'),
        (0.5, 0.4, 4.5, 'Bad', 'Too small swell height'),
        (0.8, 0.6, 6.5, 'OK', 'Typical Mediterranean conditions'),
        (1.5, 1.2, 8.0, 'Good', 'Good Mediterranean conditions'),
        (2.5, 2.0, 11.0, 'Good', 'Excellent conditions'),
        (3.8, 3.2, 14.0, 'OK', 'Large but manageable'),
        (4.2, 3.8, 17.0, 'Bad', 'Too high wave height'),
        (4.8, 4.2, 19.0, 'Bad', 'Too high for safety'),
    ]
    
    passed = 0
    failed = 0
    
    for i, (wh, sh, sp, expected, description) in enumerate(test_cases):
        result = extractor.assess_wave_conditions(wh, sh, sp)
        status = "✓" if result == expected else "✗"
        
        if result == expected:
            passed += 1
            print(f"Test {i+1:2d}: ✓ Wave={wh}m, Swell={sh}m, Period={sp}s → {result} (expected: {expected})")
        else:
            failed += 1
            print(f"Test {i+1:2d}: ✗ Wave={wh}m, Swell={sh}m, Period={sp}s → {result} (expected: {expected}) - {description}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    print(f"Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"❌ {failed} test(s) failed")
    
    return failed == 0

def test_threshold_boundaries():
    """Test the boundary conditions for each rating"""
    print("\n=== Testing Threshold Boundaries ===")
    
    extractor = MarineWeatherExtractor()
    
    # Test OK to Bad boundary
    print("Testing OK to Bad boundary:")
    print(f"Wave=0.4m, Swell=0.3m, Period=4.0s → {extractor.assess_wave_conditions(0.4, 0.3, 4.0)}")
    print(f"Wave=0.5m, Swell=0.3m, Period=4.0s → {extractor.assess_wave_conditions(0.5, 0.3, 4.0)}")
    
    # Test Bad to OK boundary
    print("\nTesting Bad to OK boundary:")
    print(f"Wave=0.4m, Swell=0.3m, Period=4.9s → {extractor.assess_wave_conditions(0.4, 0.3, 4.9)}")
    print(f"Wave=0.5m, Swell=0.4m, Period=5.0s → {extractor.assess_wave_conditions(0.5, 0.4, 5.0)}")
    
    # Test OK to Good boundary
    print("\nTesting OK to Good boundary:")
    print(f"Wave=0.9m, Swell=0.7m, Period=7.4s → {extractor.assess_wave_conditions(0.9, 0.7, 7.4)}")
    print(f"Wave=1.0m, Swell=0.8m, Period=7.5s → {extractor.assess_wave_conditions(1.0, 0.8, 7.5)}")

def main():
    """Main test function"""
    print("Wave Condition Assessment Test Suite")
    print("=" * 50)
    
    # Run main tests
    success = test_wave_conditions()
    
    # Run boundary tests
    test_threshold_boundaries()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
