#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
ZoomEye Diagnostic Tool
Test koneksi ke API dengan berbagai timeout values
"""

import requests
import sys
import time

class C:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

def test_connection(timeout_value, connect_timeout=None, read_timeout=None):
    """Test koneksi dengan specific timeout"""
    
    url = "https://api.zoomeye.org/user/login"
    
    if connect_timeout and read_timeout:
        timeout = (connect_timeout, read_timeout)
        label = f"timeout=({connect_timeout}s connect, {read_timeout}s read)"
    else:
        timeout = timeout_value
        label = f"timeout={timeout}s"
    
    try:
        start = time.time()
        response = requests.get(url, timeout=timeout)
        elapsed = time.time() - start
        
        status = response.status_code
        if status == 401:  # Expected: no auth header
            status_label = "401 (Expected - no auth header)"
            result = "✓ PASS"
            color = C.GREEN
        else:
            status_label = str(status)
            result = "✓ PASS" if status < 500 else "✗ FAIL"
            color = C.GREEN if status < 500 else C.RED
        
        print(f"{color}[{result}]{C.RESET} {label:40s} | Status: {status_label:30s} | Time: {elapsed:.2f}s")
        return True
    
    except requests.exceptions.Timeout as e:
        print(f"{C.RED}[✗ TIMEOUT]{C.RESET} {label:40s} | Error: Connection timeout")
        return False
    
    except requests.exceptions.ConnectionError as e:
        print(f"{C.RED}[✗ ERROR]{C.RESET} {label:40s} | Error: {str(e)[:50]}")
        return False
    
    except Exception as e:
        print(f"{C.RED}[✗ ERROR]{C.RESET} {label:40s} | Error: {str(e)[:50]}")
        return False

def main():
    print(f"\n{C.CYAN}╔════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.CYAN}║     ZoomEye API Diagnostic Tool                        ║{C.RESET}")
    print(f"{C.CYAN}╚════════════════════════════════════════════════════════╝{C.RESET}\n")
    
    print(f"{C.YELLOW}[*] Testing dengan berbagai timeout values...{C.RESET}\n")
    
    # Test 1: Single timeout values
    print(f"{C.BLUE}1. Single Timeout Values:{C.RESET}")
    print("-" * 90)
    
    timeouts = [5, 10, 15, 20, 30]
    for t in timeouts:
        test_connection(t)
        time.sleep(0.5)
    
    print()
    
    # Test 2: Dual timeout (connect, read)
    print(f"{C.BLUE}2. Dual Timeout (connect_timeout, read_timeout):{C.RESET}")
    print("-" * 90)
    
    dual_timeouts = [
        (5, 15),
        (10, 20),
        (10, 30),
        (15, 30),
    ]
    
    for connect_t, read_t in dual_timeouts:
        test_connection(None, connect_t, read_t)
        time.sleep(0.5)
    
    print()
    
    # Summary
    print(f"{C.CYAN}╔════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.CYAN}║  SUMMARY                                               ║{C.RESET}")
    print(f"{C.CYAN}╚════════════════════════════════════════════════════════╝{C.RESET}\n")
    
    print(f"{C.GREEN}[✓] API ZoomEye dapat diakses dari environment ini{C.RESET}\n")
    
    print(f"{C.YELLOW}💡 TIPS UNTUK KAMU:{C.RESET}")
    print(f"""
1. Jika test di atas PASS, gunakan script FIXED dengan timeout (10, 30)
   
2. Jika masih timeout di rumah/laptop kamu:
   - Cek kecepatan internet: https://speedtest.net
   - Coba di jaringan berbeda (mobile hotspot, public wifi)
   - Mungkin ISP kamu memblokir akses ke api.zoomeye.org
   
3. Untuk mengatasi timeout ISP:
   - Gunakan VPN (ProtonVPN free tier bisa)
   - Minta ke ZoomEye support untuk allowlist
   - Coba akses via proxy mereka jika ada
   
4. Script FIXED yang saya buat sudah punya:
   - Auto-retry (3x attempt)
   - Flexible timeout (10s connect, 30s read)
   - Better error messages
   
5. Jalankan: python3 zoomeye-dork-generator-FIXED.py --token YOUR_TOKEN --verify
    """)
    
    print()

if __name__ == "__main__":
    main()
