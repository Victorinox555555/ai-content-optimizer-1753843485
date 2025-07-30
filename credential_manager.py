#!/usr/bin/env python3
"""
Credential Manager - Secure handling of API keys and secrets
"""

import os
from typing import Dict, Optional, Any, List
from dotenv import load_dotenv

class CredentialManager:
    """Manages API credentials for autonomous deployment system"""
    
    def __init__(self):
        """Initialize with provided API credentials"""
        # Load environment variables from QWEN-GPT-AGI
        load_dotenv('/home/ubuntu/QWEN-GPT-AGI/.env')
        load_dotenv('/home/ubuntu/QWEN-GPT-AGI/env.txt')
        load_dotenv()
        
        self.credentials = {
            'RAILWAY_TOKEN': '2e8e81e5-cb08-4ae9-8fe8-4fa94e942a62',
            'VERCEL_TOKEN': 'ZEo01Ou1koSSDWyFw0w9LGjX',
            'RENDER_API_KEY': 'rnd_gBzxTKBbvKl6VxHFnexzTS0i9jHZ',
            
            'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
            'GITHUB_APP_ID': '1693043',
            'GITHUB_PRIVATE_KEY': 'SHA256:zUg3vVtYlXT6ENnhhVKvBu84WSYKWXgcvFWc9JE86uI=',
            
            'GODADDY_API_KEY': 'h2K7cZMm5MPB_6Daj9vMhKLqpx3c7ijGDgM',
            'GODADDY_SECRET': 'HqmPSzSHSgbboFYuWJK3NU',
            
            'SENDGRID_API_KEY': None,
            'MAILGUN_API_KEY': None,
            'MAILCHIMP_API_KEY': '4f89ab137b38a9d6272e4512daeb1b60-us19',
            'MAILCHIMP_SERVER': 'us19',
            
            'SENTRY_DSN': None,
            'DATADOG_API_KEY': None,
            
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'STRIPE_SECRET_KEY': os.getenv('STRIPE_SECRET_KEY'),
            'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
            'TELEGRAM_USER_ID': os.getenv('TELEGRAM_USER_ID'),
            'PRICE_ID': os.getenv('PRICE_ID', 'price_1RcdcyEfbTvI2h4o4PVLTykg')
        }
    
    def get_credential(self, key: str) -> Optional[str]:
        """Get a specific credential by key"""
        return self.credentials.get(key)
    
    def get_all_credentials(self) -> Dict[str, Any]:
        """Get all credentials"""
        return self.credentials.copy()
    
    def has_credential(self, key: str) -> bool:
        """Check if a credential exists and is not None"""
        return self.credentials.get(key) is not None
    
    def get_platform_credentials(self) -> Dict[str, str]:
        """Get deployment platform credentials"""
        return {
            'RAILWAY_TOKEN': self.credentials.get('RAILWAY_TOKEN'),
            'VERCEL_TOKEN': self.credentials.get('VERCEL_TOKEN'),
            'RENDER_API_KEY': self.credentials.get('RENDER_API_KEY')
        }
    
    def get_github_credentials(self) -> Dict[str, str]:
        """Get GitHub automation credentials"""
        return {
            'GITHUB_TOKEN': self.credentials.get('GITHUB_TOKEN'),
            'GITHUB_APP_ID': self.credentials.get('GITHUB_APP_ID'),
            'GITHUB_PRIVATE_KEY': self.credentials.get('GITHUB_PRIVATE_KEY')
        }
    
    def get_domain_credentials(self) -> Dict[str, str]:
        """Get domain management credentials"""
        return {
            'GODADDY_API_KEY': self.credentials.get('GODADDY_API_KEY'),
            'GODADDY_SECRET': self.credentials.get('GODADDY_SECRET')
        }
    
    def get_email_credentials(self) -> Dict[str, str]:
        """Get email service credentials"""
        return {
            'SENDGRID_API_KEY': self.credentials.get('SENDGRID_API_KEY'),
            'MAILGUN_API_KEY': self.credentials.get('MAILGUN_API_KEY'),
            'MAILCHIMP_API_KEY': self.credentials.get('MAILCHIMP_API_KEY'),
            'MAILCHIMP_SERVER': self.credentials.get('MAILCHIMP_SERVER')
        }
    
    def validate_credentials(self) -> Dict[str, Any]:
        """Validate which credentials are available"""
        validation = {
            'platform_deployment': {
                'railway': self.has_credential('RAILWAY_TOKEN'),
                'vercel': self.has_credential('VERCEL_TOKEN'),
                'render': self.has_credential('RENDER_API_KEY')
            },
            'github_automation': {
                'token': self.has_credential('GITHUB_TOKEN'),
                'app_id': self.has_credential('GITHUB_APP_ID'),
                'private_key': self.has_credential('GITHUB_PRIVATE_KEY')
            },
            'domain_management': {
                'godaddy': self.has_credential('GODADDY_API_KEY') and self.has_credential('GODADDY_SECRET')
            },
            'email_services': {
                'sendgrid': self.has_credential('SENDGRID_API_KEY'),
                'mailgun': self.has_credential('MAILGUN_API_KEY'),
                'mailchimp': self.has_credential('MAILCHIMP_API_KEY')
            },
            'core_services': {
                'openai': self.has_credential('OPENAI_API_KEY'),
                'stripe': self.has_credential('STRIPE_SECRET_KEY'),
                'telegram': self.has_credential('TELEGRAM_BOT_TOKEN')
            }
        }
        
        total_checks = 0
        passed_checks = 0
        
        for category, checks in validation.items():
            for check, status in checks.items():
                total_checks += 1
                if status:
                    passed_checks += 1
        
        validation['readiness_score'] = f"{passed_checks}/{total_checks}"
        validation['percentage'] = round((passed_checks / total_checks) * 100, 1)
        
        return validation
    
    def get_missing_credentials(self) -> List[str]:
        """Get list of missing critical credentials"""
        missing = []
        
        critical_credentials = [
            'RAILWAY_TOKEN',
            'VERCEL_TOKEN', 
            'GITHUB_TOKEN',
            'GODADDY_API_KEY',
            'GODADDY_SECRET',
            'OPENAI_API_KEY',
            'STRIPE_SECRET_KEY'
        ]
        
        for cred in critical_credentials:
            if not self.has_credential(cred):
                missing.append(cred)
        
        return missing
    
    def export_for_deployment(self, platform: str) -> Dict[str, str]:
        """Export environment variables for deployment"""
        base_env = {
            'OPENAI_API_KEY': self.get_credential('OPENAI_API_KEY') or '',
            'STRIPE_SECRET_KEY': self.get_credential('STRIPE_SECRET_KEY') or '',
            'SECRET_KEY': 'ai-content-optimizer-secret-key-2025',
            'FLASK_ENV': 'production',
            'PRICE_ID': self.get_credential('PRICE_ID') or 'price_1RcdcyEfbTvI2h4o4PVLTykg'
        }
        
        if platform == 'railway':
            base_env.update({
                'PORT': '5000',
                'RAILWAY_ENVIRONMENT': 'production'
            })
        elif platform == 'vercel':
            base_env.update({
                'VERCEL_ENV': 'production'
            })
        elif platform == 'render':
            base_env.update({
                'RENDER_ENV': 'production'
            })
        
        return {k: v for k, v in base_env.items() if v is not None}

if __name__ == "__main__":
    creds = CredentialManager()
    validation = creds.validate_credentials()
    
    print("🔑 Credential Manager Status:")
    print(f"   Readiness: {validation['readiness_score']} ({validation['percentage']}%)")
    print(f"   Platform Deployment: {validation['platform_deployment']}")
    print(f"   GitHub Automation: {validation['github_automation']}")
    print(f"   Domain Management: {validation['domain_management']}")
    print(f"   Email Services: {validation['email_services']}")
    print(f"   Core Services: {validation['core_services']}")
    
    missing = creds.get_missing_credentials()
    if missing:
        print(f"   Missing: {missing}")
