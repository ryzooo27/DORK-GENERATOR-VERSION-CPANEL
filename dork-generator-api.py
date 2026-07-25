#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

dork-generator-api.py — FOFA/Shodan Dork Generator WITH API Integration

Auto-generate dorks + API search + Auto-extract results

Features:
✅ FOFA API integration (auto-search)
✅ Shodan API integration (auto-search)
✅ Pagination handling (get all results)
✅ Rate limit handling
✅ Error recovery
✅ Batch processing
✅ Result deduplication
✅ Export to targets.txt (ready for exploit)

Usage:
  python3 dork-generator-api.py --platform fofa --email your@email.com --key YOUR_KEY --version 11.126.0
  python3 dork-generator-api.py --platform fofa --key YOUR_KEY --search-all -o all-results.txt
  python3 dork-generator-api.py --platform shodan --key YOUR_KEY --version 11.126.0 --region Indonesia
  python3 dork-generator-api.py --batch-file dorks.txt --platform fofa --key YOUR_KEY

"""

import sys
import argparse
import requests
import base64
import time
import json
from datetime import datetime
from collections import defaultdict

# ══════════════════════════════════════════════════════════════

# VULNERABLE VERSIONS DATABASE

# ══════════════════════════════════════════════════════════════

VULNERABLE_VERSIONS = {
    "11": {
        "110": {"branch": "11.110", "start": "11.110.0.0", "end": "11.110.0.96", "patched": "11.110.0.97"},
        "118": {"branch": "11.118", "start": "11.118.0.0", "end": "11.118.0.62", "patched": "11.118.0.63"},
        "126": {"branch": "11.126", "start": "11.126.0.0", "end": "11.126.0.53", "patched": "11.126.0.54", "note": "MOST COMMON"},
        "132": {"branch": "11.132", "start": "11.132.0.0", "end": "11.132.0.28", "patched": "11.132.0.29"},
        "134": {"branch": "11.134", "start": "11.134.0.0", "end": "11.134.0.19", "patched": "11.134.0.20"},
        "136": {"branch": "11.136", "start": "11.136.0.0", "end": "11.136.0.4", "patched": "11.136.0.5"},
    },
    "12": {
        "1200": {"branch": "12.0.0", "start": "12.0.0.0", "end": "12.0.0.4", "patched": "12.0.0.5", "note": "ASSUMED"},
        "1201": {"branch": "12.1.0", "start": "12.1.0.0", "end": "12.1.0.99", "patched": "12.1.1.0", "note": "ASSUMED"},
    }
}

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

# DORK GENERATOR WITH API

# ══════════════════════════════════════════════════════════════

class DorkGeneratorAPI:
    """Generate dorks + API search + Extract results"""
    
    def __init__(self, platform="fofa", email=None, api_key=None):
        self.platform = platform.lower()
        self.email = email
        self.api_key = api_key
        self.all_servers = []
    
    # ───────────────────────────────────────────────────────────
    # DORK GENERATION
    # ───────────────────────────────────────────────────────────
    
    def generate_dork(self, version, region=None, org=None):
        """Generate dork string"""
        
        if not version.startswith("cPanel/"):
            version = f"cPanel/{version}"
        
        if self.platform == "fofa":
            dork = f'port="2087" && banner="{version}" && title="WHM Login"'
            
            if region:
                dork += f' && region="{region}"'
            
            if org:
                dork += f' && org="{org}"'
            
            dork += ' && !(http.status="401")'
            
            return dork
        
        elif self.platform == "shodan":
            dork = f'port:2087 title:"WHM Login" "{version}"'
            
            if region:
                dork += f' country:"{region}"'
            
            return dork
        
        return None
    
    # ───────────────────────────────────────────────────────────
    # FOFA API SEARCH
    # ───────────────────────────────────────────────────────────
    
    def fofa_search(self, dork, max_pages=100):
        """Search FOFA menggunakan API"""
        
        if not self.email or not self.api_key:
            print(f"{C.RED}[!] Error: Need FOFA email dan API key!{C.RESET}")
            return []
        
        print(f"\n{C.CYAN}[*] Searching FOFA untuk: {dork[:70]}...{C.RESET}")
        
        servers = []
        page = 1
        
        while page <= max_pages:
            try:
                # Encode dork
                dork_encoded = base64.b64encode(dork.encode()).decode()
                
                # API call
                url = "https://fofa.info/api/v1/search/all"
                params = {
                    "email": self.email,
                    "key": self.api_key,
                    "qbase64": dork_encoded,
                    "page": page,
                    "size": 10000,
                    "full": "false"
                }
                
                response = requests.get(url, params=params, timeout=30)
                
                # Handle rate limit
                if response.status_code == 429:
                    print(f"{C.YELLOW}[!] Rate limited! Waiting 60 seconds...{C.RESET}")
                    time.sleep(60)
                    continue
                
                if response.status_code != 200:
                    print(f"{C.RED}[!] Error: HTTP {response.status_code}{C.RESET}")
                    break
                
                data = response.json()
                results = data.get('results', [])
                
                # No more results
                if not results:
                    print(f"{C.GREEN}[+] Reached end at page {page}{C.RESET}")
                    break
                
                # Extract servers
                for result in results:
                    ip, port = result[0], result[1]
                    server_url = f"https://{ip}:{port}"
                    servers.append(server_url)
                
                print(f"{C.GREEN}[+] Page {page}: {len(results)} servers (Total: {len(servers)}){C.RESET}")
                
                page += 1
                time.sleep(1)  # Rate limit safe
            
            except requests.exceptions.Timeout:
                print(f"{C.YELLOW}[!] Timeout! Retrying page {page}...{C.RESET}")
                time.sleep(5)
                continue
            
            except Exception as e:
                print(f"{C.RED}[!] Error: {str(e)[:100]}{C.RESET}")
                break
        
        print(f"\n{C.GREEN}[+] FOFA search complete! Total: {len(servers)} servers{C.RESET}")
        
        self.all_servers = servers
        return servers
    
    # ───────────────────────────────────────────────────────────
    # SHODAN API SEARCH
    # ───────────────────────────────────────────────────────────
    
    def shodan_search(self, dork):
        """Search Shodan menggunakan API"""
        
        if not self.api_key:
            print(f"{C.RED}[!] Error: Need Shodan API key!{C.RESET}")
            return []
        
        print(f"\n{C.CYAN}[*] Searching Shodan untuk: {dork[:70]}...{C.RESET}")
        
        servers = []
        page = 1
        
        try:
            while True:
                url = "https://api.shodan.io/shodan/host/search"
                params = {
                    "key": self.api_key,
                    "query": dork,
                    "page": page,
                }
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code != 200:
                    print(f"{C.RED}[!] Error: HTTP {response.status_code}{C.RESET}")
                    break
                
                data = response.json()
                matches = data.get('matches', [])
                
                if not matches:
                    print(f"{C.GREEN}[+] Reached end at page {page}{C.RESET}")
                    break
                
                for match in matches:
                    ip = match.get('ip_str')
                    port = match.get('port', 2087)
                    server_url = f"https://{ip}:{port}"
                    servers.append(server_url)
                
                print(f"{C.GREEN}[+] Page {page}: {len(matches)} servers (Total: {len(servers)}){C.RESET}")
                
                page += 1
                time.sleep(2)  # Shodan rate limit
        
        except Exception as e:
            print(f"{C.RED}[!] Error: {str(e)[:100]}{C.RESET}")
        
        print(f"\n{C.GREEN}[+] Shodan search complete! Total: {len(servers)} servers{C.RESET}")
        
        self.all_servers = servers
        return servers
    
    # ───────────────────────────────────────────────────────────
    # RESULT PROCESSING
    # ───────────────────────────────────────────────────────────
    
    def deduplicate(self):
        """Remove duplicate servers"""
        
        before = len(self.all_servers)
        self.all_servers = list(set(self.all_servers))
        after = len(self.all_servers)
        
        removed = before - after
        
        if removed > 0:
            print(f"{C.YELLOW}[*] Removed {removed} duplicates{C.RESET}")
    
    def save_targets(self, filename):
        """Save servers ke file (format: https://IP:Port)"""
        
        if not self.all_servers:
            print(f"{C.RED}[!] No servers to save!{C.RESET}")
            return
        
        try:
            with open(filename, "w") as f:
                for server in sorted(self.all_servers):
                    f.write(f"{server}\n")
            
            print(f"{C.GREEN}[+] Saved {len(self.all_servers)} targets to {filename}{C.RESET}")
        
        except Exception as e:
            print(f"{C.RED}[!] Error saving file: {e}{C.RESET}")
    
    def save_json(self, filename):
        """Save servers ke JSON format"""
        
        if not self.all_servers:
            print(f"{C.RED}[!] No servers to save!{C.RESET}")
            return
        
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "platform": self.platform,
                "total": len(self.all_servers),
                "servers": sorted(self.all_servers)
            }
            
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            
            print(f"{C.GREEN}[+] Saved JSON to {filename}{C.RESET}")
        
        except Exception as e:
            print(f"{C.RED}[!] Error saving JSON: {e}{C.RESET}")
    
    def print_stats(self):
        """Print statistics"""
        
        print(f"\n{C.CYAN}╔════════════════════════════════════════╗{C.RESET}")
        print(f"{C.CYAN}║     SEARCH RESULTS STATISTICS           ║{C.RESET}")
        print(f"{C.CYAN}╠════════════════════════════════════════╣{C.RESET}")
        print(f"{C.CYAN}║ Platform:     {self.platform.upper():25s} ║{C.RESET}")
        print(f"{C.CYAN}║ Total found:  {len(self.all_servers):25d} ║{C.RESET}")
        print(f"{C.CYAN}║ Status:       {C.GREEN}Ready for exploit{C.RESET}{C.CYAN}      ║{C.RESET}")
        print(f"{C.CYAN}╚════════════════════════════════════════╝{C.RESET}")

