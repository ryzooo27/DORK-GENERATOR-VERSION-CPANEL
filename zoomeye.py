#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
zoomeye-dork-generator.py — ZoomEye Dork Generator (IMPROVED)
Free tier: 10,000 queries/month - Perfect untuk hunting!

PERBAIKAN:
- Retry logic (3x attempt)
- Flexible timeout (connect=10s, read=30s)
- Better error handling
- Connection pool

Setup:
1. Daftar di https://www.zoomeye.org
2. Get API token: https://www.zoomeye.org/api
3. Gunakan script ini

API Docs: https://www.zoomeye.org/api/doc
"""

import sys
import argparse
import requests
import time
import json
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
# ZOOMEYE SEARCHER (IMPROVED)
# ══════════════════════════════════════════════════════════════

class ZoomEyeSearcher:
    """ZoomEye API Searcher - Free Tier (dengan Retry Logic)"""
    
    def __init__(self, api_token):
        self.api_token = api_token
        self.all_results = []
        self.base_url = "https://api.zoomeye.org"
        self.headers = {
            "Authorization": f"JWT {api_token}",
            "User-Agent": "ZoomEye-API-Client/2.0"
        }
        
        # Setup session dengan retry logic
        self.session = requests.Session()
        retries = Retry(
            total=3,  # Maksimal 3 kali retry
            backoff_factor=1,  # Wait 1s, 2s, 4s between retries
            status_forcelist=[408, 429, 500, 502, 503, 504],  # Retry on these status codes
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def verify_token(self):
        """Verify API token is valid"""
        
        print(f"\n{C.CYAN}[*] Verifying ZoomEye API token...{C.RESET}")
        
        try:
            url = f"{self.base_url}/user/login"
            # timeout = (connect_timeout, read_timeout)
            response = self.session.get(url, headers=self.headers, timeout=(10, 30))
            
            if response.status_code == 200:
                data = response.json()
                print(f"{C.GREEN}[+] Token valid!{C.RESET}")
                print(f"    User: {data.get('username', 'N/A')}")
                print(f"    Credits: {data.get('credits', 'N/A')}")
                return True
            else:
                print(f"{C.RED}[!] Invalid token! Status: {response.status_code}{C.RESET}")
                print(f"    Response: {response.text[:200]}")
                return False
        
        except requests.exceptions.Timeout as e:
            print(f"{C.RED}[!] Timeout Error: {str(e)}{C.RESET}")
            print(f"    💡 Tips: Koneksi kamu lambat atau API sedang overloaded")
            print(f"    Coba lagi dalam beberapa saat...")
            return False
        
        except requests.exceptions.ConnectionError as e:
            print(f"{C.RED}[!] Connection Error: {str(e)}{C.RESET}")
            print(f"    💡 Tips: Pastikan internet kamu stabil")
            print(f"    Atau ISP mungkin memblokir akses ke api.zoomeye.org")
            return False
        
        except Exception as e:
            print(f"{C.RED}[!] Error: {str(e)}{C.RESET}")
            return False
    
    def search(self, query, page=1, max_pages=5):
        """Search ZoomEye dengan retry logic"""
        
        print(f"\n{C.CYAN}[*] Searching ZoomEye...{C.RESET}")
        print(f"    Query: {query[:80]}...")
        
        page_num = page
        
        while page_num <= max_pages:
            try:
                url = f"{self.base_url}/host/search"
                params = {
                    "query": query,
                    "page": page_num,
                    "pagesize": 50
                }
                
                print(f"    Page {page_num}...", end=" ", flush=True)
                
                # Timeout: (connect=10s, read=30s)
                response = self.session.get(
                    url, 
                    headers=self.headers, 
                    params=params, 
                    timeout=(10, 30)
                )
                
                if response.status_code != 200:
                    print(f"\n{C.RED}[!] HTTP {response.status_code}{C.RESET}")
                    if response.status_code == 401:
                        print(f"    Invalid API token!")
                    break
                
                data = response.json()
                
                # Check for errors
                if 'error' in data:
                    print(f"\n{C.RED}[!] Error: {data.get('error')}{C.RESET}")
                    break
                
                # Get results
                matches = data.get('matches', [])
                
                if not matches:
                    print(f"{C.GREEN}✓ No more results{C.RESET}")
                    break
                
                # Parse results
                for match in matches:
                    try:
                        ip = match.get('ip')
                        port = match.get('portinfo', {}).get('port', 2087)
                        service = match.get('portinfo', {}).get('service', '')
                        banner = match.get('portinfo', {}).get('banner', '')
                        
                        server_url = f"https://{ip}:{port}"
                        
                        result_data = {
                            "url": server_url,
                            "ip": ip,
                            "port": port,
                            "service": service,
                            "banner": banner
                        }
                        
                        self.all_results.append(result_data)
                    except:
                        pass
                
                print(f"{C.GREEN}✓ {len(matches)} results (Total: {len(self.all_results)}){C.RESET}")
                
                page_num += 1
                time.sleep(0.5)  # Rate limiting
            
            except requests.exceptions.Timeout:
                print(f"\n{C.YELLOW}[!] Timeout on page {page_num} (retrying...){C.RESET}")
                time.sleep(2)
                continue
            
            except requests.exceptions.ConnectionError as e:
                print(f"\n{C.RED}[!] Connection error: {str(e)[:60]}{C.RESET}")
                break
            
            except Exception as e:
                print(f"\n{C.RED}[!] Error: {str(e)[:80]}{C.RESET}")
                break
        
        return len(self.all_results)
    
    def deduplicate(self):
        """Remove duplicates by IP"""
        
        before = len(self.all_results)
        seen_ips = set()
        unique = []
        
        for result in self.all_results:
            ip = result.get('ip')
            if ip not in seen_ips:
                seen_ips.add(ip)
                unique.append(result)
        
        self.all_results = unique
        after = len(self.all_results)
        
        if before > after:
            print(f"{C.YELLOW}[*] Removed {before - after} duplicates{C.RESET}")
    
    def save_targets(self, filename):
        """Save just URLs"""
        
        if not self.all_results:
            print(f"{C.RED}[!] No results to save{C.RESET}")
            return
        
        try:
            with open(filename, "w") as f:
                for result in self.all_results:
                    f.write(f"{result['url']}\n")
            
            print(f"{C.GREEN}[+] Saved {len(self.all_results)} targets to {filename}{C.RESET}")
        except Exception as e:
            print(f"{C.RED}[!] Error: {e}{C.RESET}")
    
    def save_detailed(self, filename):
        """Save detailed JSON"""
        
        if not self.all_results:
            print(f"{C.RED}[!] No results to save{C.RESET}")
            return
        
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "total": len(self.all_results),
                "results": self.all_results
            }
            
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            
            print(f"{C.GREEN}[+] Saved detailed data to {filename}{C.RESET}")
        except Exception as e:
            print(f"{C.RED}[!] Error: {e}{C.RESET}")

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="ZoomEye Dork Generator - Free tier (10k/month) [IMPROVED]",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
SETUP:
1. Daftar: https://www.zoomeye.org
2. Get API Token: https://www.zoomeye.org/api
3. Keep it safe!

USAGE:

# Test connection
python3 zoomeye-dork-generator-FIXED.py --token YOUR_TOKEN --verify

# Single query
python3 zoomeye-dork-generator-FIXED.py --token YOUR_TOKEN \\
  --query 'port:2087 service:cPanel' \\
  -o results.txt

# Batch queries
python3 zoomeye-dork-generator-FIXED.py --token YOUR_TOKEN \\
  --batch dorks.txt \\
  -o results.txt

EXAMPLE QUERIES:
- port:2087 service:cPanel
- port:2087 banner:WHM
- port:2087 title:WHM
- port:2087 country:ID
- port:2087

IMPROVEMENTS:
✓ Auto-retry logic (max 3x)
✓ Flexible timeout (10s connect, 30s read)
✓ Better error messages
✓ Connection pooling
        """
    )
    
    parser.add_argument("-t", "--token", required=True, help="ZoomEye API token")
    parser.add_argument("-q", "--query", help="Single query")
    parser.add_argument("-b", "--batch", help="Batch file with queries")
    parser.add_argument("-o", "--output", help="Output file (targets.txt)")
    parser.add_argument("-j", "--json", help="Output JSON file (detailed)")
    parser.add_argument("-p", "--pages", type=int, default=5, help="Max pages per query (default: 5)")
    parser.add_argument("--verify", action="store_true", help="Verify API token only")
    
    args = parser.parse_args()
    
    print(f"\n{C.BOLD}{C.BLUE}═══════════════════════════════════════{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}  ZOOMEYE DORK GENERATOR (IMPROVED){C.RESET}")
    print(f"{C.BOLD}{C.BLUE}═══════════════════════════════════════{C.RESET}")
    
    searcher = ZoomEyeSearcher(args.token)
    
    # Verify token
    if args.verify:
        searcher.verify_token()
        return
    
    if not searcher.verify_token():
        return
    
    # Single query
    if args.query:
        searcher.search(args.query, max_pages=args.pages)
        searcher.deduplicate()
        
        if args.output:
            searcher.save_targets(args.output)
        if args.json:
            searcher.save_detailed(args.json)
        
        print(f"\n{C.GREEN}[+] Total results: {len(searcher.all_results)}{C.RESET}\n")
    
    # Batch queries
    elif args.batch:
        try:
            with open(args.batch, "r") as f:
                queries = [line.strip() for line in f if line.strip()]
            
            print(f"\n{C.GREEN}[+] Loaded {len(queries)} queries{C.RESET}")
            
            for query in queries:
                searcher.search(query, max_pages=args.pages)
            
            searcher.deduplicate()
            
            if args.output:
                searcher.save_targets(args.output)
            if args.json:
                searcher.save_detailed(args.json)
            
            print(f"\n{C.GREEN}[+] Total results: {len(searcher.all_results)}{C.RESET}\n")
        
        except Exception as e:
            print(f"{C.RED}[!] Error: {e}{C.RESET}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
