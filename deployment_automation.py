import requests
import os
import json
import time
from typing import Dict, Any, Optional

class RenderDeployment:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.render.com/v1"
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def create_service(self, repo_url: str, env_vars: Dict[str, str]) -> Dict[str, Any]:
        """Create a new web service on Render"""
        try:
            service_data = {
                "type": "web_service",
                "name": f"ai-content-optimizer-{int(time.time())}",
                "repo": repo_url,
                "branch": "main",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "gunicorn main:app",
                "envVars": [{"key": k, "value": v} for k, v in env_vars.items()],
                "plan": "free"
            }
            
            response = requests.post(
                f"{self.base_url}/services",
                headers=self.headers,
                json=service_data
            )
            
            if response.status_code == 201:
                service = response.json()
                return {
                    "success": True,
                    "service_id": service["service"]["id"],
                    "url": service["service"]["serviceDetails"]["url"],
                    "status": "deploying"
                }
            else:
                return {
                    "success": False,
                    "error": f"Render API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Render deployment failed: {str(e)}"}

class RailwayDeployment:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://backboard.railway.app/graphql"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def deploy_project(self, repo_url: str, env_vars: Dict[str, str]) -> Dict[str, Any]:
        """Deploy project to Railway using GraphQL API"""
        try:
            create_project_mutation = """
            mutation projectCreate($input: ProjectCreateInput!) {
                projectCreate(input: $input) {
                    id
                    name
                }
            }
            """
            
            project_name = f"ai-content-optimizer-{int(time.time())}"
            project_input = {
                "name": project_name,
                "description": "AI-Powered Content Optimizer MVP"
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={
                    "query": create_project_mutation,
                    "variables": {"input": project_input}
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if "errors" not in data and "data" in data:
                    project_id = data["data"]["projectCreate"]["id"]
                    
                    deploy_mutation = """
                    mutation serviceCreate($input: ServiceCreateInput!) {
                        serviceCreate(input: $input) {
                            id
                            name
                        }
                    }
                    """
                    
                    service_input = {
                        "projectId": project_id,
                        "source": {
                            "repo": repo_url,
                            "branch": "main"
                        },
                        "variables": env_vars
                    }
                    
                    deploy_response = requests.post(
                        self.base_url,
                        headers=self.headers,
                        json={
                            "query": deploy_mutation,
                            "variables": {"input": service_input}
                        }
                    )
                    
                    if deploy_response.status_code == 200:
                        deploy_data = deploy_response.json()
                        if "errors" not in deploy_data and "data" in deploy_data:
                            return {
                                "success": True,
                                "project_id": project_id,
                                "service_id": deploy_data["data"]["serviceCreate"]["id"],
                                "url": f"https://{project_name}.up.railway.app",
                                "status": "deploying"
                            }
                
                error_msg = data.get("errors", [{"message": "Unknown GraphQL error"}])[0]["message"]
                return {"success": False, "error": f"Railway GraphQL error: {error_msg}"}
            else:
                return {"success": False, "error": f"Railway API error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Railway deployment failed: {str(e)}"}

class VercelDeployment:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.vercel.com/v2"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def create_deployment(self, repo_url: str, env_vars: Dict[str, str]) -> Dict[str, Any]:
        """Create deployment on Vercel"""
        try:
            repo_parts = repo_url.replace("https://github.com/", "").split("/")
            repo_owner = repo_parts[0]
            repo_name = repo_parts[1].replace(".git", "")
            
            deployment_data = {
                "name": f"ai-content-optimizer-{int(time.time())}",
                "gitSource": {
                    "type": "github",
                    "repo": f"{repo_owner}/{repo_name}",
                    "ref": "main"
                },
                "env": [{"key": k, "value": v, "type": "encrypted"} for k, v in env_vars.items()],
                "buildCommand": "pip install -r requirements.txt",
                "framework": "other"
            }
            
            response = requests.post(
                f"{self.base_url}/deployments",
                headers=self.headers,
                json=deployment_data
            )
            
            if response.status_code in [200, 201]:
                deployment = response.json()
                return {
                    "success": True,
                    "deployment_id": deployment["id"],
                    "url": f"https://{deployment['url']}",
                    "status": "deploying"
                }
            else:
                return {
                    "success": False,
                    "error": f"Vercel API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Vercel deployment failed: {str(e)}"}
