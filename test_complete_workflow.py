#!/usr/bin/env python3
"""
Test the complete user workflow for the AI Content Optimizer
"""

import sys
import os
import time
import requests
import json
from urllib.parse import urlparse

def test_complete_workflow(base_url):
    """Test the complete user workflow: signup, login, optimize content"""
    
    print(f"🧪 Testing complete workflow on {base_url}")
    print("=" * 60)
    
    print("\n📝 Testing signup...")
    test_email = f"test_user_{int(time.time())}@example.com"
    test_password = "TestPassword123!"
    
    signup_data = {
        "email": test_email,
        "password": test_password
    }
    
    signup_response = requests.post(
        f"{base_url}/api/signup",
        json=signup_data
    )
    
    if signup_response.status_code == 200 and signup_response.json().get('success'):
        print(f"✅ Signup successful for {test_email}")
    else:
        print(f"❌ Signup failed: {signup_response.text}")
        if "Email already exists" in signup_response.text:
            print("   Using existing account for login test")
        else:
            return False
    
    print("\n🔑 Testing login...")
    login_data = {
        "email": test_email,
        "password": test_password
    }
    
    session = requests.Session()
    login_response = session.post(
        f"{base_url}/api/login",
        json=login_data
    )
    
    if login_response.status_code == 200 and login_response.json().get('success'):
        print(f"✅ Login successful for {test_email}")
    else:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    print("\n📊 Testing dashboard access...")
    dashboard_response = session.get(f"{base_url}/dashboard")
    
    if dashboard_response.status_code == 200 and "AI Content Optimization" in dashboard_response.text:
        print("✅ Dashboard access successful")
    else:
        print(f"❌ Dashboard access failed: {dashboard_response.status_code}")
        return False
    
    print("\n🤖 Testing AI content optimization...")
    test_content = "Transform your business with cutting-edge artificial intelligence solutions. Our AI platform helps companies automate processes, gain insights from data, and improve customer experiences. Whether you're looking to streamline operations or enhance decision-making, our advanced machine learning algorithms deliver measurable results that drive growth and innovation."
    
    optimize_data = {
        "content": test_content,
        "target_audience": "Business"
    }
    
    optimize_response = session.post(
        f"{base_url}/api/optimize",
        json=optimize_data
    )
    
    if optimize_response.status_code == 200:
        result = optimize_response.json()
        if result.get('success'):
            print("✅ Content optimization successful")
            print(f"   Engagement Score: {result.get('engagement_score')}/100")
            print(f"   Improvements: {len(result.get('improvements', []))} suggestions")
            print(f"   Usage Count: {result.get('usage_count')}/5")
        else:
            print(f"❌ Optimization failed: {result.get('error')}")
            return False
    else:
        print(f"❌ Optimization request failed: {optimize_response.status_code}")
        print(optimize_response.text)
        return False
    
    print("\n🎉 Complete workflow test PASSED!")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "http://localhost:5000"
    
    success = test_complete_workflow(url)
    sys.exit(0 if success else 1)
