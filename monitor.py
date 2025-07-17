#!/usr/bin/env python3
"""
Monitoring script for MythicAI to track 504 timeout issues
"""

import requests
import time
import json
from datetime import datetime
import sys

def check_health():
    """Check the health endpoint"""
    try:
        response = requests.get('https://mythicai.me/api/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data.get('message', 'OK')}")
            if 'system' in data:
                sys_info = data['system']
                print(f"   Memory: {sys_info.get('memory_percent', 'N/A')}%")
                print(f"   CPU: {sys_info.get('cpu_percent', 'N/A')}%")
                print(f"   Disk: {sys_info.get('disk_percent', 'N/A')}%")
            return True
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Health check timeout")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def check_status_endpoint():
    """Test the status endpoint with a dummy run ID"""
    try:
        # Use a dummy run ID for testing
        test_run_id = "test-monitoring-123"
        response = requests.get(f'https://mythicai.me/api/status/{test_run_id}', timeout=30)
        
        if response.status_code == 401:
            print("✅ Status endpoint responding (401 Unauthorized - expected for test)")
            return True
        elif response.status_code == 200:
            print("✅ Status endpoint responding (200 OK)")
            return True
        else:
            print(f"⚠️  Status endpoint returned HTTP {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Status endpoint timeout (504 Gateway Timeout)")
        return False
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
        return False

def main():
    print(f"🔍 MythicAI Monitoring - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Check health endpoint
    print("\n1. Checking health endpoint...")
    health_ok = check_health()
    
    # Check status endpoint
    print("\n2. Checking status endpoint...")
    status_ok = check_status_endpoint()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"   Health endpoint: {'✅ OK' if health_ok else '❌ FAILED'}")
    print(f"   Status endpoint: {'✅ OK' if status_ok else '❌ FAILED'}")
    
    if not health_ok or not status_ok:
        print("\n🚨 Issues detected! Check the following:")
        print("   - Backend service status")
        print("   - Nginx configuration")
        print("   - Network connectivity")
        print("   - Server resources (CPU, memory, disk)")
        sys.exit(1)
    else:
        print("\n✅ All systems operational!")
        sys.exit(0)

if __name__ == "__main__":
    main() 