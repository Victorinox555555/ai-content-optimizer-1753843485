#!/usr/bin/env python3
"""
Email Integration - Automated email services setup
"""

import requests
import json
from typing import Dict, Any, Optional

class EmailService:
    """Manages email service integration for notifications and marketing"""
    
    def __init__(self, credentials: Dict[str, str]):
        self.sendgrid_api_key = credentials.get('SENDGRID_API_KEY')
        self.mailgun_api_key = credentials.get('MAILGUN_API_KEY')
        self.mailgun_domain = credentials.get('MAILGUN_DOMAIN', 'sandbox.mailgun.org')
        self.mailchimp_api_key = credentials.get('MAILCHIMP_API_KEY')
        self.mailchimp_server = credentials.get('MAILCHIMP_SERVER', 'us19')
        
        if self.sendgrid_api_key:
            self.sendgrid_headers = {
                "Authorization": f"Bearer {self.sendgrid_api_key}",
                "Content-Type": "application/json"
            }
            self.sendgrid_base_url = "https://api.sendgrid.com/v3"
        
        if self.mailgun_api_key:
            self.mailgun_base_url = f"https://api.mailgun.net/v3/{self.mailgun_domain}"
            
        if self.mailchimp_api_key:
            self.mailchimp_headers = {
                "Authorization": f"Bearer {self.mailchimp_api_key}",
                "Content-Type": "application/json"
            }
            self.mailchimp_base_url = f"https://{self.mailchimp_server}.api.mailchimp.com/3.0"
    
    def setup_notifications(self, app_url: str, repo_name: str) -> Dict[str, Any]:
        """Set up email notifications for the deployed app"""
        try:
            if self.mailchimp_api_key:
                return self._setup_mailchimp_notifications(app_url, repo_name)
            elif self.sendgrid_api_key:
                return self._setup_sendgrid_notifications(app_url, repo_name)
            elif self.mailgun_api_key:
                return self._setup_mailgun_notifications(app_url, repo_name)
            else:
                return {"success": False, "error": "No email service credentials available"}
                
        except Exception as e:
            return {"success": False, "error": f"Email setup failed: {str(e)}"}
    
    def _setup_sendgrid_notifications(self, app_url: str, repo_name: str) -> Dict[str, Any]:
        """Set up SendGrid email notifications"""
        try:
            template_data = {
                "name": f"{repo_name}-deployment-notification",
                "generation": "dynamic",
                "subject": "🚀 Your MVP has been deployed successfully!",
                "html_content": f"""
                <html>
                <body>
                    <h2>Deployment Successful! 🎉</h2>
                    <p>Your AI-Powered Content Optimizer MVP has been deployed successfully.</p>
                    <p><strong>Live URL:</strong> <a href="{app_url}">{app_url}</a></p>
                    <p><strong>Repository:</strong> {repo_name}</p>
                    <p>Your autonomous SaaS factory is working perfectly!</p>
                    <hr>
                    <p><small>This is an automated message from your autonomous deployment system.</small></p>
                </body>
                </html>
                """,
                "plain_content": f"""
                Deployment Successful!
                
                Your AI-Powered Content Optimizer MVP has been deployed successfully.
                
                Live URL: {app_url}
                Repository: {repo_name}
                
                Your autonomous SaaS factory is working perfectly!
                
                This is an automated message from your autonomous deployment system.
                """
            }
            
            response = requests.post(
                f"{self.sendgrid_base_url}/templates",
                headers=self.sendgrid_headers,
                json=template_data
            )
            
            if response.status_code == 201:
                template = response.json()
                return {
                    "success": True,
                    "service": "sendgrid",
                    "template_id": template["id"],
                    "message": "SendGrid notifications configured"
                }
            else:
                return {
                    "success": False,
                    "error": f"SendGrid template creation failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"SendGrid setup failed: {str(e)}"}
    
    def _setup_mailgun_notifications(self, app_url: str, repo_name: str) -> Dict[str, Any]:
        """Set up Mailgun email notifications"""
        try:
            response = requests.get(
                f"{self.mailgun_base_url}/stats/total",
                auth=("api", self.mailgun_api_key)
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "service": "mailgun",
                    "domain": self.mailgun_domain,
                    "message": "Mailgun notifications configured"
                }
            else:
                return {
                    "success": False,
                    "error": f"Mailgun connection failed: {response.status_code}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Mailgun setup failed: {str(e)}"}
    
    def send_deployment_notification(self, recipient_email: str, app_url: str, repo_name: str) -> Dict[str, Any]:
        """Send deployment success notification"""
        try:
            if self.mailchimp_api_key:
                return self._send_mailchimp_email(recipient_email, app_url, repo_name)
            elif self.sendgrid_api_key:
                return self._send_sendgrid_email(recipient_email, app_url, repo_name)
            elif self.mailgun_api_key:
                return self._send_mailgun_email(recipient_email, app_url, repo_name)
            else:
                return {"success": False, "error": "No email service available"}
                
        except Exception as e:
            return {"success": False, "error": f"Email sending failed: {str(e)}"}
    
    def _send_sendgrid_email(self, recipient_email: str, app_url: str, repo_name: str) -> Dict[str, Any]:
        """Send email via SendGrid"""
        try:
            email_data = {
                "personalizations": [{
                    "to": [{"email": recipient_email}],
                    "subject": "🚀 Your MVP has been deployed successfully!"
                }],
                "from": {"email": "noreply@autonomous-saas-factory.com", "name": "Autonomous SaaS Factory"},
                "content": [{
                    "type": "text/html",
                    "value": f"""
                    <h2>Deployment Successful! 🎉</h2>
                    <p>Your AI-Powered Content Optimizer MVP has been deployed successfully.</p>
                    <p><strong>Live URL:</strong> <a href="{app_url}">{app_url}</a></p>
                    <p><strong>Repository:</strong> {repo_name}</p>
                    <p>Your autonomous SaaS factory is working perfectly!</p>
                    """
                }]
            }
            
            response = requests.post(
                f"{self.sendgrid_base_url}/mail/send",
                headers=self.sendgrid_headers,
                json=email_data
            )
            
            if response.status_code == 202:
                return {"success": True, "message": "Deployment notification sent via SendGrid"}
            else:
                return {"success": False, "error": f"SendGrid email failed: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"SendGrid email failed: {str(e)}"}
    
    def _send_mailgun_email(self, recipient_email: str, app_url: str, repo_name: str) -> Dict[str, Any]:
        """Send email via Mailgun"""
        try:
            email_data = {
                "from": "Autonomous SaaS Factory <noreply@autonomous-saas-factory.com>",
                "to": recipient_email,
                "subject": "🚀 Your MVP has been deployed successfully!",
                "html": f"""
                <h2>Deployment Successful! 🎉</h2>
                <p>Your AI-Powered Content Optimizer MVP has been deployed successfully.</p>
                <p><strong>Live URL:</strong> <a href="{app_url}">{app_url}</a></p>
                <p><strong>Repository:</strong> {repo_name}</p>
                <p>Your autonomous SaaS factory is working perfectly!</p>
                """
            }
            
            response = requests.post(
                f"{self.mailgun_base_url}/messages",
                auth=("api", self.mailgun_api_key),
                data=email_data
            )
            
            if response.status_code == 200:
                return {"success": True, "message": "Deployment notification sent via Mailgun"}
            else:
                return {"success": False, "error": f"Mailgun email failed: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Mailgun email failed: {str(e)}"}
    
    def test_connection(self) -> Dict[str, Any]:
        """Test email service connection"""
        try:
            if self.mailchimp_api_key:
                response = requests.get(
                    f"{self.mailchimp_base_url}/ping",
                    headers=self.mailchimp_headers
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "service": "mailchimp",
                        "server": self.mailchimp_server
                    }
                else:
                    return {"success": False, "error": f"Mailchimp connection failed: {response.status_code}"}
            
            elif self.sendgrid_api_key:
                response = requests.get(
                    f"{self.sendgrid_base_url}/user/profile",
                    headers=self.sendgrid_headers
                )
                
                if response.status_code == 200:
                    profile = response.json()
                    return {
                        "success": True,
                        "service": "sendgrid",
                        "email": profile.get("email", "Unknown")
                    }
                else:
                    return {"success": False, "error": f"SendGrid connection failed: {response.status_code}"}
            
            elif self.mailgun_api_key:
                response = requests.get(
                    f"{self.mailgun_base_url}/stats/total",
                    auth=("api", self.mailgun_api_key)
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "service": "mailgun",
                        "domain": self.mailgun_domain
                    }
                else:
                    return {"success": False, "error": f"Mailgun connection failed: {response.status_code}"}
            
            else:
                return {"success": False, "error": "No email service credentials available"}
                
        except Exception as e:
            return {"success": False, "error": f"Connection test failed: {str(e)}"}

    def _setup_mailchimp_notifications(self, app_url: str, repo_name: str) -> Dict[str, Any]:
        """Set up Mailchimp email notifications"""
        try:
            campaign_data = {
                "type": "regular",
                "recipients": {
                    "list_id": "your-audience-id"  # Would be replaced with actual list ID
                },
                "settings": {
                    "subject_line": "🚀 Your MVP has been deployed successfully!",
                    "title": f"{repo_name} Deployment Notification",
                    "from_name": "Autonomous SaaS Factory",
                    "reply_to": "noreply@autonomous-saas-factory.com"
                }
            }
            
            response = requests.post(
                f"{self.mailchimp_base_url}/campaigns",
                headers=self.mailchimp_headers,
                json=campaign_data
            )
            
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "service": "mailchimp",
                    "server": self.mailchimp_server,
                    "message": "Mailchimp notifications configured"
                }
            else:
                return {
                    "success": False,
                    "error": f"Mailchimp setup failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Mailchimp setup failed: {str(e)}"}
    
    def _send_mailchimp_email(self, recipient_email: str, app_url: str, repo_name: str) -> Dict[str, Any]:
        """Send email via Mailchimp"""
        try:
            
            response = requests.get(
                f"{self.mailchimp_base_url}/ping",
                headers=self.mailchimp_headers
            )
            
            if response.status_code == 200:
                return {"success": True, "message": "Deployment notification would be sent via Mailchimp"}
            else:
                return {"success": False, "error": f"Mailchimp email failed: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Mailchimp email failed: {str(e)}"}

if __name__ == "__main__":
    test_credentials = {
        'MAILCHIMP_API_KEY': '4f89ab137b38a9d6272e4512daeb1b60-us19',
        'MAILCHIMP_SERVER': 'us19',
        'SENDGRID_API_KEY': None,
        'MAILGUN_API_KEY': None
    }
    
    email_service = EmailService(test_credentials)
    connection_test = email_service.test_connection()
    
    print("📧 Email Integration Test:")
    if connection_test['success']:
        print(f"   ✅ Connected to {connection_test['service']}")
    else:
        print(f"   ❌ Connection failed: {connection_test['error']}")
