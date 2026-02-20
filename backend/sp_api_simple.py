#!/usr/bin/env python3
"""
WallCharmers SP-API Simple Test - Try without AWS role first
"""

import requests
import json
import time
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sp_api_simple():
    """Test SP-API with just LWA token (no AWS role)"""
    import os
    
    # Load credentials from environment variables
    client_id = os.getenv('SP_API_CLIENT_ID')
    client_secret = os.getenv('SP_API_CLIENT_SECRET')
    refresh_token = os.getenv('SP_API_REFRESH_TOKEN')
    
    seller_id = os.getenv('SELLER_ID')
    marketplace_id = os.getenv('MARKETPLACE_ID', 'ATVPDKIKX0DER')
    
    if not all([client_id, client_secret, refresh_token, seller_id]):
        print("❌ Missing required environment variables!")
        print("Please set: SP_API_CLIENT_ID, SP_API_CLIENT_SECRET, SP_API_REFRESH_TOKEN, SELLER_ID")
        return
    
    print("🇺🇦 WallCharmers SP-API Simple Test")
    print("=" * 40)
    
    # Step 1: Get LWA token
    print("🔑 Getting LWA access token...")
    try:
        lwa_response = requests.post('https://api.amazon.com/auth/o2/token', data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': client_id,
            'client_secret': client_secret
        }, timeout=10)
        
        if lwa_response.status_code == 200:
            token_data = lwa_response.json()
            access_token = token_data['access_token']
            print("✅ LWA token obtained successfully")
        else:
            print(f"❌ LWA failed: {lwa_response.status_code} - {lwa_response.text}")
            return
            
    except Exception as e:
        print(f"❌ LWA error: {e}")
        return
    
    # Step 2: Try different SP-API endpoints to see what works
    base_url = 'https://sellingpartnerapi-na.amazon.com'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'x-amz-access-token': access_token,
        'Content-Type': 'application/json',
        'User-Agent': 'WallCharmers-ViktoryDashboard/3.0'
    }
    
    # Test different endpoints
    test_endpoints = [
        ('/sellers/v1/marketplaceParticipations', 'Marketplace Participations'),
        ('/orders/v0/orders?MarketplaceIds=ATVPDKIKX0DER&CreatedAfter=2024-02-01T00:00:00Z', 'Orders'),
        ('/fba/inventory/v1/summaries?details=true&granularityType=Marketplace&granularityId=ATVPDKIKX0DER&marketplaceIds=ATVPDKIKX0DER', 'Inventory')
    ]
    
    results = {}
    
    for endpoint, name in test_endpoints:
        print(f"🚀 Testing {name}...")
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, headers=headers, timeout=15)
            
            print(f"📊 {name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                results[name] = {'status': 'SUCCESS', 'data': data}
                print(f"✅ {name} - SUCCESS!")
            elif response.status_code == 403:
                error_data = response.json() if response.content else {}
                results[name] = {'status': 'AUTH_FAILED', 'error': error_data}
                print(f"❌ {name} - AUTH FAILED (needs AWS role)")
            else:
                results[name] = {'status': 'ERROR', 'code': response.status_code, 'text': response.text}
                print(f"❌ {name} - Error {response.status_code}")
                
        except Exception as e:
            results[name] = {'status': 'EXCEPTION', 'error': str(e)}
            print(f"❌ {name} - Exception: {e}")
    
    print("\n" + "=" * 40)
    print("SUMMARY:")
    print("=" * 40)
    
    success_count = sum(1 for r in results.values() if r['status'] == 'SUCCESS')
    auth_failed_count = sum(1 for r in results.values() if r['status'] == 'AUTH_FAILED')
    
    if success_count > 0:
        print(f"🎉 {success_count} endpoints working!")
        print("✅ SP-API connection confirmed")
        print("📝 Some endpoints may need AWS role for production")
    elif auth_failed_count == len(test_endpoints):
        print("🔐 All endpoints need AWS role authentication")
        print("📋 Next: Configure IAM user permissions for role assumption")
    else:
        print("❌ Mixed results - check individual endpoints")
    
    print(f"🔑 LWA Token: ✅ Working")
    print(f"🏪 Seller ID: {seller_id}")
    print(f"🛒 Marketplace: {marketplace_id}")
    
    return results

if __name__ == '__main__':
    test_sp_api_simple()