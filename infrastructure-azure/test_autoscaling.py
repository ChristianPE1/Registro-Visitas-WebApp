#!/usr/bin/env python3
"""
Autoscaling Load Test Script
Generates sustained CPU load to trigger Azure VMSS autoscaling
"""

import requests
import time
import sys
import threading
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def stress_worker(base_url, duration, thread_id):
    try:
        url = f"{base_url}/api/stress?duration={duration}"
        log(f"Thread-{thread_id}: Starting stress request")
        response = requests.get(url, timeout=duration+10)
        log(f"Thread-{thread_id}: Completed (HTTP {response.status_code})")
        return response.status_code == 200
    except Exception as e:
        log(f"Thread-{thread_id}: Error - {str(e)}")
        return False

def check_health(base_url):
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_autoscaling.py <LOAD_BALANCER_IP>")
        print("Example: python3 test_autoscaling.py 20.184.147.57")
        sys.exit(1)
    
    lb_ip = sys.argv[1]
    base_url = f"http://{lb_ip}"
    
    print("\nAUTOSCALING LOAD TEST\n")
    log(f"Target: {base_url}")
    
    # Health check
    log("Verifying endpoint availability...")
    if not check_health(base_url):
        log("ERROR: Health check failed. Is the application running?")
        sys.exit(1)
    log("Health check passed")
    
    # Configuration
    num_threads = 8
    stress_duration = 90
    
    log(f"\nConfiguration:")
    log(f"  Threads: {num_threads}")
    log(f"  Duration per thread: {stress_duration}s")
    log(f"  Expected CPU load: >70% sustained")
    log(f"  Expected behavior: VMSS should scale from 1 to 2-3 instances")
    
    log(f"\nStarting load generation...")
    
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(
            target=stress_worker,
            args=(base_url, stress_duration, i+1)
        )
        threads.append(thread)
        thread.start()
        time.sleep(0.5)
    
    for thread in threads:
        thread.join()
    
    log("1. Check VMSS instances:")
    log("   az vmss list-instances -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-vmss -o table")
    log("\n2. Monitor autoscale activity:")
    log("   watch -n 10 'az vmss list-instances -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-vmss -o table'")
    log("\n3. View Grafana dashboard:")
    log(f"   http://{lb_ip}:3000 (admin/admin)")

if __name__ == "__main__":
    main()
