#!/usr/bin/env python3
"""
Test GitHub automation with the provided private key
"""

import sys
import os
import time
sys.path.append('/tmp/test_skill_output')

from github_automation import GitHubAutomation
from credential_manager import CredentialManager

def test_github_authentication():
    """Test GitHub token authentication"""
    print("🔑 Testing GitHub Token Authentication...")
    
    cred_manager = CredentialManager()
    github_token = cred_manager.get_credential('GITHUB_TOKEN')
    
    if not github_token:
        print("   ❌ GitHub token not available")
        return False
    
    github_automation = GitHubAutomation(github_token)
    
    connection_test = github_automation.test_connection()
    
    if connection_test['success']:
        print(f"   ✅ GitHub token authentication successful")
        print(f"   Username: {connection_test['username']}")
        print(f"   Rate limit remaining: {connection_test['api_rate_limit']}")
        return True
    else:
        print(f"   ❌ GitHub token authentication failed: {connection_test['error']}")
        return False

def test_repository_creation():
    """Test creating a test repository"""
    print("\n📁 Testing Repository Creation...")
    
    cred_manager = CredentialManager()
    github_token = cred_manager.get_credential('GITHUB_TOKEN')
    
    if not github_token:
        print("   ❌ GitHub token not available")
        return False, None
    
    github_automation = GitHubAutomation(github_token)
    
    repo_name = f"test-autonomous-deployment-{int(time.time())}"
    repo_result = github_automation.create_repository(
        name=repo_name,
        description="Test repository for autonomous deployment system",
        private=True
    )
    
    if repo_result['success']:
        print(f"   ✅ Repository created successfully: {repo_result['repo_url']}")
        return True, repo_result['repo_url']
    else:
        print(f"   ❌ Repository creation failed: {repo_result['error']}")
        return False, None

def main():
    """Run GitHub automation tests"""
    print("🧪 Testing GitHub Automation with Private Key")
    print("=" * 60)
    
    auth_success = test_github_authentication()
    
    if not auth_success:
        print("\n❌ GitHub authentication failed - cannot proceed with repository tests")
        return False
    
    repo_success, repo_url = test_repository_creation()
    
    if repo_success:
        print(f"\n🎉 GitHub automation is fully functional!")
        print(f"   Test repository: {repo_url}")
        return True
    else:
        print(f"\n❌ GitHub automation has issues with repository creation")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
