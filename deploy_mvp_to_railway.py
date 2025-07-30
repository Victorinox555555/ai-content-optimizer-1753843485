#!/usr/bin/env python3
"""
Deploy AI Content Optimizer MVP to Railway using autonomous deployment system
"""

import sys
import os
import time
sys.path.append('/tmp/test_skill_output')

from autonomous_deployer import AutonomousDeployer
from credential_manager import CredentialManager

def main():
    print("🚀 Deploying AI Content Optimizer MVP to Railway...")
    print("=" * 60)
    
    deployer = AutonomousDeployer()
    
    status = deployer.get_deployment_status()
    print(f"📊 Deployment System Status:")
    print(f"   Platforms: {status['platforms_available']}")
    print(f"   GitHub: {'✅' if status['github_ready'] else '❌'}")
    print(f"   Domain Management: {'✅' if status['domain_management'] else '❌'}")
    print(f"   Credentials: {status['credentials_loaded']}/{status['total_credentials']}")
    
    if 'railway' not in status['platforms_available']:
        print("❌ Railway platform not available. Missing RAILWAY_TOKEN.")
        return False
    
    print("\n🚂 Starting Railway deployment...")
    
    mvp_path = "/tmp/test_skill_output"
    
    deployment_result = deployer.deploy_mvp(
        mvp_path=mvp_path,
        platform='railway',
        custom_domain=None  # No custom domain for now
    )
    
    print("\n" + "=" * 60)
    print("📋 Deployment Log:")
    for log_entry in deployment_result.get('log', []):
        print(f"   {log_entry}")
    
    if deployment_result['success']:
        print("\n🎉 DEPLOYMENT SUCCESSFUL!")
        print(f"   Live URL: {deployment_result['app_url']}")
        print(f"   Repository: {deployment_result['repo_url']}")
        print(f"   Platform: {deployment_result['platform'].title()}")
        print(f"   Deployment ID: {deployment_result.get('deployment_id', 'N/A')}")
        
        print("\n🔍 Testing deployed application...")
        verification = deployment_result.get('verification', {})
        if verification.get('overall_status', False):
            print("   ✅ Application is responding correctly")
            print("   ✅ Health check passed")
            print("   ✅ Main page accessible")
        else:
            print("   ⚠️ Application verification had issues")
            if 'error' in verification:
                print(f"   Error: {verification['error']}")
        
        print(f"\n🌟 Your AI-Powered Content Optimizer is now live!")
        print(f"🔗 Access it at: {deployment_result['app_url']}")
        
        return True
    else:
        print(f"\n❌ DEPLOYMENT FAILED!")
        print(f"   Error: {deployment_result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
