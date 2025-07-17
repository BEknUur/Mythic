#!/usr/bin/env python3
"""
Performance testing script for MythicAI status endpoint
"""

import requests
import time
import statistics
from datetime import datetime
import sys

def test_status_endpoint(run_id: str, num_requests: int = 10):
    """Test the status endpoint performance"""
    print(f"🔍 Testing status endpoint performance for run_id: {run_id}")
    print(f"📊 Making {num_requests} requests...")
    
    response_times = []
    success_count = 0
    timeout_count = 0
    error_count = 0
    
    for i in range(num_requests):
        start_time = time.time()
        
        try:
            response = requests.get(
                f'https://mythicai.me/api/status/{run_id}', 
                timeout=15
            )
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code == 200:
                success_count += 1
                response_times.append(response_time)
                print(f"✅ Request {i+1}: {response_time:.1f}ms")
            else:
                error_count += 1
                print(f"❌ Request {i+1}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            timeout_count += 1
            print(f"⏰ Request {i+1}: Timeout (>15s)")
        except Exception as e:
            error_count += 1
            print(f"💥 Request {i+1}: Error - {e}")
    
    # Calculate statistics
    if response_times:
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"\n📈 PERFORMANCE RESULTS:")
        print(f"   Average response time: {avg_time:.1f}ms")
        print(f"   Median response time: {median_time:.1f}ms")
        print(f"   Min response time: {min_time:.1f}ms")
        print(f"   Max response time: {max_time:.1f}ms")
        
        if avg_time > 5000:
            print(f"   ⚠️  Average response time is high (>5s)")
        elif avg_time > 2000:
            print(f"   ⚠️  Average response time is moderate (>2s)")
        else:
            print(f"   ✅ Average response time is good (<2s)")
    else:
        print(f"\n❌ No successful requests to calculate statistics")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Successful requests: {success_count}/{num_requests}")
    print(f"   Timeout requests: {timeout_count}/{num_requests}")
    print(f"   Error requests: {error_count}/{num_requests}")
    
    return success_count > 0

def main():
    print(f"🚀 MythicAI Performance Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test with a dummy run ID
    test_run_id = "test-performance-123"
    
    # Run performance test
    success = test_status_endpoint(test_run_id, 10)
    
    if success:
        print(f"\n✅ Performance test completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Performance test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 