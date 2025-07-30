#!/usr/bin/env python3
"""
Domain Management - Automated domain registration and DNS configuration
"""

import requests
import json
from typing import Dict, Any, Optional

class DomainManager:
    """Manages domain registration and DNS configuration"""
    
    def __init__(self, credentials: Dict[str, str]):
        self.godaddy_api_key = credentials.get('GODADDY_API_KEY')
        self.godaddy_secret = credentials.get('GODADDY_SECRET')
        
        if self.godaddy_api_key and self.godaddy_secret:
            self.godaddy_headers = {
                "Authorization": f"sso-key {self.godaddy_api_key}:{self.godaddy_secret}",
                "Content-Type": "application/json"
            }
            self.godaddy_base_url = "https://api.godaddy.com/v1"
    
    def setup_domain(self, domain: str, target_url: str) -> Dict[str, Any]:
        """Set up custom domain pointing to deployment"""
        try:
            if not self.godaddy_api_key:
                return {"success": False, "error": "GoDaddy credentials not available"}
            
            availability = self.check_domain_availability(domain)
            if not availability['success']:
                return availability
            
            if availability['available']:
                registration = self.register_domain(domain)
                if not registration['success']:
                    return registration
            
            dns_result = self.configure_dns(domain, target_url)
            return dns_result
            
        except Exception as e:
            return {"success": False, "error": f"Domain setup failed: {str(e)}"}
    
    def check_domain_availability(self, domain: str) -> Dict[str, Any]:
        """Check if domain is available for registration"""
        try:
            response = requests.get(
                f"{self.godaddy_base_url}/domains/available?domain={domain}",
                headers=self.godaddy_headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "available": data.get("available", False),
                    "price": data.get("price", 0),
                    "currency": data.get("currency", "USD")
                }
            else:
                return {
                    "success": False,
                    "error": f"Domain availability check failed: {response.status_code}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Availability check failed: {str(e)}"}
    
    def register_domain(self, domain: str) -> Dict[str, Any]:
        """Register a new domain"""
        try:
            registration_data = {
                "domain": domain,
                "period": 1,  # 1 year
                "nameServers": ["ns1.godaddy.com", "ns2.godaddy.com"],
                "renewAuto": True,
                "privacy": True,
                "consent": {
                    "agreementKeys": ["DNRA"],
                    "agreedBy": "auto-deployment-system",
                    "agreedAt": "2025-01-01T00:00:00Z"
                }
            }
            
            response = requests.post(
                f"{self.godaddy_base_url}/domains/purchase",
                headers=self.godaddy_headers,
                json=registration_data
            )
            
            if response.status_code in [200, 201]:
                return {"success": True, "message": "Domain registered successfully"}
            else:
                return {
                    "success": False,
                    "error": f"Domain registration failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Domain registration failed: {str(e)}"}
    
    def configure_dns(self, domain: str, target_url: str) -> Dict[str, Any]:
        """Configure DNS records for the domain"""
        try:
            target_host = target_url.replace("https://", "").replace("http://", "").split("/")[0]
            
            dns_records = [
                {
                    "type": "A",
                    "name": "@",
                    "data": target_host,
                    "ttl": 3600
                },
                {
                    "type": "CNAME",
                    "name": "www",
                    "data": domain,
                    "ttl": 3600
                }
            ]
            
            response = requests.put(
                f"{self.godaddy_base_url}/domains/{domain}/records",
                headers=self.godaddy_headers,
                json=dns_records
            )
            
            if response.status_code == 200:
                return {"success": True, "message": "DNS configured successfully"}
            else:
                return {
                    "success": False,
                    "error": f"DNS configuration failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"DNS configuration failed: {str(e)}"}
    
    def get_domain_info(self, domain: str) -> Dict[str, Any]:
        """Get information about a domain"""
        try:
            response = requests.get(
                f"{self.godaddy_base_url}/domains/{domain}",
                headers=self.godaddy_headers
            )
            
            if response.status_code == 200:
                return {"success": True, "domain_info": response.json()}
            else:
                return {
                    "success": False,
                    "error": f"Domain info retrieval failed: {response.status_code}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Domain info failed: {str(e)}"}
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to domain management API"""
        try:
            if not self.godaddy_api_key or not self.godaddy_secret:
                return {"success": False, "error": "GoDaddy credentials not available"}
            
            response = requests.get(
                f"{self.godaddy_base_url}/domains/tlds",
                headers=self.godaddy_headers,
                params={"limit": 5}  # Just get a few to verify connection
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "service": "godaddy",
                    "message": "GoDaddy API connection successful"
                }
            else:
                return {
                    "success": False,
                    "error": f"GoDaddy API connection failed: {response.status_code}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Connection test failed: {str(e)}"}

if __name__ == "__main__":
    test_credentials = {
        'GODADDY_API_KEY': 'h2K7cZMm5MPB_6Daj9vMhKLqpx3c7ijGDgM',
        'GODADDY_SECRET': 'HqmPSzSHSgbboFYuWJK3NU'
    }
    
    domain_manager = DomainManager(test_credentials)
    
    test_domain = "ai-content-optimizer-test.com"
    availability = domain_manager.check_domain_availability(test_domain)
    
    print("🌐 Domain Management Test:")
    if availability['success']:
        print(f"   Domain {test_domain}: {'Available' if availability['available'] else 'Not available'}")
        if availability['available']:
            print(f"   Price: ${availability['price']} {availability['currency']}")
    else:
        print(f"   ❌ Test failed: {availability['error']}")
