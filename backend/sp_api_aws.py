#!/usr/bin/env python3
"""
WallCharmers SP-API with AWS Role Assumption - Production Ready
Real-time Amazon seller data with proper AWS authentication
"""

import requests
import json
import time
import boto3
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from urllib.parse import urlencode, quote
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WallCharmersSPAPIAWS:
    def __init__(self):
        # Load credentials from environment variables
        import os
        self.client_id = os.getenv('SP_API_CLIENT_ID')
        self.client_secret = os.getenv('SP_API_CLIENT_SECRET')
        self.refresh_token = os.getenv('SP_API_REFRESH_TOKEN')
        
        # AWS Configuration from environment
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.role_arn = os.getenv('AWS_ROLE_ARN')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
        # SP-API Configuration
        self.seller_id = os.getenv('SELLER_ID')
        self.marketplace_id = os.getenv('MARKETPLACE_ID', 'ATVPDKIKX0DER')
        self.base_url = 'https://sellingpartnerapi-na.amazon.com'
        self.lwa_url = 'https://api.amazon.com/auth/o2/token'
        
        # Authentication tokens
        self.lwa_access_token = None
        self.lwa_token_expires_at = 0
        self.aws_session = None
        self.aws_session_expires_at = 0
        self.api_calls = 0

    def get_lwa_token(self):
        """Get LWA access token"""
        if self.lwa_access_token and time.time() < self.lwa_token_expires_at:
            return self.lwa_access_token
            
        try:
            logger.info("🔑 Getting LWA access token...")
            response = requests.post(self.lwa_url, data={
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                self.lwa_access_token = token_data['access_token']
                self.lwa_token_expires_at = time.time() + token_data.get('expires_in', 3600) - 60
                logger.info("✅ LWA token obtained")
                return self.lwa_access_token
            else:
                logger.error(f"❌ LWA token failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ LWA token error: {e}")
            return None

    def assume_role(self):
        """Assume AWS IAM role for SP-API"""
        if self.aws_session and time.time() < self.aws_session_expires_at:
            return self.aws_session
            
        try:
            logger.info("🔐 Assuming AWS IAM role...")
            
            # Create STS client with base credentials
            sts_client = boto3.client(
                'sts',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.region
            )
            
            # Assume the SP-API role
            response = sts_client.assume_role(
                RoleArn=self.role_arn,
                RoleSessionName='ViktoryDashboard-Session'
            )
            
            credentials = response['Credentials']
            self.aws_session = {
                'access_key': credentials['AccessKeyId'],
                'secret_key': credentials['SecretAccessKey'],
                'session_token': credentials['SessionToken']
            }
            self.aws_session_expires_at = credentials['Expiration'].timestamp() - 60
            
            logger.info("✅ AWS role assumed successfully")
            return self.aws_session
            
        except Exception as e:
            logger.error(f"❌ AWS role assumption failed: {e}")
            return None

    def create_aws_signature(self, method, url, headers, payload=''):
        """Create AWS Signature Version 4"""
        session = self.assume_role()
        if not session:
            return None
            
        # Parse URL
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        host = parsed_url.netloc
        canonical_uri = parsed_url.path or '/'
        canonical_querystring = parsed_url.query or ''
        
        # Create canonical request
        canonical_headers = '\n'.join([f"{k.lower()}:{v}" for k, v in sorted(headers.items())]) + '\n'
        signed_headers = ';'.join([k.lower() for k in sorted(headers.keys())])
        
        payload_hash = hashlib.sha256(payload.encode()).hexdigest()
        canonical_request = f"{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        
        # Create string to sign
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        date_stamp = timestamp[:8]
        credential_scope = f"{date_stamp}/{self.region}/execute-api/aws4_request"
        algorithm = 'AWS4-HMAC-SHA256'
        
        string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode()).hexdigest()}"
        
        # Calculate signature
        signing_key = self.get_signature_key(session['secret_key'], date_stamp, self.region, 'execute-api')
        signature = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()
        
        # Create authorization header
        authorization = f"{algorithm} Credential={session['access_key']}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        
        # Add AWS headers
        headers['Authorization'] = authorization
        headers['X-Amz-Date'] = timestamp
        if session['session_token']:
            headers['X-Amz-Security-Token'] = session['session_token']
            
        return headers

    def get_signature_key(self, key, date_stamp, region_name, service_name):
        """Create signing key for AWS Signature V4"""
        k_date = hmac.new(f'AWS4{key}'.encode(), date_stamp.encode(), hashlib.sha256).digest()
        k_region = hmac.new(k_date, region_name.encode(), hashlib.sha256).digest()
        k_service = hmac.new(k_region, service_name.encode(), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, 'aws4_request'.encode(), hashlib.sha256).digest()
        return k_signing

    def make_sp_api_call(self, endpoint, params=None):
        """Make SP-API call with proper AWS authentication"""
        lwa_token = self.get_lwa_token()
        if not lwa_token:
            return {'error': 'LWA authentication failed'}
            
        # Construct URL
        url = f"{self.base_url}{endpoint}"
        if params:
            url += '?' + urlencode(params)
            
        # Base headers
        headers = {
            'host': 'sellingpartnerapi-na.amazon.com',
            'user-agent': 'WallCharmers-ViktoryDashboard/3.0',
            'x-amz-access-token': lwa_token
        }
        
        # Add AWS signature
        signed_headers = self.create_aws_signature('GET', url, headers.copy())
        if not signed_headers:
            return {'error': 'AWS signature creation failed'}
            
        self.api_calls += 1
        
        try:
            logger.info(f"🚀 SP-API Call #{self.api_calls}: {endpoint}")
            response = requests.get(url, headers=signed_headers, timeout=15)
            
            logger.info(f"📊 Response: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("⏳ Rate limited - waiting...")
                time.sleep(2)
                return self.make_sp_api_call(endpoint, params)
            else:
                logger.error(f"❌ API Error {response.status_code}: {response.text}")
                return {'error': f'SP-API Error: {response.status_code}', 'details': response.text}
                
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            return {'error': str(e)}

    def get_orders_today(self):
        """Get today's orders"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        params = {
            'MarketplaceIds': self.marketplace_id,
            'CreatedAfter': today.isoformat() + 'Z',
            'OrderStatuses': 'Shipped,Delivered'
        }
        return self.make_sp_api_call('/orders/v0/orders', params)
    
    def get_orders_week(self):
        """Get this week's orders"""
        week_ago = datetime.utcnow() - timedelta(days=7)
        params = {
            'MarketplaceIds': self.marketplace_id,
            'CreatedAfter': week_ago.isoformat() + 'Z',
            'OrderStatuses': 'Shipped,Delivered'
        }
        return self.make_sp_api_call('/orders/v0/orders', params)

    def get_inventory(self):
        """Get inventory levels"""
        params = {
            'details': 'true',
            'granularityType': 'Marketplace',
            'granularityId': self.marketplace_id,
            'marketplaceIds': self.marketplace_id
        }
        return self.make_sp_api_call('/fba/inventory/v1/summaries', params)

    def test_connection(self):
        """Test complete SP-API connection"""
        logger.info("🧪 Testing SP-API connection with AWS authentication...")
        
        # Test 1: LWA Token
        lwa_token = self.get_lwa_token()
        if not lwa_token:
            return {'status': 'FAILED', 'step': 'LWA_TOKEN', 'error': 'LWA token failed'}
        
        # Test 2: AWS Role
        aws_session = self.assume_role()
        if not aws_session:
            return {'status': 'FAILED', 'step': 'AWS_ROLE', 'error': 'AWS role assumption failed'}
        
        # Test 3: SP-API Call
        result = self.make_sp_api_call('/orders/v0/orders', {
            'MarketplaceIds': self.marketplace_id,
            'CreatedAfter': (datetime.utcnow() - timedelta(hours=24)).isoformat() + 'Z'
        })
        
        if 'error' in result:
            return {'status': 'FAILED', 'step': 'SP_API_CALL', 'error': result['error'], 'details': result.get('details')}
        
        return {
            'status': 'SUCCESS',
            'seller_id': self.seller_id,
            'marketplace': self.marketplace_id,
            'api_calls_made': self.api_calls,
            'lwa_token_valid': True,
            'aws_role_valid': True,
            'sample_orders': len(result.get('payload', {}).get('Orders', []))
        }

if __name__ == '__main__':
    print("🇺🇦 WallCharmers SP-API + AWS Integration Test")
    print("=" * 55)
    
    # Install boto3 if needed
    try:
        import boto3
    except ImportError:
        print("Installing boto3...")
        import subprocess
        subprocess.check_call(['pip3', 'install', 'boto3'])
        import boto3
    
    api = WallCharmersSPAPIAWS()
    test_result = api.test_connection()
    
    print(f"Status: {test_result['status']}")
    
    if test_result['status'] == 'SUCCESS':
        print(f"✅ Seller ID: {test_result['seller_id']}")
        print(f"✅ Marketplace: {test_result['marketplace']}")
        print(f"✅ API Calls: {test_result['api_calls_made']}")
        print(f"✅ Sample Orders Found: {test_result['sample_orders']}")
        print("🎉 READY FOR REAL-TIME DATA!")
    else:
        print(f"❌ Failed at: {test_result['step']}")
        print(f"❌ Error: {test_result['error']}")
        if 'details' in test_result:
            print(f"❌ Details: {test_result['details']}")