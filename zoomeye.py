#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
zoomeye-dork-generator-V2.py — ZoomEye Dork Generator (API v2)
Updated untuk API v2 ZoomEye (api.zoomeye.ai)

PERUBAHAN DARI API LAMA:
- Base URL: api.zoomeye.ai (bukan api.zoomeye.org)
- Auth header: "API-KEY: xxx" (bukan "Authorization: JWT xxx")
- Method: POST (bukan GET)
- Query: base64-encoded dalam JSON body (bukan query string biasa)

Setup:
1. Daftar/login di https://www.zoomeye.ai
2. Klik avatar -> Profile -> copy API-KEY
3. Gunakan script ini

API Docs: https://www.zoomeye.ai/doc
"""

import sys
import argparse
import requests
import time
import json
import base64
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
# ZOOMEYE SEARCHER (API v2)
# ══════════════════════════════════════════════════════════════

class ZoomEyeSearcherV2:
    """ZoomEye API v2 Searcher — pakai api.zoomeye.ai, API-KEY, POST"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.all_results = []
        self.base_url = "https://api.zoomeye.ai"
        self.headers = {
            "API-KEY": api_key,
            "Content-Type": "application/json"
        }

        # Session dengan retry logic
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[408, 429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def verify_token(self):
        """Verify API-KEY via /v2/userinfo (GET)"""

        print(f"\n{C.CYAN}[*] Verifying ZoomEye API-KEY (v2)...{C.RESET}")

        try:
            url = f"{self.base_url}/v2/userinfo"
            response = self.session.get(url, headers=self.headers, timeout=(10, 30))

            if response.status_code == 200:
                data = response.json()
                print(f"{C.GREEN}[+] API-KEY valid!{C.RESET}")
                print(f"    Response: {json.dumps(data, indent=2)[:300]}")
                return True
            else:
                print(f"{C.RED}[!] Invalid API-KEY! Status: {response.status_code}{C.RESET}")
                print(f"    Response: {response.text[:300]}")
                return False

        except requests.exceptions.Timeout:
            print(f"{C.RED}[!] Timeout Error{C.RESET}")
            return False
        except requests.exceptions.ConnectionError as e:
            print(f"{C.RED}[!] Connection Error: {str(e)[:100]}{C.RESET}")
            return False
        except Exception as e:
            print(f"{C.RED}[!] Error: {str(e)}{C.RESET}")
            return False

    def search(self, query, page=1, max_pages=5, pagesize=50):
        """Search via /v2/search (POST, qbase64 body)"""

        print(f"\n{C.CYAN}[*] Searching ZoomEye (API v2)...{C.RESET}")
        print(f"    Query: {query[:80]}")

        # Encode query jadi base64 (WAJIB untuk API v2)
        qbase64 = base64.b64encode(query.encode("utf-8")).decode("utf-8")

        page_num = page

        while page_num <= max_pages:
            try:
                url = f"{self.base_url}/v2/search"
                body = {
                    "qbase64": qbase64,
                    "page": page_num,
                    "pagesize": pagesize
                }

                print(f"    Page {page_num}...", end=" ", flush=True)

                response = self.session.post(
                    url,
                    headers=self.headers,
                    json=body,
                    timeout=(10, 30)
                )

                if response.status_code != 200:
                    print(f"\n{C.RED}[!] HTTP {response.status_code}{C.RESET}")
                    print(f"    Response: {response.text[:300]}")
                    break

                data = response.json()

                # API v2 pakai field "code" untuk status, bukan "error"
                if data.get("code") != 60000:
                    print(f"\n{C.RED}[!] API Error: {data.get('message', 'Unknown error')}{C.RESET}")
                    break

                matches = data.get("data", [])

                if not matches:
                    print(f"{C.GREEN}✓ No more results{C.RESET}")
                    break

                for match in matches:
                    try:
                        ip = match.get("ip")
                        port = match.get("port", 2087)
                        service = match.get("service", "")

                        result_data = {
                            "url": f"https://{ip}:{port}",
                            "ip": ip,
                            "port": port,
                            "service": service,
                            "domain": match.get("domain", "")
                        }

                        self.all_results.append(result_data)
                    except Exception:
                        pass

                total = data.get("total", "?")
                print(f"{C.GREEN}✓ {len(matches)} results (Total DB: {total}, Collected: {len(self.all_results)}){C.RESET}")

                page_num += 1
                time.sleep(0.5)

            except requests.exceptions.Timeout:
                print(f"\n{C.YELLOW}[!] Timeout on page {page_num} (retrying handled by session){C.RESET}")
                time.sleep(2)
                continue
            except requests.exceptions.ConnectionError as e:
                print(f"\n{C.RED}[!] Connection error: {str(e)[:80]}{C.RESET}")
                break
            except Exception as e:
                print(f"\n{C.RED}[!] Error: {str(e)[:100]}{C.RESET}")
                break

        return len(self.all_results)

    def deduplicate(self):
        before = len(self.all_results)
        seen_ips = set()
        unique = []
        for r in self.all_results:
            ip = r.get("ip")
            if ip not in seen_ips:
                seen_ips.add(ip)
                unique.append(r)
        self.all_results = unique
        after = len(self.all_results)
        if before > after:
            print(f"{C.YELLOW}[*] Removed {before - after} duplicates{C.RESET}")

    def save_targets(self, filename):
        if not self.all_results:
            print(f"{C.RED}[!] No results to save{C.RESET}")
            return
        with open(filename, "w") as f:
            for r in self.all_results:
                f.write(f"{r['url']}\n")
        print(f"{C.GREEN}[+] Saved {len(self.all_results)} targets to {filename}{C.RESET}")

    def save_detailed(self, filename):
        if not self.all_results:
            print(f"{C.RED}[!] No results to save{C.RESET}")
            return
        data = {
            "timestamp": datetime.now().isoformat(),
            "total": len(self.all_results),
            "results": self.all_results
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"{C.GREEN}[+] Saved detailed data to {filename}{C.RESET}")

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="ZoomEye Dork Generator - API v2 (api.zoomeye.ai)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
SETUP:
1. Login: https://www.zoomeye.ai
2. Avatar -> Profile -> copy API-KEY
3. Keep it safe!

USAGE:

# Test API-KEY
python3 zoomeye-dork-generator-V2.py --key YOUR_API_KEY --verify

# Single query
python3 zoomeye-dork-generator-V2.py --key YOUR_API_KEY \\
  --query 'port:2087 service:cPanel' \\
  -o results.txt

# Batch queries
python3 zoomeye-dork-generator-V2.py --key YOUR_API_KEY \\
  --batch dorks.txt \\
  -o results.txt

CATATAN:
- Argumen sekarang --key (API-KEY), bukan --token (JWT lama)
- Query otomatis di-encode base64 oleh script, tidak perlu manual
        """
    )

    parser.add_argument("-k", "--key", required=True, help="ZoomEye API-KEY (dari zoomeye.ai/profile)")
    parser.add_argument("-q", "--query", help="Single query (plain text, auto base64)")
    parser.add_argument("-b", "--batch", help="Batch file with queries (satu per baris)")
    parser.add_argument("-o", "--output", help="Output file (targets.txt)")
    parser.add_argument("-j", "--json", help="Output JSON file (detailed)")
    parser.add_argument("-p", "--pages", type=int, default=5, help="Max pages per query (default: 5)")
    parser.add_argument("--verify", action="store_true", help="Verify API-KEY only")

    args = parser.parse_args()

    print(f"\n{C.BOLD}{C.BLUE}═══════════════════════════════════════{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}  ZOOMEYE DORK GENERATOR (API v2){C.RESET}")
    print(f"{C.BOLD}{C.BLUE}═══════════════════════════════════════{C.RESET}")

    searcher = ZoomEyeSearcherV2(args.key)

    if args.verify:
        searcher.verify_token()
        return

    if not searcher.verify_token():
        print(f"\n{C.RED}[!] Berhenti karena API-KEY tidak valid.{C.RESET}\n")
        return

    if args.query:
        searcher.search(args.query, max_pages=args.pages)
        searcher.deduplicate()
        if args.output:
            searcher.save_targets(args.output)
        if args.json:
            searcher.save_detailed(args.json)
        print(f"\n{C.GREEN}[+] Total results: {len(searcher.all_results)}{C.RESET}\n")

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
