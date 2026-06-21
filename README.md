# Ethical Hacking Simulation

A Python-based ethical hacking simulation built for a cybersecurity course. Four attacks are launched from a Kali Linux VM against a vulnerable Ubuntu victim VM, with Wazuh SIEM detecting and alerting on every attack in real time.

---

## Environment

| Machine | OS | IP | Role |
| --- | --- | --- | --- |
| Attacker | Kali Linux | 172.22.225.120 | Launches attacks via Flask GUI |
| Victim | Ubuntu 22.04 | 172.22.229.213 | Runs SSH, Apache, MySQL, Wazuh |
| Host | Windows 11 Pro | — | Hyper-V hypervisor |

Both VMs run on the **Default Switch** in Hyper-V — fully isolated from any external network.

---

## Attacks Simulated

| Attack | Module | MITRE ATT&CK | Detected By |
| --- | --- | --- | --- |
| SSH Brute Force | `attack.ipynb` + Flask tab | T1110.001 | Wazuh rule 5760 (built-in) |
| Port Scanner | `port_scanner.py` + Flask tab | T1046 | Wazuh Remote Services detection |
| Web Login Brute Force | `web_bruteforce.py` + Flask tab | T1110.001 | Custom rules 100002 + 100003 |
| SQL Injection | `sqli_attack.py` + Flask tab | T1190 | Wazuh rules 31103, 31164 (built-in) |

---

## Project Structure

```text
cybersecurity/
│
├── attacker/
│   ├── app.py                    # Flask GUI — four-tab attacker dashboard
│   ├── port_scanner.py           # TCP Connect scanner (65,535 ports, threading, banner grab)
│   ├── web_bruteforce.py         # HTTP POST login brute force
│   ├── sqli_attack.py            # SQL injection (login bypass + UNION extraction)
│   ├── attack.ipynb              # Jupyter notebook walkthrough
│   ├── templates/
│   │   └── index.html            # Dashboard UI
│   └── wordlists/
│       └── common_passwords.txt  # Password wordlist
│
├── victim-webapp/                # PHP source files for the vulnerable web app
│   ├── login_basic.php           # Hardcoded login — target for web brute force
│   ├── login_sqli.php            # MySQL login — vulnerable to SQL injection
│   ├── search.php                # Vulnerable search page — UNION extraction target
│   └── dashboard.php             # Protected page shown after successful login
│
├── shared/
│   └── crypto_demo.py            # Cryptography module (MD5 vs SHA-256 vs bcrypt)
│
├── report/
│   └── report.md                 # Full project report (10 sections)
│
├── SETUP.md                      # Step-by-step environment setup guide
└── PROJECT_PLAN.md               # Project plan and progress log
```

---

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Attack Scripts | Python 3 · Paramiko · Requests · Socket · Threading |
| GUI & Streaming | Flask · Server-Sent Events (SSE) |
| Notebook | Jupyter |
| Cryptography | hashlib (MD5 / SHA-256) · bcrypt |
| Victim Stack | PHP · Apache2 (port 8888) · MySQL · mysqli |
| SIEM / IDS | Wazuh Manager · Wazuh Indexer · Wazuh Dashboard |
| Infrastructure | Kali Linux · Ubuntu 22.04 · Windows Hyper-V |
| Framework | MITRE ATT&CK |

---

## Flask Attacker Dashboard

The main interface runs on Kali at `http://172.22.225.120:5000`. Four tabs:

**SSH BRUTE FORCE**
- Target IP, username, wordlist path
- Live log stream via SSE
- Progress bar and result banner on crack

**PORT SCANNER**
- Target IP and port range (`common`, `1-1024`, `1-65535`)
- 50 concurrent threads
- Open ports table with banner/service info

**WEB BRUTE FORCE**
- Target URL, username, wordlist, fail indicator
- Detects success via HTTP 302 redirect vs 200 failure
- Live log stream

**SQL INJECTION**
- Login URL (for bypass) and search URL (for UNION extraction)
- Phase 0: probe for SQL errors
- Phase 1: 6 login bypass payloads
- Phase 2: 6 UNION payloads dumping users, passwords, emails, MySQL version
- Extracted data table rendered live

---

## Wazuh Detection Results

| Attack | Rule ID | Level | Description |
| --- | --- | --- | --- |
| SSH Brute Force | 5760 | 5 | SSH authentication failure |
| Web Brute Force | 100002 | 3 | Login page request detected |
| Web Brute Force | 100003 | 10 | 5+ attempts from same IP in 30s |
| SQL Injection | 31103 | 7 | SQL injection attempt |
| SQL Injection | 31164 | 6 | SQL injection pattern matched |
| SQL Injection | 31106 | 6 | Web attack returned 200 success |

Custom rules for web brute force are in `/var/ossec/etc/rules/local_rules.xml` on the Ubuntu VM. SQL injection was caught automatically by Wazuh's built-in web ruleset — no custom rule needed because SQL keywords (`UNION`, `OR`, `SELECT`) appear in the Apache access log.

---

## Key Results

| Metric | Result |
| --- | --- |
| SSH password cracked | 123123 — found in 21 attempts |
| Web login cracked | 123123 — found in 21 attempts, under 1 second |
| Ports scanned | 65,535 |
| Open ports found | 9 |
| SQL login bypass | admin' OR '1'='1 — bypassed in 4th attempt |
| UNION payloads run | 6 — dumped users, passwords, emails, MySQL version |
| bcrypt vs MD5 speed | bcrypt is 127,330x slower per attempt |
| MITRE techniques detected | 5 (T1110, T1046, T1190, Valid Accounts, SSH) |

---

## Setup

See [SETUP.md](SETUP.md) for the full step-by-step guide covering Hyper-V, Ubuntu, Kali, Wazuh, Apache, MySQL, and PHP setup.

---

## Ethical Disclaimer

All attacks were performed exclusively inside an isolated Hyper-V virtual network. No real infrastructure, external networks, or third-party systems were targeted at any point.
