#!/usr/bin/env python3
"""
WallCharmers Direct SP-API Integration - Production Ready
Real-time Amazon seller data without AWS complexity
"""

import requests
import json
import time
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WallCharmersSPAPI:
    def __init__(self):
        # WallCharmers Production SP-API Credentials
        self.client_id = 'amzn1.application-oa2-client.989c167e4b3d439fa1b49ec0d903d33d'
        self.client_secret = 'amzn1.oa2-cs.v1.f25a5855ef9165a35476bec59064820adfea5ee9b4d3fb825252ac0873b4f412'
        self.refresh_token = 'Atzr|IwEBIOnz1ydgqlKByNovrdOwUib8ajfCW8gyjCsDmi21kPflzy2zGF5B0Pa-9ZpFVvKvDFSK2u-HJPQWgAZE5YRsSDnHZICqv7RM6ggQoMrjPxaWAsb_b0bXuivBXcTbNJa9Dz28O2t-_Scv7-CCDNxpoQ3CxY8n1G-u6X_f3Hu8nHqtMPcwUUV0DxeQiZYC2lOrGBsOVpg9c6dnbmNJsL0SaNtYv8ExoNHCSLOoSs8np9cq7yP8PwvMRBHV7QYYVItefMDW6j7KKAAXuhT-jlDDVMLgfyKbiARICJLveZJUmUaZUNoNZgljnQVo8JpgMWoBIJs'
        
        # Production Configuration  
        self.seller_id = 'ADUJPLWTXWPJI'
        self.marketplace_id = 'ATVPDKIKX0DER'  # US
        self.region = 'us-east-1'
        self.base_url = 'https://sellingpartnerapi-na.amazon.com'
        self.lwa_url = 'https://api.amazon.com/auth/o2/token'
        
        # Authentication
        self.access_token = None
        self.token_expires_at = 0
        self.api_calls = 0
        
        # Real WallCharmers SKU → ASIN mapping
        self.sku_mapping = {
            'frog_tow_gol': 'B088HDWG7R',
            'cat_tow_gol': 'B088HDVF7V',
            'oct_tow_gol': 'B094NTH1CQ', 
            'dino_tow_gol': 'B088HDJNYY',
            'skum_whi_gol_FBA': 'B071WGFMC7',
            'cste_nat': 'B082WDDHSL',
            'dino_tow_rus': 'B08JZCFRFB',
            'key_gol_0': 'B07JMTWDRT',
            'anc_rus_FBA': 'B07DHBBJS6',
            '3tr_tray': 'B08TRMF386',
            'arrb_end': 'B089QSWZVC',
            'aus_whi_gol_fba': 'B071JJ6N1R'
        }

    def get_access_token(self):
        """Get LWA access token for SP-API"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
            
        try:
            logger.info("🔑 Getting SP-API access token...")
            response = requests.post(self.lwa_url, data={
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.token_expires_at = time.time() + token_data.get('expires_in', 3600) - 60
                logger.info("✅ SP-API token obtained successfully")
                return self.access_token
            else:
                logger.error(f"❌ Token request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Token error: {e}")
            return None

    def make_api_call(self, endpoint, params=None):
        """Make direct SP-API call"""
        token = self.get_access_token()
        if not token:
            return {'error': 'Authentication failed'}
            
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'x-amz-access-token': token,
            'User-Agent': 'WallCharmers-ViktoryDashboard/3.0'
        }
        
        url = f"{self.base_url}{endpoint}"
        self.api_calls += 1
        
        try:
            logger.info(f"🚀 SP-API Call #{self.api_calls}: {endpoint}")
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            logger.info(f"📊 Response: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("⏳ Rate limited - waiting...")
                time.sleep(2)
                return self.make_api_call(endpoint, params)
            else:
                logger.error(f"❌ API Error {response.status_code}: {response.text}")
                return {'error': f'SP-API Error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            return {'error': str(e)}

    def get_orders_today(self):
        """Get today's orders from SP-API"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        params = {
            'MarketplaceIds': self.marketplace_id,
            'CreatedAfter': today.isoformat() + 'Z',
            'CreatedBefore': datetime.utcnow().isoformat() + 'Z',
            'OrderStatuses': 'Shipped,Delivered'
        }
        
        return self.make_api_call('/orders/v0/orders', params)

    def get_orders_week(self):
        """Get this week's orders"""
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        params = {
            'MarketplaceIds': self.marketplace_id,
            'CreatedAfter': week_ago.isoformat() + 'Z',
            'OrderStatuses': 'Shipped,Delivered'
        }
        
        return self.make_api_call('/orders/v0/orders', params)

    def get_inventory(self):
        """Get current inventory levels"""
        params = {
            'details': 'true',
            'granularityType': 'Marketplace',
            'granularityId': self.marketplace_id,
            'marketplaceIds': self.marketplace_id
        }
        
        return self.make_api_call('/fba/inventory/v1/summaries', params)

    def test_connection(self):
        """Test SP-API connection"""
        logger.info("🧪 Testing SP-API connection...")
        
        # Test 1: Authentication
        token = self.get_access_token()
        if not token:
            return {'status': 'FAILED', 'error': 'Authentication failed'}
        
        # Test 2: Simple API call
        result = self.make_api_call('/orders/v0/orders', {
            'MarketplaceIds': self.marketplace_id,
            'CreatedAfter': (datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z'
        })
        
        if 'error' in result:
            return {'status': 'FAILED', 'error': result['error']}
        
        return {
            'status': 'SUCCESS',
            'seller_id': self.seller_id,
            'marketplace': self.marketplace_id,
            'api_calls_made': self.api_calls,
            'sample_data': result
        }

if __name__ == '__main__':
    print("🇺🇦 WallCharmers SP-API Direct Connection Test")
    print("=" * 50)
    
    api = WallCharmersSPAPI()
    test_result = api.test_connection()
    
    print(f"Status: {test_result['status']}")
    if test_result['status'] == 'SUCCESS':
        print(f"✅ Connected to Seller: {test_result['seller_id']}")
        print(f"✅ Marketplace: {test_result['marketplace']}")
        print(f"✅ API Calls Made: {test_result['api_calls_made']}")
        print("🎉 Ready for real-time data!")
    else:
        print(f"❌ Error: {test_result.get('error', 'Unknown')}")