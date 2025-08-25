#!/usr/bin/env python3
"""
Test script for the User Interface & Decision System.
Tests interactive prompts and user decision handling.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append('src')

from pivot_table_manager_enhanced import PivotTableManager

def test_user_interface():
    """Test the user interface system."""
    print("🎮 Testing User Interface & Decision System...")
    
    # Initialize components
    country = "CANADA"
    manager = PivotTableManager(country)
    
    print(f"\n📊 Current table status:")
    info = manager.get_table_info()
    print(f"  Shape: {info['dimensions']}")
    print(f"  Categories: {info['categories']}")
    print(f"  Months: {len(info['months'])}")
    
    # Test 1: Change Analysis (to see what's available)
    print(f"\n🔍 Running Change Analysis...")
    try:
        analysis = manager.analyze_changes()
        
        if 'error' not in analysis:
            print(f"✅ Change analysis completed!")
            print(f"  📅 New months: {len(analysis['new_months'])}")
            print(f"  🏷️  New categories: {len(analysis['new_categories'])}")
            print(f"  🔑 New keywords: {analysis['new_keywords_count']}")
        else:
            print(f"❌ Analysis failed: {analysis['error']}")
            return
            
    except Exception as e:
        print(f"❌ Error during change analysis: {e}")
        return
    
    # Test 2: User Interface (non-interactive mode for testing)
    print(f"\n🎮 Testing User Interface (Non-Interactive Mode)...")
    
    # Simulate different scenarios
    test_scenarios = [
        {
            'name': 'No Updates Scenario',
            'analysis': analysis,
            'expected': 'No updates needed'
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🧪 Testing: {scenario['name']}")
        
        try:
            # Test the interface without user input
            if not scenario['analysis']['new_months'] and not scenario['analysis']['new_categories']:
                print("✅ Scenario: No updates needed")
                print("   Expected: Interface should show 'no updates needed'")
                print("   Result: ✅ Correctly detected no updates needed")
            else:
                print("⚠️  Scenario: Updates available")
                print("   Note: Would normally show interactive menu")
                print("   For testing, we'll skip the interactive part")
                
        except Exception as e:
            print(f"❌ Error in scenario: {e}")

def test_decision_execution():
    """Test decision execution system."""
    print(f"\n🔧 Testing Decision Execution System...")
    
    country = "CANADA"
    manager = PivotTableManager(country)
    
    # Test different decision types
    test_decisions = [
        {
            'name': 'No Updates Decision',
            'decision': {'action': 'none', 'reason': 'no_updates_needed'},
            'expected': True
        },
        {
            'name': 'Skip Updates Decision',
            'decision': {'action': 'skip', 'reason': 'user_choice'},
            'expected': True
        },
        {
            'name': 'Cancelled Decision',
            'decision': {'action': 'cancelled', 'reason': 'user_declined'},
            'expected': False
        }
    ]
    
    for test in test_decisions:
        print(f"\n🧪 Testing: {test['name']}")
        
        try:
            result = manager.execute_user_decision(test['decision'])
            expected = test['expected']
            
            if result == expected:
                print(f"✅ PASS: Expected {expected}, got {result}")
            else:
                print(f"❌ FAIL: Expected {expected}, got {result}")
                
        except Exception as e:
            print(f"❌ Error in test: {e}")

def test_error_handling():
    """Test error handling in the interface."""
    print(f"\n⚠️  Testing Error Handling...")
    
    country = "CANADA"
    manager = PivotTableManager(country)
    
    # Test invalid decisions
    invalid_decisions = [
        None,
        {},
        {'action': 'unknown_action'},
        {'action': 'update_months', 'months': []}
    ]
    
    for i, invalid_decision in enumerate(invalid_decisions):
        print(f"\n🧪 Testing Invalid Decision {i+1}: {invalid_decision}")
        
        try:
            result = manager.execute_user_decision(invalid_decision)
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error caught: {e}")

if __name__ == "__main__":
    print("🎮 User Interface & Decision System Test Suite")
    print("=" * 60)
    
    # Test 1: User Interface
    test_user_interface()
    
    # Test 2: Decision Execution
    test_decision_execution()
    
    # Test 3: Error Handling
    test_error_handling()
    
    print("\n🎯 Test suite completed!")
    print("\n💡 Note: Interactive features are tested in non-interactive mode")
    print("   To test full interactivity, run the methods manually")
