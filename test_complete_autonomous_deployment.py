#!/usr/bin/env python3
"""
Test complete autonomous deployment system end-to-end
"""

import sys
import os
import time
sys.path.append('/tmp/test_skill_output')

from autonomous_deployer import AutonomousDeployer
from credential_manager import CredentialManager

def test_complete_deployment():
    """Test complete autonomous deployment to Railway"""
    print("🚀 Testing Complete Autonomous Deployment...")
    
    deployer = AutonomousDeployer()
    
    print("\n📦 Deploying AI Content Optimizer to Railway...")
    
    deployment_result = deployer.deploy_mvp(
        mvp_path="/tmp/test_skill_output",
        platform="railway"
    )
    
    if deployment_result['success']:
        print(f"   ✅ Deployment successful!")
        print(f"   Repository: {deployment_result.get('repo_url', 'N/A')}")
        print(f"   Deployment URL: {deployment_result.get('deployment_url', 'N/A')}")
        print(f"   Status: {deployment_result.get('status', 'N/A')}")
        return True, deployment_result
    else:
        print(f"   ❌ Deployment failed: {deployment_result.get('error', 'Unknown error')}")
        return False, deployment_result

def test_render_deployment():
    """Test deployment to Render as backup"""
    print("\n🎨 Testing Render Deployment...")
    
    deployer = AutonomousDeployer()
    
    deployment_result = deployer.deploy_mvp(
        mvp_path="/tmp/test_skill_output",
        platform="render"
    )
    
    if deployment_result['success']:
        print(f"   ✅ Render deployment successful!")
        print(f"   Deployment URL: {deployment_result.get('deployment_url', 'N/A')}")
        return True, deployment_result
    else:
        print(f"   ❌ Render deployment failed: {deployment_result.get('error', 'Unknown error')}")
        return False, deployment_result

def main():
    """Run complete autonomous deployment test"""
    print("🧪 Testing Complete Autonomous Deployment System")
    print("=" * 60)
    
    railway_success, railway_result = test_complete_deployment()
    
    if railway_success:
        print(f"\n🎉 Autonomous deployment system is fully functional!")
        print(f"   Platform: Railway")
        print(f"   Repository: {railway_result.get('repo_url', 'N/A')}")
        print(f"   Live URL: {railway_result.get('deployment_url', 'N/A')}")
        return True
    
    print(f"\n⚠️ Railway deployment failed, trying Render...")
    render_success, render_result = test_render_deployment()
    
    if render_success:
        print(f"\n🎉 Autonomous deployment system is functional with Render!")
        print(f"   Platform: Render")
        print(f"   Live URL: {render_result.get('deployment_url', 'N/A')}")
        return True
    
    print(f"\n❌ Both Railway and Render deployments failed")
    print(f"   Railway error: {railway_result.get('error', 'Unknown')}")
    print(f"   Render error: {render_result.get('error', 'Unknown')}")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
