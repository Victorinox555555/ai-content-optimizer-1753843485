#!/usr/bin/env python3
"""
Autonomous Deployer - Complete deployment orchestration system
"""

import os
import sys
import json
import time
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path

sys.path.append('/tmp/test_skill_output')

from deployment_automation import RenderDeployment, RailwayDeployment, VercelDeployment
from github_automation import GitHubAutomation
from credential_manager import CredentialManager
from domain_management import DomainManager
from email_integration import EmailService
from monitoring_integration import MonitoringSetup
from cicd_automation import CICDPipeline
from business_operations import BusinessOperations

class AutonomousDeployer:
    """Complete autonomous deployment system for SaaS MVPs"""
    
    def __init__(self, credentials: Optional[Dict[str, str]] = None):
        """Initialize with credentials from CredentialManager or provided dict"""
        if credentials:
            self.credentials = credentials
        else:
            cred_manager = CredentialManager()
            self.credentials = cred_manager.get_all_credentials()
        
        self.platforms = {}
        if self.credentials.get('RENDER_API_KEY'):
            self.platforms['render'] = RenderDeployment(self.credentials['RENDER_API_KEY'])
        if self.credentials.get('RAILWAY_TOKEN'):
            self.platforms['railway'] = RailwayDeployment(self.credentials['RAILWAY_TOKEN'])
        if self.credentials.get('VERCEL_TOKEN'):
            self.platforms['vercel'] = VercelDeployment(self.credentials['VERCEL_TOKEN'])
        
        self.github = GitHubAutomation(self.credentials.get('GITHUB_TOKEN'))
        self.domain_manager = DomainManager(self.credentials)
        self.email_service = EmailService(self.credentials)
        self.monitoring = MonitoringSetup(self.credentials)
        self.cicd = CICDPipeline(self.credentials)
        self.business_ops = BusinessOperations(self.credentials)
    
    def deploy_mvp(self, mvp_path: str, platform: str = 'railway', 
                   custom_domain: Optional[str] = None) -> Dict[str, Any]:
        """Complete autonomous deployment pipeline"""
        
        deployment_log = []
        
        try:
            deployment_log.append("🐙 Creating GitHub repository...")
            repo_name = f"ai-content-optimizer-{int(time.time())}"
            
            repo_result = self.github.create_repository(
                name=repo_name,
                description="AI-Powered Content Optimizer MVP - Autonomous SaaS Factory",
                private=False
            )
            
            if not repo_result['success']:
                return {
                    'success': False,
                    'error': f"GitHub repository creation failed: {repo_result['error']}",
                    'log': deployment_log
                }
            
            repo_url = repo_result['repo_url']
            clone_url = repo_result['clone_url']
            deployment_log.append(f"✅ Repository created: {repo_url}")
            
            deployment_log.append("📁 Pushing MVP files to repository...")
            push_result = self._push_mvp_files(mvp_path, clone_url)
            
            if not push_result['success']:
                return {
                    'success': False,
                    'error': f"File push failed: {push_result['error']}",
                    'log': deployment_log
                }
            
            deployment_log.append("✅ MVP files pushed successfully")
            
            deployment_log.append("🔐 Setting up environment variables...")
            env_vars = self._prepare_environment_variables()
            
            env_result = self.github.setup_environment_variables(repo_name, env_vars)
            if env_result:
                deployment_log.append("✅ Environment variables configured")
            else:
                deployment_log.append("⚠️ Environment variable setup had issues")
            
            deployment_log.append(f"🚀 Deploying to {platform.title()}...")
            
            if platform not in self.platforms:
                return {
                    'success': False,
                    'error': f"Platform {platform} not available. Available: {list(self.platforms.keys())}",
                    'log': deployment_log
                }
            
            deploy_result = self.platforms[platform].create_service(repo_url, env_vars) if platform == 'render' else \
                           self.platforms[platform].deploy_project(repo_url, env_vars) if platform == 'railway' else \
                           self.platforms[platform].create_deployment(repo_url, env_vars)
            
            if not deploy_result['success']:
                return {
                    'success': False,
                    'error': f"{platform.title()} deployment failed: {deploy_result['error']}",
                    'log': deployment_log
                }
            
            app_url = deploy_result['url']
            deployment_log.append(f"✅ Deployed successfully to: {app_url}")
            
            if custom_domain:
                deployment_log.append(f"🌐 Setting up custom domain: {custom_domain}")
                domain_result = self.domain_manager.setup_domain(custom_domain, app_url)
                if domain_result['success']:
                    deployment_log.append(f"✅ Custom domain configured: https://{custom_domain}")
                    app_url = f"https://{custom_domain}"
                else:
                    deployment_log.append(f"⚠️ Domain setup failed: {domain_result['error']}")
            
            deployment_log.append("📊 Setting up monitoring...")
            monitoring_result = self.monitoring.setup_monitoring(app_url, repo_name)
            if monitoring_result['success']:
                deployment_log.append("✅ Monitoring configured")
            else:
                deployment_log.append(f"⚠️ Monitoring setup failed: {monitoring_result['error']}")
            
            deployment_log.append("⚙️ Setting up CI/CD pipeline...")
            cicd_result = self.cicd.setup_pipeline(repo_name, platform)
            if cicd_result['success']:
                deployment_log.append("✅ CI/CD pipeline configured")
            else:
                deployment_log.append(f"⚠️ CI/CD setup failed: {cicd_result['error']}")
            
            deployment_log.append("📧 Setting up email services...")
            email_result = self.email_service.setup_notifications(app_url, repo_name)
            if email_result['success']:
                deployment_log.append("✅ Email services configured")
            else:
                deployment_log.append(f"⚠️ Email setup failed: {email_result['error']}")
            
            deployment_log.append("📋 Setting up business operations...")
            business_result = self.business_ops.setup_operations(app_url, repo_name)
            if business_result['success']:
                deployment_log.append("✅ Business operations configured")
            else:
                deployment_log.append(f"⚠️ Business operations setup failed: {business_result['error']}")
            
            deployment_log.append("🔍 Running final verification...")
            verification_result = self._verify_deployment(app_url)
            
            return {
                'success': True,
                'app_url': app_url,
                'repo_url': repo_url,
                'platform': platform,
                'deployment_id': deploy_result.get('service_id') or deploy_result.get('deployment_id'),
                'verification': verification_result,
                'log': deployment_log,
                'timestamp': time.time()
            }
            
        except Exception as e:
            deployment_log.append(f"❌ Deployment failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'log': deployment_log
            }
    
    def _prepare_environment_variables(self) -> Dict[str, str]:
        """Prepare environment variables for deployment"""
        return {
            'OPENAI_API_KEY': self.credentials.get('OPENAI_API_KEY', ''),
            'STRIPE_SECRET_KEY': self.credentials.get('STRIPE_SECRET_KEY', ''),
            'SECRET_KEY': 'ai-content-optimizer-secret-key-2025',
            'FLASK_ENV': 'production',
            'PRICE_ID': self.credentials.get('PRICE_ID', 'price_1RcdcyEfbTvI2h4o4PVLTykg'),
            'TELEGRAM_BOT_TOKEN': self.credentials.get('TELEGRAM_BOT_TOKEN', ''),
            'TELEGRAM_USER_ID': self.credentials.get('TELEGRAM_USER_ID', '')
        }
    
    def _push_mvp_files(self, mvp_path: str, clone_url: str) -> Dict[str, Any]:
        """Push MVP files to GitHub repository"""
        try:
            import shutil
            import glob
            
            temp_dir = f"/tmp/deploy_{int(time.time())}"
            os.makedirs(temp_dir, exist_ok=True)
            
            subprocess.run(['git', 'clone', clone_url, temp_dir], check=True, capture_output=True)
            
            source_items = glob.glob(os.path.join(mvp_path, '*'))
            
            for item in source_items:
                item_name = os.path.basename(item)
                dest_path = os.path.join(temp_dir, item_name)
                
                if os.path.isdir(item):
                    shutil.copytree(item, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest_path)
            
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                subprocess.run(['git', 'add', '.'], check=True)
                subprocess.run(['git', 'commit', '-m', 'Initial MVP deployment'], check=True)
                subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            finally:
                os.chdir(original_cwd)
            
            return {'success': True}
            
        except subprocess.CalledProcessError as e:
            return {'success': False, 'error': f"Git operation failed: {e}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _verify_deployment(self, app_url: str) -> Dict[str, Any]:
        """Verify deployment is working correctly"""
        try:
            import requests
            
            health_response = requests.get(f"{app_url}/api/health", timeout=30)
            health_ok = health_response.status_code == 200
            
            main_response = requests.get(app_url, timeout=30)
            main_ok = main_response.status_code == 200
            
            return {
                'health_check': health_ok,
                'main_page': main_ok,
                'overall_status': health_ok and main_ok
            }
            
        except Exception as e:
            return {
                'health_check': False,
                'main_page': False,
                'overall_status': False,
                'error': str(e)
            }
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get status of deployment automation capabilities"""
        return {
            'platforms_available': list(self.platforms.keys()),
            'github_ready': bool(self.credentials.get('GITHUB_TOKEN')),
            'domain_management': bool(self.credentials.get('GODADDY_API_KEY')),
            'email_services': bool(self.credentials.get('SENDGRID_API_KEY')),
            'monitoring_ready': bool(self.credentials.get('SENTRY_DSN')),
            'credentials_loaded': len([k for k, v in self.credentials.items() if v]),
            'total_credentials': len(self.credentials)
        }

if __name__ == "__main__":
    deployer = AutonomousDeployer()
    status = deployer.get_deployment_status()
    
    print("🚀 Autonomous Deployment System Status:")
    print(f"   Platforms: {status['platforms_available']}")
    print(f"   GitHub: {'✅' if status['github_ready'] else '❌'}")
    print(f"   Domain Management: {'✅' if status['domain_management'] else '❌'}")
    print(f"   Email Services: {'✅' if status['email_services'] else '❌'}")
    print(f"   Monitoring: {'✅' if status['monitoring_ready'] else '❌'}")
    print(f"   Credentials: {status['credentials_loaded']}/{status['total_credentials']}")
