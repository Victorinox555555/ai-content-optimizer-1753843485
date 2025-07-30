#!/usr/bin/env python3
"""
Test the autonomous deployment system with all provided credentials
"""

import sys
import os
import time
sys.path.append('/tmp/test_skill_output')

from autonomous_deployer import AutonomousDeployer
from credential_manager import CredentialManager
from email_integration import EmailService
from domain_management import DomainManager

def test_credential_manager():
    """Test the credential manager with all provided credentials"""
    print("🔑 Testing Credential Manager...")
    
    cred_manager = CredentialManager()
    validation = cred_manager.validate_credentials()
    
    print(f"   Readiness: {validation['readiness_score']} ({validation['percentage']}%)")
    print(f"   Platform Deployment: {validation['platform_deployment']}")
    print(f"   GitHub Automation: {validation['github_automation']}")
    print(f"   Domain Management: {validation['domain_management']}")
    print(f"   Email Services: {validation['email_services']}")
    print(f"   Core Services: {validation['core_services']}")
    
    missing = cred_manager.get_missing_credentials()
    if missing:
        print(f"   Missing critical credentials: {missing}")
    
    return validation['percentage'] >= 70  # At least 70% of credentials available

def test_email_integration():
    """Test the email integration with Mailchimp"""
    print("\n📧 Testing Email Integration...")
    
    cred_manager = CredentialManager()
    credentials = cred_manager.get_all_credentials()
    
    email_service = EmailService(credentials)
    connection_test = email_service.test_connection()
    
    if connection_test['success']:
        print(f"   ✅ Connected to {connection_test['service']}")
        if connection_test['service'] == 'mailchimp':
            print(f"   Server: {connection_test['server']}")
        return True
    else:
        print(f"   ❌ Connection failed: {connection_test['error']}")
        return False

def test_domain_management():
    """Test the domain management with GoDaddy"""
    print("\n🌐 Testing Domain Management...")
    
    cred_manager = CredentialManager()
    credentials = cred_manager.get_all_credentials()
    
    domain_manager = DomainManager(credentials)
    connection_test = domain_manager.test_connection()
    
    if connection_test['success']:
        print(f"   ✅ Connected to {connection_test['service']}")
        return True
    else:
        print(f"   ❌ Connection failed: {connection_test['error']}")
        return False

def test_deployment_system():
    """Test the autonomous deployment system"""
    print("\n🚀 Testing Autonomous Deployment System...")
    
    deployer = AutonomousDeployer()
    status = deployer.get_deployment_status()
    
    print(f"   Platforms available: {status['platforms_available']}")
    print(f"   GitHub ready: {'✅' if status['github_ready'] else '❌'}")
    print(f"   Domain management: {'✅' if status['domain_management'] else '❌'}")
    print(f"   Email services: {'✅' if status.get('email_services', False) else '❌'}")
    print(f"   Monitoring ready: {'✅' if status.get('monitoring_ready', False) else '❌'}")
    print(f"   Credentials loaded: {status['credentials_loaded']}/{status['total_credentials']}")
    
    return len(status['platforms_available']) > 0 and status['github_ready']

def main():
    """Run all tests for the autonomous deployment system"""
    print("🧪 Testing Autonomous Deployment System")
    print("=" * 60)
    
    tests = [
        ("Credential Manager", test_credential_manager),
        ("Email Integration", test_email_integration),
        ("Domain Management", test_domain_management),
        ("Deployment System", test_deployment_system)
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n[TEST] {name}")
        try:
            result = test_func()
            results.append((name, result))
            print(f"[RESULT] {'✅ PASS' if result else '❌ FAIL'}")
        except Exception as e:
            print(f"[ERROR] Test failed with exception: {str(e)}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {name}: {status}")
        if result:
            passed += 1
    
    success_rate = (passed / len(results)) * 100
    print(f"\n🎯 Overall Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 75:
        print("\n🎉 The autonomous deployment system is ready for production use!")
        return True
    else:
        print("\n⚠️ The autonomous deployment system needs additional configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
