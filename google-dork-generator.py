#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
google-dork-generator-v2.py — Google Dorking untuk cPanel Hunt
BATCH MODE INCLUDED - Run semua dorks sekaligus!

Completely FREE, Unlimited, Powerful!
"""

import sys
import argparse
import requests
import time
import re
from urllib.parse import quote
from bs4 import BeautifulSoup

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
# GOOGLE DORKING
# ══════════════════════════════════════════════════════════════

class GoogleDorkSearcher:
    """Google Dorking untuk mencari cPanel servers"""
    
    def __init__(self):
        self.all_results = []
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def generate_dorks(self, dork_type="basic"):
        """Generate Google dorks untuk cPanel"""
        
        if dork_type == "basic":
            return [
                'inurl:2087',
                'port:2087',
                'inurl:"2087" cPanel',
                'intitle:"WHM Login"',
                'intitle:"cPanel Login"',
                'intext:"WHM - WebHost Manager"',
                'intext:"Server Administrator"',
                '"WebHost Manager" port 2087',
                'cPanel inurl:2087',
                'WHM Login inurl:2087',
            ]
        
        elif dork_type == "specific":
            return [
                'inurl:2087 intitle:WHM',
                'inurl:2087 intitle:cPanel',
                'inurl:2087 "Server Administrator"',
                'inurl:2087 "WebHost Manager"',
                '"cPanel/11" port:2087',
                '"cPanel/12" port:2087',
                'inurl:2087 body:"WHM Login"',
                'site:*.com inurl:2087',
                'inurl:2087 country:ID',
                'inurl:2087 Indonesia',
            ]
        
        elif dork_type == "regional":
            return [
                'cPanel site:.id',
                'WHM site:.id',
                'inurl:2087 site:.id',
                'cPanel site:.sg',
                'cPanel site:.my',
                'cPanel site:.th',
                'cPanel site:.ph',
                'cPanel site:.jp',
                '"WHM Login" site:.id',
                'inurl:2087 site:.sg',
            ]
        
        else:  # advanced
            return [
                'inurl:2087 status:200',
                'inurl:2087 "HTTP/1.1 200"',
                'cache:cPanel 2087',
                'related:cpanel.net port:2087',
                'filetype:html cPanel 2087',
                'inurl:2087 -forum -blog -news',
                'inurl:2087 -localhost -127.0.0.1',
                'inurl:2087 ext:html',
                'inurl:2087 "Powered by cPanel"',
                'inurl:2087 "Copyright cPanel"',
            ]
    
    def search_google(self, dork, max_results=10):
        """Search Google dengan dork query"""
        
        try:
            search_url = f"https://www.google.com/search?q={quote(dork)}"
            
            response = self.session.get(
                search_url,
                headers=self.headers,
                timeout=10,
                allow_redirects=True
            )
            
            if response.status_code != 200:
                print(f"{C.RED}✗ HTTP {response.status_code}{C.RESET}")
                return 0
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)
            found = 0
            
            for link in links:
                url = link['href']
                
                if url.startswith('/url?q='):
                    actual_url = url.split('/url?q=')[1].split('&')[0]
                    
                    if any(skip in actual_url for skip in ['google.', 'wikipedia.', 'youtube.', 'reddit.']):
                        continue
                    
                    if ':2087' in actual_url or '2087' in actual_url:
                        self.all_results.append(actual_url)
                        found += 1
                        
                        if found >= max_results:
                            break
            
            if found > 0:
                print(f"{C.YELLOW}[*]{C.RESET} {dork[:60]:<60} → {C.GREEN}{found} results{C.RESET}")
            else:
                print(f"{C.YELLOW}[*]{C.RESET} {dork[:60]:<60} → {C.DIM}0 results{C.RESET}")
            
            return found
        
        except requests.exceptions.Timeout:
            print(f"{C.YELLOW}[*]{C.RESET} {dork[:60]:<60} → {C.RED}Timeout{C.RESET}")
            return 0
        except Exception as e:
            print(f"{C.YELLOW}[*]{C.RESET} {dork[:60]:<60} → {C.RED}Error{C.RESET}")
            return 0
    
    def search_all_dorks(self, dork_list):
        """Search semua dorks"""
        
        total = len(dork_list)
        
        for i, dork in enumerate(dork_list, 1):
            self.search_google(dork, max_results=5)
            time.sleep(1)  # Rate limit safe
        
        return len(self.all_results)
    
    def load_dorks_from_file(self, filepath):
        """Load dorks dari file"""
        
        try:
            with open(filepath, 'r') as f:
                dorks = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            return dorks
        except FileNotFoundError:
            print(f"{C.RED}[!] File not found: {filepath}{C.RESET}")
            return None
        except Exception as e:
            print(f"{C.RED}[!] Error reading file: {e}{C.RESET}")
            return None
    
    def deduplicate(self):
        """Remove duplicates"""
        
        before = len(self.all_results)
        self.all_results = list(set(self.all_results))
        after = len(self.all_results)
        
        if before > after:
            print(f"\n{C.YELLOW}[*] Removed {before - after} duplicates{C.RESET}")
    
    def extract_targets(self):
        """Extract targets dari URLs"""
        
        targets = []
        
        for url in self.all_results:
            match = re.search(r'(\d+\.\d+\.\d+\.\d+)[:/]+(2087)', url)
            if match:
                targets.append(f"https://{match.group(1)}:{match.group(2)}")
                continue
            
            if ':2087' in url:
                targets.append(url.split(':2087')[0] + ':2087')
                continue
            
            if 'http' in url:
                targets.append(url)
        
        return list(set(targets))
    
    def save_targets(self, filename):
        """Save targets ke file"""
        
        targets = self.extract_targets()
        
        if not targets:
            print(f"{C.RED}[!] No targets to save{C.RESET}")
            return
        
        try:
            with open(filename, "w") as f:
                for target in sorted(targets):
                    f.write(f"{target}\n")
            
            print(f"{C.GREEN}[+] Saved {len(targets)} targets to {filename}{C.RESET}")
        except Exception as e:
            print(f"{C.RED}[!] Error: {e}{C.RESET}")
    
    def save_urls(self, filename):
        """Save raw URLs"""
        
        if not self.all_results:
            print(f"{C.RED}[!] No results to save{C.RESET}")
            return
        
        try:
            with open(filename, "w") as f:
                for url in sorted(self.all_results):
                    f.write(f"{url}\n")
            
            print(f"{C.GREEN}[+] Saved {len(self.all_results)} URLs to {filename}{C.RESET}")
        except Exception as e:
            print(f"{C.RED}[!] Error: {e}{C.RESET}")

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Google Dorking untuk cPanel Hunt - BATCH MODE ENABLED",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
USAGE EXAMPLES:

# LIST all dorks
  python3 google-dork-generator-v2.py --list

# BASIC dorks (preset)
  python3 google-dork-generator-v2.py --type basic

# SPECIFIC dorks
  python3 google-dork-generator-v2.py --type specific -o results.txt

# REGIONAL dorks (Asia)
  python3 google-dork-generator-v2.py --type regional -o regional.txt

# ADVANCED dorks
  python3 google-dork-generator-v2.py --type advanced -o advanced.txt

# ★ BATCH MODE - RUN ALL DORKS FROM FILE ★
  python3 google-dork-generator-v2.py --batch GOOGLE-DORKS-COMPREHENSIVE.txt -o all-results.txt

# CUSTOM dork
  python3 google-dork-generator-v2.py --dork 'inurl:2087 intitle:WHM' -o custom.txt

# Save raw URLs too
  python3 google-dork-generator-v2.py --batch GOOGLE-DORKS-COMPREHENSIVE.txt -o targets.txt -u urls.txt

DORK TYPES:
  basic     - Common dorks (~10 queries)
  specific  - Port 2087 + cPanel specific (~10 queries)
  regional  - Asia countries ID/SG/MY/TH/etc (~10 queries)
  advanced  - Advanced techniques (~10 queries)

BATCH MODE:
  --batch FILE.txt    → Load dorks dari file dan run semuanya
  Supports comments (lines starting with #)
  Supports empty lines

EXAMPLES:
  python3 google-dork-generator-v2.py --batch dork-google.txt -o results.txt
  python3 google-dork-generator-v2.py --batch GOOGLE-DORKS-COMPREHENSIVE.txt -o all.txt
        """
    )
    
    parser.add_argument("-t", "--type", default="basic",
                       choices=["basic", "specific", "regional", "advanced"],
                       help="Dork type (preset)")
    parser.add_argument("-d", "--dork", 
                       help="Custom single dork query")
    parser.add_argument("-b", "--batch", 
                       help="Batch file dengan multiple dorks (one per line)")
    parser.add_argument("-o", "--output", 
                       help="Output file (targets/IP:port)")
    parser.add_argument("-u", "--urls", 
                       help="Output file (raw URLs)")
    parser.add_argument("-l", "--list", action="store_true", 
                       help="List all available dorks")
    
    args = parser.parse_args()
    
    print(f"\n{C.BOLD}{C.BLUE}╔═══════════════════════════════════════╗{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}║  GOOGLE DORKING - cPanel Hunt v2      ║{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}║  Batch Mode Enabled ✓                 ║{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}╚═══════════════════════════════════════╝{C.RESET}\n")
    
    searcher = GoogleDorkSearcher()
    
    # LIST mode
    if args.list:
        print(f"{C.CYAN}[*] Available Dork Categories:{C.RESET}\n")
        
        print(f"{C.YELLOW}BASIC DORKS:{C.RESET}")
        for i, dork in enumerate(searcher.generate_dorks("basic"), 1):
            print(f"  {i:2d}. {dork}")
        
        print(f"\n{C.YELLOW}SPECIFIC DORKS:{C.RESET}")
        for i, dork in enumerate(searcher.generate_dorks("specific"), 1):
            print(f"  {i:2d}. {dork}")
        
        print(f"\n{C.YELLOW}REGIONAL DORKS:{C.RESET}")
        for i, dork in enumerate(searcher.generate_dorks("regional"), 1):
            print(f"  {i:2d}. {dork}")
        
        print(f"\n{C.YELLOW}ADVANCED DORKS:{C.RESET}")
        for i, dork in enumerate(searcher.generate_dorks("advanced"), 1):
            print(f"  {i:2d}. {dork}")
        
        print()
        return
    
    # BATCH MODE
    if args.batch:
        dorks = searcher.load_dorks_from_file(args.batch)
        if not dorks:
            return
        
        print(f"{C.GREEN}[+] Loaded {len(dorks)} dorks from {args.batch}{C.RESET}")
        print(f"{C.CYAN}[*] Starting batch search (this may take a few minutes)...{C.RESET}\n")
        
        searcher.search_all_dorks(dorks)
    
    # CUSTOM DORK mode
    elif args.dork:
        print(f"{C.CYAN}[*] Searching custom dork...{C.RESET}\n")
        searcher.search_google(args.dork, max_results=20)
    
    # PRESET DORKS mode
    else:
        print(f"{C.CYAN}[*] Using {args.type} dorks...{C.RESET}\n")
        dorks = searcher.generate_dorks(args.type)
        searcher.search_all_dorks(dorks)
    
    print()
    searcher.deduplicate()
    
    # SAVE results
    if args.output:
        searcher.save_targets(args.output)
    
    if args.urls:
        searcher.save_urls(args.urls)
    
    print(f"\n{C.GREEN}[✓] Total unique results: {len(searcher.all_results)}{C.RESET}\n")

if __name__ == "__main__":
    main()
