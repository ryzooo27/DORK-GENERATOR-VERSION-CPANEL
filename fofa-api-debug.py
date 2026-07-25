#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
fofa-api-debug.py — Debug FOFA API Response
Untuk lihat apa yang actually di-return oleh FOFA
"""

import sys
import argparse
import requests
import base64
import json

# ══════════════════════════════════════════════════════════════
# COLORS
# ══════════════════════════════════════════════════════════════

class C:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

# ══════════════════════════════════════════════════════════════
# DEBUG FOFA API
# ══════════════════════════════════════════════════════════════

def debug_fofa_api(email, api_key, dork):
    """Debug FOFA API response"""
    
    print(f"\n{C.BOLD}{C.BLUE}═══════════════════════════════════════{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}  FOFA API RESPONSE DEBUG{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}═══════════════════════════════════════{C.RESET}\n")
    
    print(f"{C.CYAN}[*] Input Dork:{C.RESET}")
    print(f"    {dork}\n")
    
    # Encode dork
    dork_encoded = base64.b64encode(dork.encode()).decode()
    
    print(f"{C.CYAN}[*] Encoded Dork:{C.RESET}")
    print(f"    {dork_encoded}\n")
    
    # Build API request
    url = "https://fofa.info/api/v1/search/all"
    params = {
        "email": email,
        "key": api_key,
        "qbase64": dork_encoded,
        "page": 1,
        "size": 100,
        "full": "false"
    }
    
    print(f"{C.CYAN}[*] API Request:{C.RESET}")
    print(f"    URL: {url}")
    print(f"    Params: {json.dumps(params, indent=4)}\n")
    
    try:
        print(f"{C.CYAN}[*] Sending request...{C.RESET}\n")
        response = requests.get(url, params=params, timeout=10)
        
        print(f"{C.CYAN}[*] Response Status: {C.BOLD}{response.status_code}{C.RESET}\n")
        
        print(f"{C.CYAN}[*] Response Headers:{C.RESET}")
        for key, value in response.headers.items():
            print(f"    {key}: {value}")
        
        print(f"\n{C.CYAN}[*] Response Body (Raw):{C.RESET}")
        print(f"    {response.text[:500]}\n")
        
        print(f"{C.CYAN}[*] Response Body (JSON):{C.RESET}")
        try:
            data = response.json()
            print(json.dumps(data, indent=2)[:2000])
        except:
            print(f"    {C.RED}[!] Not valid JSON{C.RESET}")
            print(f"    {response.text}")
        
        print(f"\n{C.CYAN}[*] Data Analysis:{C.RESET}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"    Status: {C.GREEN}{data.get('status', 'N/A')}{C.RESET}")
            print(f"    Error: {data.get('error', 'None')}")
            
            results = data.get('results', [])
            print(f"    Results count (page 1): {len(results)}")
            
            if results:
                print(f"\n    {C.GREEN}First 5 results:{C.RESET}")
                for i, result in enumerate(results[:5], 1):
                    print(f"      {i}. {result}")
            else:
                print(f"\n    {C.YELLOW}⚠ No results on page 1{C.RESET}")
        
        else:
            print(f"    {C.RED}Error code: {response.status_code}{C.RESET}")
            print(f"    Response: {response.text[:200]}")
    
    except Exception as e:
        print(f"    {C.RED}Exception: {str(e)}{C.RESET}")
    
    print(f"\n{C.BOLD}{C.BLUE}═══════════════════════════════════════{C.RESET}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Debug FOFA API Response",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
USAGE:

python3 fofa-api-debug.py --email your@email.com --key YOUR_KEY \\
  --dork 'port="2087" && "Server Administrator"'

python3 fofa-api-debug.py --email your@email.com --key YOUR_KEY \\
  --dork 'port="2087"'

EXAMPLE DORKS:
- port="2087"
- port="2087" && "Server Administrator"
- port="2087" && title="WHM Login"
- port="2087" && body="cPanel"
        """
    )
    
    parser.add_argument("-e", "--email", required=True, help="FOFA email")
    parser.add_argument("-k", "--key", required=True, help="FOFA API key")
    parser.add_argument("-d", "--dork", required=True, help="Dork query")
    
    args = parser.parse_args()
    
    debug_fofa_api(args.email, args.key, args.dork)

if __name__ == "__main__":
    main()
