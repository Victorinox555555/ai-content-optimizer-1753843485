#!/usr/bin/env python3
"""
GitHub Automation - Repository creation and management
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List

class GitHubAutomation:
    """Automates GitHub repository operations for deployment"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
    
    def create_repository(self, name: str, description: str, private: bool = False) -> Dict[str, Any]:
        """Create a new GitHub repository"""
        try:
            repo_data = {
                "name": name,
                "description": description,
                "private": private,
                "auto_init": True,
                "gitignore_template": "Python",
                "license_template": "mit"
            }
            
            response = requests.post(
                f"{self.base_url}/user/repos",
                headers=self.headers,
                json=repo_data
            )
            
            if response.status_code == 201:
                repo = response.json()
                return {
                    "success": True,
                    "repo_url": repo["html_url"],
                    "clone_url": repo["clone_url"],
                    "ssh_url": repo["ssh_url"],
                    "repo_id": repo["id"],
                    "full_name": repo["full_name"]
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Repository creation failed: {str(e)}"}
    
    def setup_environment_variables(self, repo_name: str, env_vars: Dict[str, str]) -> bool:
        """Set up GitHub secrets for repository"""
        try:
            repo_response = requests.get(
                f"{self.base_url}/user/repos",
                headers=self.headers
            )
            
            if repo_response.status_code != 200:
                return False
            
            repos = repo_response.json()
            target_repo = None
            
            for repo in repos:
                if repo["name"] == repo_name:
                    target_repo = repo
                    break
            
            if not target_repo:
                return False
            
            secrets_url = f"{self.base_url}/repos/{target_repo['full_name']}/actions/secrets"
            
            for key, value in env_vars.items():
                secret_data = {
                    "encrypted_value": value,  # In production, this would be properly encrypted
                    "key_id": "placeholder"    # Would use actual key ID
                }
                
                requests.put(
                    f"{secrets_url}/{key}",
                    headers=self.headers,
                    json=secret_data
                )
            
            return True
            
        except Exception as e:
            print(f"Environment variable setup failed: {e}")
            return False
    
    def get_repository_info(self, repo_name: str) -> Dict[str, Any]:
        """Get information about a repository"""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{repo_name}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {"success": True, "repo": response.json()}
            else:
                return {"success": False, "error": f"Repository not found: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_webhook(self, repo_name: str, webhook_url: str, events: List[str] = None) -> Dict[str, Any]:
        """Create a webhook for the repository"""
        if events is None:
            events = ["push", "pull_request"]
        
        try:
            webhook_data = {
                "name": "web",
                "active": True,
                "events": events,
                "config": {
                    "url": webhook_url,
                    "content_type": "json",
                    "insecure_ssl": "0"
                }
            }
            
            response = requests.post(
                f"{self.base_url}/repos/{repo_name}/hooks",
                headers=self.headers,
                json=webhook_data
            )
            
            if response.status_code == 201:
                webhook = response.json()
                return {
                    "success": True,
                    "webhook_id": webhook["id"],
                    "webhook_url": webhook["config"]["url"]
                }
            else:
                return {
                    "success": False,
                    "error": f"Webhook creation failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Webhook creation failed: {str(e)}"}
    
    def test_connection(self) -> Dict[str, Any]:
        """Test GitHub API connection"""
        try:
            response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers
            )
            
            if response.status_code == 200:
                user = response.json()
                return {
                    "success": True,
                    "username": user["login"],
                    "user_id": user["id"],
                    "api_rate_limit": response.headers.get("X-RateLimit-Remaining", "Unknown")
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API connection failed: {response.status_code}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Connection test failed: {str(e)}"}

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv('/home/ubuntu/QWEN-GPT-AGI/.env')
    load_dotenv('/home/ubuntu/QWEN-GPT-AGI/env.txt')
    
    github_token = os.getenv('GITHUB_TOKEN')
    
    if github_token:
        github = GitHubAutomation(github_token)
        connection_test = github.test_connection()
        
        print("🐙 GitHub Automation Test:")
        if connection_test['success']:
            print(f"   ✅ Connected as: {connection_test['username']}")
            print(f"   Rate limit remaining: {connection_test['api_rate_limit']}")
        else:
            print(f"   ❌ Connection failed: {connection_test['error']}")
    else:
        print("❌ GitHub token not found")