# ══════════════════════════════════════════════════════════════

# HELPER FUNCTIONS

# ══════════════════════════════════════════════════════════════

def get_all_versions():
    """Get semua vulnerable versions"""
    
    versions = []
    
    for major in sorted(VULNERABLE_VERSIONS.keys()):
        for branch_key, info in sorted(VULNERABLE_VERSIONS[major].items()):
            versions.append(info.get('branch', 'N/A'))
    
    return versions

# ══════════════════════════════════════════════════════════════

# MAIN

# ══════════════════════════════════════════════════════════════

def main():
    
    parser = argparse.ArgumentParser(
        description="FOFA/Shodan Dork Generator WITH API Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
COMMANDS:

# Search single version
python3 dork-generator-api.py --platform fofa --email your@email.com --key YOUR_KEY --version 11.126.0

# Search dengan region filter
python3 dork-generator-api.py --platform fofa --key YOUR_KEY --version 11.126.0 --region Asia

# Search semua vulnerable versions
python3 dork-generator-api.py --platform fofa --key YOUR_KEY --search-all -o all-results.txt

# Shodan search
python3 dork-generator-api.py --platform shodan --key YOUR_KEY --version 11.126.0

# Batch search dari file
python3 dork-generator-api.py --batch-file dorks.txt --platform fofa --key YOUR_KEY -o results.txt

# List semua vulnerable versions
python3 dork-generator-api.py --list

# Export as JSON
python3 dork-generator-api.py --platform fofa --key YOUR_KEY --version 11.126.0 --json -o results.json
        """
    )
    
    parser.add_argument("-p", "--platform", default="fofa", 
                       choices=["fofa", "shodan"],
                       help="API platform (fofa/shodan)")
    parser.add_argument("-e", "--email", help="FOFA email (required untuk FOFA)")
    parser.add_argument("-k", "--key", help="API key (FOFA atau Shodan)")
    parser.add_argument("-v", "--version", help="cPanel version (e.g., 11.126.0)")
    parser.add_argument("-r", "--region", help="Region filter (e.g., Asia, Indonesia)")
    parser.add_argument("--org", help="Organization filter (FOFA only)")
    parser.add_argument("-o", "--output", help="Output file untuk results")
    parser.add_argument("--json", action="store_true", help="Export as JSON")
    parser.add_argument("--search-all", action="store_true", help="Search semua vulnerable versions")
    parser.add_argument("--batch-file", help="Batch file dengan dorks (satu per line)")
    parser.add_argument("-l", "--list", action="store_true", help="List semua vulnerable versions")
    
    args = parser.parse_args()
    
    # List versions
    if args.list:
        versions = get_all_versions()
        print(f"\n{C.BOLD}{C.BLUE}VULNERABLE cPanel VERSIONS{C.RESET}\n")
        for i, v in enumerate(versions, 1):
            print(f"  {i:2d}. {v}")
        print()
        return
    
    # Check API key
    if not args.key:
        print(f"{C.RED}[!] Error: API key required! Use --key{C.RESET}")
        return
    
    # Initialize generator
    gen = DorkGeneratorAPI(platform=args.platform, email=args.email, api_key=args.key)
    
    # Single version search
    if args.version:
        print(f"\n{C.BOLD}{C.BLUE}SEARCHING SINGLE VERSION{C.RESET}")
        
        dork = gen.generate_dork(args.version, region=args.region, org=args.org)
        print(f"\n{C.YELLOW}Generated dork:{C.RESET}")
        print(f"{C.CYAN}{dork}{C.RESET}")
        
        # Search
        if args.platform == "fofa":
            gen.fofa_search(dork)
        elif args.platform == "shodan":
            gen.shodan_search(dork)
        
        # Deduplicate
        gen.deduplicate()
        
        # Save
        if args.output:
            if args.json:
                gen.save_json(args.output)
            else:
                gen.save_targets(args.output)
        
        # Stats
        gen.print_stats()
    
    # Search all versions
    elif args.search_all:
        print(f"\n{C.BOLD}{C.BLUE}SEARCHING ALL VULNERABLE VERSIONS{C.RESET}")
        
        versions = get_all_versions()
        
        for version in versions:
            dork = gen.generate_dork(version, region=args.region)
            
            if args.platform == "fofa":
                gen.fofa_search(dork, max_pages=50)
            elif args.platform == "shodan":
                gen.shodan_search(dork)
        
        # Deduplicate
        gen.deduplicate()
        
        # Save
        if args.output:
            if args.json:
                gen.save_json(args.output)
            else:
                gen.save_targets(args.output)
        
        # Stats
        gen.print_stats()
    
    # Batch search
    elif args.batch_file:
        print(f"\n{C.BOLD}{C.BLUE}BATCH SEARCH FROM FILE{C.RESET}")
        
        try:
            with open(args.batch_file, "r") as f:
                dorks = [line.strip() for line in f if line.strip()]
            
            print(f"{C.GREEN}[+] Loaded {len(dorks)} dorks from {args.batch_file}{C.RESET}")
            
            for dork in dorks:
                if args.platform == "fofa":
                    gen.fofa_search(dork, max_pages=20)
                elif args.platform == "shodan":
                    gen.shodan_search(dork)
            
            # Deduplicate
            gen.deduplicate()
            
            # Save
            if args.output:
                if args.json:
                    gen.save_json(args.output)
                else:
                    gen.save_targets(args.output)
            
            # Stats
            gen.print_stats()
        
        except Exception as e:
            print(f"{C.RED}[!] Error: {e}{C.RESET}")
    
    else:
        parser.print_help()
        print(f"\n{C.YELLOW}Tip: Use --list untuk lihat semua vulnerable versions{C.RESET}\n")

if __name__ == "__main__":
    main()
