#!/usr/bin/env python3
"""
WallCharmers Viktory Dashboard Flask Backend
Real-time SP-API integration with fallback to demo data
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import SP-API client
try:
    from sp_api_aws import WallCharmersSPAPIAWS
    SP_API_AVAILABLE = True
    logger.info("✅ SP-API client available")
except ImportError as e:
    SP_API_AVAILABLE = False
    logger.warning(f"⚠️ SP-API client not available: {e}")

class ViktoryDashboard:
    def __init__(self):
        self.sp_api = None
        if SP_API_AVAILABLE:
            try:
                self.sp_api = WallCharmersSPAPIAWS()
                logger.info("✅ SP-API client initialized")
            except Exception as e:
                logger.error(f"❌ SP-API initialization failed: {e}")
                
    def get_dashboard_data(self):
        """Get comprehensive dashboard data"""
        
        # Try to get real SP-API data
        if self.sp_api:
            try:
                logger.info("🚀 Fetching real SP-API data...")
                
                # Get today's orders
                today_orders = self.sp_api.get_orders_today()
                week_orders = self.sp_api.get_orders_week() 
                inventory = self.sp_api.get_inventory()
                
                if not any('error' in data for data in [today_orders, week_orders, inventory]):
                    logger.info("✅ SP-API data retrieved successfully")
                    return self.process_sp_api_data(today_orders, week_orders, inventory)
                else:
                    logger.warning("⚠️ SP-API returned errors, using fallback data")
                    
            except Exception as e:
                logger.error(f"❌ SP-API call failed: {e}")
        
        # Fallback to enhanced demo data
        logger.info("📊 Using enhanced demo data")
        return self.get_enhanced_demo_data()
    
    def process_sp_api_data(self, today_orders, week_orders, inventory):
        """Process real SP-API data into dashboard format"""
        
        # Extract order data
        today_order_list = today_orders.get('payload', {}).get('Orders', [])
        week_order_list = week_orders.get('payload', {}).get('Orders', [])
        
        # Calculate metrics
        today_metrics = {
            'orders': len(today_order_list),
            'units': sum(len(order.get('OrderItems', [])) for order in today_order_list),
            'revenue': sum(len(order.get('OrderItems', [])) * 45.50 for order in today_order_list),  # Estimate
            'source': 'api'
        }
        
        week_metrics = {
            'orders': len(week_order_list),
            'units': sum(len(order.get('OrderItems', [])) for order in week_order_list),
            'revenue': sum(len(order.get('OrderItems', [])) * 45.50 for order in week_order_list),
            'source': 'api'
        }
        
        # Calculate profit (estimate 17.5% margin)
        today_metrics['profit'] = today_metrics['revenue'] * 0.175
        today_metrics['margin'] = 17.5
        
        week_metrics['profit'] = week_metrics['revenue'] * 0.175  
        week_metrics['margin'] = 17.5
        
        # Process inventory data
        inventory_list = inventory.get('payload', {}).get('inventorySummaries', [])
        
        return {
            'summary': {
                'today': today_metrics,
                'yesterday': {**today_metrics, 'source': 'estimated'},
                'week': week_metrics,
                'last_week': {**week_metrics, 'source': 'estimated'}, 
                'month': {'revenue': 60261.07, 'orders': 1024, 'units': 1138, 'profit': 10752.76, 'margin': 17.84, 'source': 'spreadsheet'},
                'last_month': {'revenue': 55432.18, 'orders': 942, 'units': 1047, 'profit': 9877.74, 'margin': 17.82, 'source': 'spreadsheet'}
            },
            'inventory': inventory_list,
            'api_status': 'connected',
            'last_updated': datetime.utcnow().isoformat(),
            'data_source': 'sp_api'
        }
    
    def get_enhanced_demo_data(self):
        """Enhanced demo data based on real WallCharmers patterns"""
        import random
        
        # Realistic variations
        base_today_revenue = 1847.23
        daily_variation = random.uniform(0.85, 1.15)
        
        today_revenue = base_today_revenue * daily_variation
        today_orders = random.randint(28, 38)
        today_units = random.randint(32, 42)
        
        return {
            'summary': {
                'today': {
                    'revenue': today_revenue,
                    'orders': today_orders,
                    'units': today_units,
                    'profit': today_revenue * 0.174,
                    'margin': 17.4,
                    'source': 'demo'
                },
                'yesterday': {
                    'revenue': 2134.56,
                    'orders': 35,
                    'units': 42, 
                    'profit': 378.92,
                    'margin': 17.8,
                    'source': 'demo'
                },
                'week': {
                    'revenue': 12456.78 * random.uniform(0.95, 1.05),
                    'orders': random.randint(190, 220),
                    'units': random.randint(235, 265),
                    'profit': 2189.34,
                    'margin': 17.6,
                    'source': 'demo'
                },
                'last_week': {
                    'revenue': 11234.89,
                    'orders': 187,
                    'units': 223,
                    'profit': 1967.45,
                    'margin': 17.5,
                    'source': 'demo'
                },
                'month': {
                    'revenue': 60261.07,
                    'orders': 1024,
                    'units': 1138,
                    'profit': 10752.76,
                    'margin': 17.84,
                    'source': 'spreadsheet'
                },
                'last_month': {
                    'revenue': 55432.18,
                    'orders': 942,
                    'units': 1047,
                    'profit': 9877.74,
                    'margin': 17.82,
                    'source': 'spreadsheet'
                }
            },
            'api_status': 'demo',
            'last_updated': datetime.utcnow().isoformat(),
            'data_source': 'demo'
        }

# Initialize dashboard
dashboard = ViktoryDashboard()

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'sp_api_available': SP_API_AVAILABLE,
        'sp_api_working': dashboard.sp_api is not None
    })

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """Get complete dashboard data"""
    try:
        data = dashboard.get_dashboard_data()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Dashboard data error: {e}")
        return jsonify({
            'error': 'Failed to fetch dashboard data',
            'api_status': 'error',
            'last_updated': datetime.utcnow().isoformat()
        }), 500

@app.route('/api/test-sp-api')
def test_sp_api():
    """Test SP-API connection"""
    if not SP_API_AVAILABLE:
        return jsonify({
            'status': 'unavailable',
            'message': 'SP-API client not available'
        })
    
    if not dashboard.sp_api:
        return jsonify({
            'status': 'error',
            'message': 'SP-API client not initialized'
        })
    
    try:
        result = dashboard.sp_api.test_connection()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    print("🇺🇦 WallCharmers Viktory Dashboard Backend")
    print("=" * 50)
    print(f"SP-API Available: {SP_API_AVAILABLE}")
    print(f"Dashboard Initialized: {dashboard.sp_api is not None}")
    print("=" * 50)
    print("Starting Flask server...")
    print("Frontend will connect to: http://localhost:5000/api")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
