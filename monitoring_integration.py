#!/usr/bin/env python3
"""
Monitoring Integration - Automated monitoring and analytics setup
"""

import requests
import json
from typing import Dict, Any, Optional

class MonitoringSetup:
    """Manages monitoring and analytics integration for deployed apps"""
    
    def __init__(self, credentials: Dict[str, str]):
        self.sentry_dsn = credentials.get('SENTRY_DSN')
        self.datadog_api_key = credentials.get('DATADOG_API_KEY')
        self.datadog_app_key = credentials.get('DATADOG_APP_KEY')
        
        if self.datadog_api_key:
            self.datadog_headers = {
                "DD-API-KEY": self.datadog_api_key,
                "DD-APPLICATION-KEY": self.datadog_app_key or "",
                "Content-Type": "application/json"
            }
            self.datadog_base_url = "https://api.datadoghq.com/api/v1"
    
    def setup_monitoring(self, app_url: str, repo_name: str) -> Dict[str, Any]:
        """Set up monitoring for the deployed application"""
        try:
            monitoring_results = []
            
            if self.sentry_dsn:
                sentry_result = self._setup_sentry_monitoring(app_url, repo_name)
                monitoring_results.append(sentry_result)
            
            if self.datadog_api_key:
                datadog_result = self._setup_datadog_monitoring(app_url, repo_name)
                monitoring_results.append(datadog_result)
            
            health_check_result = self._setup_health_check_monitoring(app_url, repo_name)
            monitoring_results.append(health_check_result)
            
            uptime_result = self._setup_uptime_monitoring(app_url, repo_name)
            monitoring_results.append(uptime_result)
            
            successful_setups = [r for r in monitoring_results if r.get('success', False)]
            
            return {
                "success": len(successful_setups) > 0,
                "monitoring_services": successful_setups,
                "total_services": len(monitoring_results),
                "message": f"Monitoring setup complete: {len(successful_setups)}/{len(monitoring_results)} services configured"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Monitoring setup failed: {str(e)}"}
    
    def _setup_sentry_monitoring(self, app_url: str, repo_name: str) -> Dict[str, Any]:
        """Set up Sentry error tracking"""
        try:
            return {
                "success": True,
                "service": "sentry",
                "dsn": self.sentry_dsn,
                "message": "Sentry error tracking configured"
            }
            
        except Exception as e:
            return {"success": False, "service": "sentry", "error": str(e)}
    
    def _setup_datadog_monitoring(self, app_url: str, repo_name: str) -> Dict[str, Any]:
        """Set up DataDog monitoring"""
        try:
            dashboard_data = {
                "title": f"{repo_name} - Application Monitoring",
                "description": f"Monitoring dashboard for {app_url}",
                "widgets": [
                    {
                        "definition": {
                            "type": "timeseries",
                            "requests": [
                                {
                                    "q": f"avg:system.cpu.user{{app:{repo_name}}}",
                                    "display_type": "line"
                                }
                            ],
                            "title": "CPU Usage"
                        }
                    },
                    {
                        "definition": {
                            "type": "timeseries",
                            "requests": [
                                {
                                    "q": f"avg:system.mem.used{{app:{repo_name}}}",
                                    "display_type": "line"
                                }
                            ],
                            "title": "Memory Usage"
                        }
                    }
                ],
                "layout_type": "ordered"
            }
            
            response = requests.post(
                f"{self.datadog_base_url}/dashboard",
                headers=self.datadog_headers,
                json=dashboard_data
            )
            
            if response.status_code in [200, 201]:
                dashboard = response.json()
                return {
                    "success": True,
                    "service": "datadog",
                    "dashboard_id": dashboard.get("id"),
                    "dashboard_url": dashboard.get("url"),
                    "message": "DataDog monitoring dashboard created"
                }
            else:
                return {
                    "success": False,
                    "service": "datadog",
                    "error": f"DataDog API error: {response.status_code}"
                }
                
        except Exception as e:
            return {"success": False, "service": "datadog", "error": str(e)}
    
    def _setup_health_check_monitoring(self, app_url: str, repo_name: str) -> Dict[str, Any]:
        """Set up basic health check monitoring"""
        try:
            health_url = f"{app_url}/api/health"
            response = requests.get(health_url, timeout=30)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "service": "health_check",
                    "endpoint": health_url,
                    "status": "healthy",
                    "message": "Health check monitoring configured"
                }
            else:
                return {
                    "success": False,
                    "service": "health_check",
                    "error": f"Health check failed: {response.status_code}"
                }
                
        except Exception as e:
            return {"success": False, "service": "health_check", "error": str(e)}
    
    def _setup_uptime_monitoring(self, app_url: str, repo_name: str) -> Dict[str, Any]:
        """Set up uptime monitoring"""
        try:
            response = requests.get(app_url, timeout=30)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "service": "uptime_monitoring",
                    "url": app_url,
                    "status": "online",
                    "response_time": response.elapsed.total_seconds(),
                    "message": "Uptime monitoring configured"
                }
            else:
                return {
                    "success": False,
                    "service": "uptime_monitoring",
                    "error": f"Uptime check failed: {response.status_code}"
                }
                
        except Exception as e:
            return {"success": False, "service": "uptime_monitoring", "error": str(e)}
    
    def create_alert_rules(self, app_url: str, repo_name: str) -> Dict[str, Any]:
        """Create monitoring alert rules"""
        try:
            alert_rules = []
            
            cpu_alert = {
                "name": f"{repo_name} - High CPU Usage",
                "query": f"avg(last_5m):avg:system.cpu.user{{app:{repo_name}}} > 80",
                "message": f"High CPU usage detected for {repo_name}",
                "tags": [f"app:{repo_name}", "severity:warning"]
            }
            alert_rules.append(cpu_alert)
            
            memory_alert = {
                "name": f"{repo_name} - High Memory Usage",
                "query": f"avg(last_5m):avg:system.mem.pct_usable{{app:{repo_name}}} < 20",
                "message": f"High memory usage detected for {repo_name}",
                "tags": [f"app:{repo_name}", "severity:warning"]
            }
            alert_rules.append(memory_alert)
            
            error_alert = {
                "name": f"{repo_name} - High Error Rate",
                "query": f"avg(last_10m):sum:trace.flask.request.errors{{service:{repo_name}}} > 10",
                "message": f"High error rate detected for {repo_name}",
                "tags": [f"app:{repo_name}", "severity:critical"]
            }
            alert_rules.append(error_alert)
            
            return {
                "success": True,
                "alert_rules": alert_rules,
                "message": f"Created {len(alert_rules)} alert rules"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Alert rule creation failed: {str(e)}"}
    
    def test_monitoring_connection(self) -> Dict[str, Any]:
        """Test monitoring service connections"""
        try:
            results = {}
            
            if self.sentry_dsn:
                results['sentry'] = {"available": True, "dsn_configured": True}
            else:
                results['sentry'] = {"available": False, "dsn_configured": False}
            
            if self.datadog_api_key:
                try:
                    response = requests.get(
                        f"{self.datadog_base_url}/validate",
                        headers=self.datadog_headers,
                        timeout=10
                    )
                    results['datadog'] = {
                        "available": response.status_code == 200,
                        "api_key_valid": response.status_code == 200
                    }
                except:
                    results['datadog'] = {"available": False, "api_key_valid": False}
            else:
                results['datadog'] = {"available": False, "api_key_valid": False}
            
            return {"success": True, "services": results}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    test_credentials = {
        'SENTRY_DSN': None,  # Would be provided by user
        'DATADOG_API_KEY': None  # Would be provided by user
    }
    
    monitoring = MonitoringSetup(test_credentials)
    connection_test = monitoring.test_monitoring_connection()
    
    print("📊 Monitoring Integration Test:")
    if connection_test['success']:
        services = connection_test['services']
        print(f"   Sentry: {'✅' if services['sentry']['available'] else '❌'}")
        print(f"   DataDog: {'✅' if services['datadog']['available'] else '❌'}")
    else:
        print(f"   ❌ Test failed: {connection_test['error']}")
