#!/usr/bin/env python3
"""
Test script to verify Flask app works correctly
"""

import os
import sys

def test_app():
    print("🧪 Testing Technical Analysis Dashboard...")
    
    # Check if all required files exist
    required_files = ['app.py', 'dashboard.html', 'requirements.txt', 'Procfile', 'runtime.txt']
    
    print("\n📁 File Check:")
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING!")
            return False
    
    # Test import
    print("\n🔍 Import Test:")
    try:
        from app import app
        print("   ✅ Flask app import successful")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test basic routes
    print("\n🌐 Route Test:")
    try:
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("   ✅ /health endpoint working")
            else:
                print(f"   ❌ /health failed: {response.status_code}")
            
            # Test API endpoint
            response = client.get('/api/data/RELIANCE')
            if response.status_code == 200:
                print("   ✅ /api/data/RELIANCE endpoint working")
            else:
                print(f"   ❌ /api/data/RELIANCE failed: {response.status_code}")
            
            # Test main dashboard
            response = client.get('/')
            if response.status_code == 200:
                print("   ✅ / (dashboard) endpoint working")
            else:
                print(f"   ❌ / (dashboard) failed: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Route test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! App is ready for Railway deployment.")
    return True

if __name__ == '__main__':
    success = test_app()
    sys.exit(0 if success else 1)