#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
dork-tester-ranking.py — Test semua dork dan ranking hasil
Berguna untuk menemukan dork mana yang paling banyak hasil
"""

import sys
import argparse
import requests
import base64
import time
import json
from datetime import datetime

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
# DORK TESTER & RANKER
# ══════════════════════════════════════════════════════════════

class DorkTesterRanker:
    """Test dork dan ranking hasilnya"""
    
    def __init__(self, platform="fofa", email=None, api_key=None):
        self.platform = platform.lower()
        self.email = email
        self.api_key = api_key
        self.results = {}
    
    def test_fofa_dork(self, dork):
        """Test satu dork di FOFA"""
        
        try:
            dork_encoded = base64.b64encode(dork.encode()).decode()
            
            url = "https://fofa.info/api/v1/search/all"
            params = {
                "email": self.email,
                "key": self.api_key,
                "qbase64": dork_encoded,
                "page": 1,
                "size": 100,
                "full": "false"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                return len(results)
            else:
                return -1  # Error
        
        except Exception as e:
            return -1
    
    def test_shodan_dork(self, dork):
        """Test satu dork di Shodan"""
        
        try:
            url = "https://api.shodan.io/shodan/host/search"
            params = {
                "key": self.api_key,
                "query": dork,
                "page": 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('matches', [])
                return len(matches)
            else:
                return -1  # Error
        
        except Exception as e:
            return -1
    
    def test_all_dorks(self, dork_file):
        """Test semua dork dari file"""
        
        try:
            with open(dork_file, "r") as f:
                dorks = [line.strip() for line in f if line.strip()]
        except:
            print(f"{C.RED}[!] Error reading file: {dork_file}{C.RESET}")
            return
        
        print(f"\n{C.CYAN}[*] Testing {len(dorks)} dorks dari {dork_file}...{C.RESET}\n")
        
        for i, dork in enumerate(dorks, 1):
            print(f"{C.YELLOW}[{i}/{len(dorks)}] Testing: {dork[:60]}...{C.RESET}", end=" ")
            
            if self.platform == "fofa":
                count = self.test_fofa_dork(dork)
            else:
                count = self.test_shodan_dork(dork)
            
            if count >= 0:
                print(f"{C.GREEN}✓ {count} results{C.RESET}")
                self.results[dork] = count
            else:
                print(f"{C.RED}✗ Error{C.RESET}")
                self.results[dork] = 0
            
            time.sleep(0.5)  # Jangan spam API
        
        self.print_ranking()
    
    def print_ranking(self):
        """Print ranking dork berdasarkan results"""
        
        if not self.results:
            print(f"{C.RED}[!] No results to rank{C.RESET}")
            return
        
        # Sort by results desc
        sorted_dorks = sorted(self.results.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n{C.CYAN}╔══════════════════════════════════════════════════════════════╗{C.RESET}")
        print(f"{C.CYAN}║             DORK RANKING BY RESULTS                           ║{C.RESET}")
        print(f"{C.CYAN}╠══════════════════════════════════════════════════════════════╣{C.RESET}")
        
        for rank, (dork, count) in enumerate(sorted_dorks, 1):
            status = C.GREEN if count > 0 else C.DIM
            
            dork_display = dork[:50] + "..." if len(dork) > 50 else dork
            print(f"{C.CYAN}║ {rank:2d}. {status}{count:5d} results {C.CYAN}| {dork_display:<40s} ║{C.RESET}")
        
        print(f"{C.CYAN}╚══════════════════════════════════════════════════════════════╝{C.RESET}")
        
        # Summary
        total_results = sum(self.results.values())
        best_dork = sorted_dorks[0]
        
        print(f"\n{C.GREEN}[+] Total results: {total_results}{C.RESET}")
        print(f"{C.GREEN}[+] Best dork: {best_dork[0]}{C.RESET}")
        print(f"{C.GREEN}[+] Results: {best_dork[1]}{C.RESET}")
        
        # Save best dorks
        best_dorks = [d for d, c in sorted_dorks if c > 0]
        if best_dorks:
            with open("best-dorks.txt", "w") as f:
                for dork in best_dorks:
                    f.write(f"{dork}\n")
            print(f"{C.GREEN}[+] Saved {len(best_dorks)} best dorks to best-dorks.txt{C.RESET}")

def main():
    parser = argparse.ArgumentParser(
        description="Test dan rank dork queries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
USAGE:

# Test all dorks di FOFA
python3 dork-tester-ranking.py --platform fofa \\
  --email your@email.com --key YOUR_KEY \\
  --file dorks-fofa-broad.txt

# Test all dorks di Shodan
python3 dork-tester-ranking.py --platform shodan \\
  --key YOUR_SHODAN_KEY \\
  --file dorks-shodan-broad.txt

Output:
- Ranked list dorks by results count
- best-dorks.txt (dorks with >0 results)
        """
    )
    
    parser.add_argument("-p", "--platform", default="fofa", 
                       choices=["fofa", "shodan"],
                       help="API platform")
    parser.add_argument("-e", "--email", help="FOFA email")
    parser.add_argument("-k", "--key", help="API key")
    parser.add_argument("-f", "--file", required=True, help="Dork file")
    
    args = parser.parse_args()
    
    if not args.key:
        print(f"{C.RED}[!] API key required!{C.RESET}")
        return
    
    if args.platform == "fofa" and not args.email:
        print(f"{C.RED}[!] FOFA email required!{C.RESET}")
        return
    
    print(f"\n{C.BOLD}{C.BLUE}═══════════════════════════════════════{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}  DORK TESTER & RANKER{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}═══════════════════════════════════════{C.RESET}")
    
    tester = DorkTesterRanker(
        platform=args.platform,
        email=args.email,
        api_key=args.key
    )
    
    tester.test_all_dorks(args.file)
    
    print(f"\n{C.BOLD}{C.BLUE}═══════════════════════════════════════{C.RESET}\n")

if __name__ == "__main__":
    main()
