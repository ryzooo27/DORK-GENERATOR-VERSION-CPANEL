#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
google-dork-generator.py — Google Dorking untuk cPanel Hunt
Completely FREE, Unlimited, Powerful!

Gunakan Google untuk mencari vulnerable servers tanpa API key
"""

import sys
import argparse
import requests
import time
import re
import random
from urllib.parse import quote, urlparse
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════════════════════
# DEPENDENCY CHECK
# ══════════════════════════════════════════════════════════════

def check_dependencies():
    """Check apakah dependencies sudah terinstall"""
    
    try:
        import requests
        import bs4
        return True
    except ImportError as e:
        print(f"\n[ERROR] Missing dependency: {e}")
        print("\nInstall dengan command:")
        print("  pip install requests beautifulsoup4")
        print("\nAtau untuk Python 3:")
        print("  pip3 install requests beautifulsoup4\n")
        sys.exit(1)

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
        # Gunakan user-agent browser real
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
        
        print(f"{C.YELLOW}[*] Searching: {dork[:60]}...{C.RESET}", end=" ", flush=True)
        
        try:
            # Construct Google search URL
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
            
            # Check jika response kosong
            if not response.content or len(response.content) == 0:
                print(f"{C.RED}✗ Empty response{C.RESET}")
                return 0
            
            # Parse HTML dengan error handling
            try:
                soup = BeautifulSoup(response.content, 'html.parser')
            except Exception as parse_error:
                print(f"{C.RED}✗ Parse error: {str(parse_error)[:30]}{C.RESET}")
                return 0
            
            # Extract URLs dari search results dengan error handling
            try:
                links = soup.find_all('a', href=True)
            except Exception as e:
                print(f"{C.RED}✗ Find error: {str(e)[:30]}{C.RESET}")
                return 0
            
            if not links:
                print(f"{C.DIM}✗ No links found{C.RESET}")
                return 0
            
            found = 0
            
            for link in links:
                try:
                    url = link.get('href', '')
                    if not url:
                        continue
                    
                    # Filter out Google's own links
                    if url.startswith('/url?q='):
                        actual_url = url.split('/url?q=')[1].split('&')[0]
                        
                        # Skip Google, Wikipedia, etc
                        if any(skip in actual_url for skip in ['google.', 'wikipedia.', 'youtube.', 'reddit.']):
                            continue
                        
                        # Extract IP:port atau domain jika matches pattern
                        if ':2087' in actual_url or '2087' in actual_url:
                            self.all_results.append(actual_url)
                            found += 1
                            
                            if found >= max_results:
                                break
                except Exception as e:
                    # Skip individual link yang error
                    continue
            
            if found > 0:
                print(f"{C.GREEN}✓ {found} results{C.RESET}")
            else:
                print(f"{C.DIM}✗ 0 results{C.RESET}")
            
            return found
        
        except requests.exceptions.Timeout:
            print(f"{C.YELLOW}✗ Timeout{C.RESET}")
            return 0
        except requests.exceptions.ConnectionError:
            print(f"{C.YELLOW}✗ Connection error{C.RESET}")
            return 0
        except Exception as e:
            print(f"{C.RED}✗ Error: {str(e)[:40]}{C.RESET}")
            return 0
    
    def search_all_dorks(self, dork_list):
        """Search semua dorks dengan random delay"""
        
        for i, dork in enumerate(dork_list, 1):
            self.search_google(dork, max_results=5)
            
            # Random delay antara 3-7 detik untuk menghindari rate limiting
            if i < len(dork_list):
                delay = random.uniform(3, 7)
                time.sleep(delay)
        
        return len(self.all_results)
    
    def deduplicate(self):
        """Remove duplicates"""
        
        before = len(self.all_results)
        self.all_results = list(set(self.all_results))
        after = len(self.all_results)
        
        if before > after:
            print(f"{C.YELLOW}[*] Removed {before - after} duplicates{C.RESET}")
    
    def extract_targets(self):
        """Extract targets dari URLs dengan multiple format support"""
        
        targets = set()
        
        for url in self.all_results:
            try:
                # Pattern 1: IP:port format
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)[:/]+(2087)', url)
                if match:
                    targets.add(f"https://{match.group(1)}:{match.group(2)}")
                    continue
                
                # Pattern 2: Domain dengan port di URL
                if ':2087' in url:
                    # Coba parse URL untuk mendapatkan domain dengan port
                    try:
                        parsed = urlparse(url)
                        if parsed.netloc:
                            targets.add(f"https://{parsed.netloc}")
                        else:
                            # Fallback: ambil sebelum :2087
                            domain = url.split(':2087')[0]
                            if 'http' in domain:
                                domain = domain.split('://')[-1]
                            targets.add(f"https://{domain}:2087")
                    except:
                        # Fallback sederhana
                        domain_part = url.split(':2087')[0]
                        if domain_part:
                            targets.add(domain_part + ':2087')
                    continue
                
                # Pattern 3: URL lengkap (https://domain)
                if url.startswith('http'):
                    targets.add(url)
                    
            except Exception as e:
                # Skip URL yang gagal di-parse
                continue
        
        return sorted(list(targets))
    
    def save_targets(self, filename):
        """Save targets ke file"""
        
        targets = self.extract_targets()
        
        if not targets:
            print(f"{C.RED}[!] No targets to save{C.RESET}")
            return
        
        try:
            with open(filename, "w", encoding='utf-8') as f:
                for target in targets:
                    f.write(f"{target}\n")
            
            print(f"{C.GREEN}[+] Saved {len(targets)} targets to {filename}{C.RESET}")
        except Exception as e:
            print(f"{C.RED}[!] Error saving file: {e}{C.RESET}")
    
    def save_urls(self, filename):
        """Save raw URLs"""
        
        if not self.all_results:
            print(f"{C.RED}[!] No results to save{C.RESET}")
            return
        
        try:
            with open(filename, "w", encoding='utf-8') as f:
                for url in sorted(self.all_results):
                    f.write(f"{url}\n")
            
            print(f"{C.GREEN}[+] Saved {len(self.all_results)} URLs to {filename}{C.RESET}")
        except Exception as e:
            print(f"{C.RED}[!] Error saving file: {e}{C.RESET}")

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    # Check dependencies dulu sebelum parsing arguments
    check_dependencies()
    
    parser = argparse.ArgumentParser(
        description="Google Dorking untuk cPanel Hunt - Completely FREE!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
USAGE:

# Basic dorks
python3 google-dork-generator.py --type basic

# Specific dorks (more targeted)
python3 google-dork-generator.py --type specific -o results.txt

# Regional dorks (Indonesia, Singapore, etc)
python3 google-dork-generator.py --type regional -o regional-results.txt

# Advanced dorks
python3 google-dork-generator.py --type advanced -o advanced-results.txt

# Custom dork
python3 google-dork-generator.py --dork 'inurl:2087 intitle:WHM' -o custom.txt

DORK TYPES:
- basic     : Common dorks
- specific  : Port 2087 + cPanel specific
- regional  : Asia countries (ID, SG, MY, TH, etc)
- advanced  : Advanced dork techniques

EXAMPLE DORKS:
- inurl:2087
- intitle:"WHM Login"
- intext:"Server Administrator" port:2087
- inurl:2087 site:.id (Indonesia only)
- cPanel inurl:2087
        """
    )
    
    parser.add_argument("-t", "--type", default="basic",
                       choices=["basic", "specific", "regional", "advanced"],
                       help="Dork type")
    parser.add_argument("-d", "--dork", help="Custom dork query")
    parser.add_argument("-o", "--output", help="Output file (targets)")
    parser.add_argument("-u", "--urls", help="Output file (raw URLs)")
    parser.add_argument("-l", "--list", action="store_true", help="List all dorks")
    
    args = parser.parse_args()
    
    print(f"\n{C.BOLD}{C.BLUE}═══════════════════════════════════════{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}  GOOGLE DORKING - cPanel Hunt{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}═══════════════════════════════════════{C.RESET}\n")
    
    searcher = GoogleDorkSearcher()
    
    # List dorks
    if args.list:
        print(f"\n{C.CYAN}[*] Basic Dorks:{C.RESET}")
        for i, dork in enumerate(searcher.generate_dorks("basic"), 1):
            print(f"  {i:2d}. {dork}")
        
        print(f"\n{C.CYAN}[*] Specific Dorks:{C.RESET}")
        for i, dork in enumerate(searcher.generate_dorks("specific"), 1):
            print(f"  {i:2d}. {dork}")
        
        print(f"\n{C.CYAN}[*] Regional Dorks:{C.RESET}")
        for i, dork in enumerate(searcher.generate_dorks("regional"), 1):
            print(f"  {i:2d}. {dork}")
        
        print(f"\n{C.CYAN}[*] Advanced Dorks:{C.RESET}")
        for i, dork in enumerate(searcher.generate_dorks("advanced"), 1):
            print(f"  {i:2d}. {dork}")
        
        print()
        return
    
    # Search
    if args.dork:
        # Custom dork
        print(f"{C.CYAN}[*] Searching custom dork...{C.RESET}\n")
        searcher.search_google(args.dork, max_results=20)
    else:
        # Preset dorks
        print(f"{C.CYAN}[*] Using {args.type} dorks...{C.RESET}\n")
        dorks = searcher.generate_dorks(args.type)
        searcher.search_all_dorks(dorks)
    
    print()
    searcher.deduplicate()
    
    # Save
    if args.output:
        searcher.save_targets(args.output)
    
    if args.urls:
        searcher.save_urls(args.urls)
    
    print(f"\n{C.GREEN}[+] Total results: {len(searcher.all_results)}{C.RESET}\n")

if __name__ == "__main__":
    main()
