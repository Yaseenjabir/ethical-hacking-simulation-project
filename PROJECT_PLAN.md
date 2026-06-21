# Ethical Hacking Project — Project Plan

## Overview

A Python-based ethical hacking simulation with two sides:

- **Attacker:** Four attack modules launched from Kali Linux via a Flask GUI and Jupyter Notebook
- **Defender:** Wazuh SIEM/IDS running on the victim Ubuntu VM, detecting all attacks and mapping them to MITRE ATT&CK

---

## Attacks Simulated

| Attack | Tool | MITRE ATT&CK |
| --- | --- | --- |
| SSH Brute Force | Python paramiko | T1110.001 — Password Guessing |
| Port Scanning | Python socket + threading | T1046 — Network Service Discovery |
| Web Login Brute Force | Python requests + PHP Apache | T1110.001 — Password Guessing (HTTP) |
| SQL Injection | Python requests + MySQL PHP app | T1190 — Exploit Public-Facing Application |

---

## Project Structure

```text
cybersecurity/
│
├── attacker/
│   ├── app.py                    # Flask GUI — four-tab attacker dashboard
│   ├── port_scanner.py           # Port scanner module (TCP Connect, threading, banner grab)
│   ├── web_bruteforce.py         # Web login brute force (HTTP POST, requests library)
│   ├── sqli_attack.py            # SQL injection (login bypass + UNION extraction)
│   ├── attack.ipynb              # Jupyter Notebook — step-by-step brute force
│   ├── templates/
│   │   └── index.html            # Attacker dashboard UI (dark hacker theme, three tabs)
│   └── wordlists/
│       └── common_passwords.txt  # 21-password wordlist (includes target password)
│
├── shared/
│   └── crypto_demo.py            # Cryptography demos — MD5, SHA-256, Bcrypt comparison
│
├── report/
│   └── report.md                 # Full 8-section project report
│
├── SETUP.md                      # Local setup guide for cloning and running
└── PROJECT_PLAN.md               # This file
```

---

## Phase Progress

### Phase 1 — Environment Setup

```text
[x] Confirm Hyper-V is active on Windows 11 Pro
[x] Ubuntu victim VM (test-vm) confirmed in Hyper-V
[x] Dynamic memory enabled on Ubuntu (0.5 GB min / 5 GB max)
[x] Download Kali Hyper-V image and create kali-attacker VM
[x] Enable Dynamic memory on Kali (1 GB min / 2 GB startup / 3 GB max)
[x] Connect both VMs to Default Switch
[x] Ubuntu disk expanded to 50 GB
[x] SSH confirmed running on Ubuntu (port 22, user: yaseen)
[x] auth.log confirmed at /var/log/auth.log
[x] Wazuh installed on Ubuntu (all-in-one with -i flag to bypass RAM check)
[x] Kali and Ubuntu confirmed reachable — 0% packet loss, ~0.4ms latency
      Kali IP:   172.22.225.120
      Ubuntu IP: 172.22.229.213
[x] Python venv created on Kali (~/project-env)
[x] Flask, paramiko, bcrypt installed on Kali
[x] Timezone synced — all three systems set to Asia/Karachi (UTC+5)
```

### Phase 2 — Cryptography Module

```text
[x] shared/crypto_demo.py
      - MD5 hashing (fast, 0.0086 ms — insecure)
      - SHA-256 hashing (fast, 0.0029 ms — better but still fast)
      - Salted SHA-256 (resistant to rainbow tables)
      - Bcrypt (1095 ms — intentionally slow, 127,330x slower than MD5)
      - Brute force speed comparison across all four algorithms
```

### Phase 3 — Attacker Side

```text
[x] attack.ipynb
      - Imports and crypto demo
      - Target configuration (172.22.229.213:22, user: yaseen)
      - Reachability check
      - Wordlist loading
      - Brute force loop with paramiko
      - Attack summary (21 attempts, cracked: 123123)
      - MITRE ATT&CK label: T1110 — Brute Force

[x] attacker/app.py (Flask GUI — brute force routes)
      - POST /start  — launches background brute force thread
      - POST /stop   — signals stop event
      - GET  /stream — SSE live log stream
      - GET  /status — progress and found password

[x] attacker/port_scanner.py
      - TCP Connect scan (no raw sockets required)
      - Threading with semaphore (50 concurrent threads)
      - Banner grabbing via HTTP HEAD probe
      - parse_port_range() — supports "common", "1-1024", "22,80,443", "1-65535"
      - COMMON_PORTS dictionary (18 well-known ports named)

[x] attacker/app.py (Flask GUI — port scanner routes)
      - POST /scan/start   — launches background scan thread
      - POST /scan/stop    — signals stop event
      - GET  /scan/stream  — SSE live scan log
      - GET  /scan/results — returns open ports as JSON

[x] attacker/web_bruteforce.py
      - HTTP POST login form brute force using requests library
      - Detects success via 302 redirect vs 200 failure response
      - allow_redirects=False to distinguish success from failure
      - Sequential attempts (no threading — avoids session corruption)
      - MITRE ATT&CK: T1110.001 — Brute Force: Password Guessing (HTTP)

[x] attacker/sqli_attack.py
      - Phase 0: injection probe (single quote test, error detection)
      - Phase 1: login bypass (6 payloads — OR-based, comment-based)
      - Phase 2: UNION extraction (dump users, passwords, emails, DB version, tables)
      - Uses # as MySQL comment (more reliable than -- in HTTP context)
      - Parses HTML table rows from response to display extracted data
      - MITRE ATT&CK: T1190 — Exploit Public-Facing Application

[x] attacker/app.py (Flask GUI — web brute force + SQL injection routes)
      - POST /web/start   — launches background web attack thread
      - POST /web/stop    — signals stop event
      - GET  /web/stream  — SSE live log stream
      - GET  /web/status  — found password
      - POST /sqli/start  — launches background SQL injection thread
      - POST /sqli/stop   — signals stop event
      - GET  /sqli/stream — SSE live log stream
      - GET  /sqli/status — bypass payload and extracted data

[x] attacker/templates/index.html
      - Four-tab dashboard: SSH BRUTE FORCE | PORT SCANNER | WEB BRUTE FORCE | SQL INJECTION
      - SQL injection tab: login URL + search URL config, live log, extracted data table
      - Dark hacker theme (green on black, Courier New)
      - Default port range: 1-65535

[x] victim-webapp/ (PHP source files for anyone cloning the repo)
      - login_basic.php  — hardcoded creds, used for web brute force
      - login_sqli.php   — MySQL login, vulnerable to SQL injection
      - search.php       — vulnerable search, used for UNION extraction
      - dashboard.php    — protected page shown after successful login
```

### Phase 4 — Defender Side

```text
[x] Wazuh all-in-one installed on Ubuntu
[x] Wazuh Manager, Indexer, Dashboard — all running
[x] Dashboard accessible at https://172.22.229.213
[x] SSH brute force detected — rules 5760, 5503, 5501 triggered
[x] Port scan detected — Remote Services technique flagged
[x] Web brute force detected — custom rules 100002 + 100003 written and deployed
[x] Apache log monitoring added to ossec.conf
[x] Custom Wazuh rule written in local_rules.xml:
      - Rule 100002 (level 3): fires on every POST to /login.php
      - Rule 100003 (level 10): fires after 5 hits from same IP in 30 seconds
[x] SQL injection detected automatically — Wazuh built-in rules fired:
      - Rule 31103 (level 7): SQL injection attempt (OR/UNION keywords in request)
      - Rule 31164 (level 6): SQL injection pattern matched
      - Rule 31106 (level 6): web attack returned 200 success
      - Rule 31122 (level 5): 500 error during probe phase
[x] MITRE ATT&CK auto-mapped:
      - Valid Accounts
      - Password Guessing
      - SSH
      - Sudo and Sudo Caching
      - Remote Services
[x] Timezone aligned — alert timestamps now match real clock time
```

### Phase 5 — Integration and Testing

```text
[x] SSH brute force ran end-to-end — password cracked in 21 attempts
[x] Flask GUI showed live attack log and PASSWORD CRACKED banner
[x] Port scan ran across all 65,535 ports — 9 open ports found
[x] Banner grabbing returned SSH version and HTTP status codes
[x] Web brute force ran against PHP login page — password cracked in 21 attempts
[x] Wazuh detected web attack — rule 100003 fired at level 10
[x] SQL injection ran — login bypassed with OR payload, UNION extraction dumped DB
[x] Wazuh detected SQL injection automatically — rules 31103 and 31164 fired
[x] Wazuh dashboard showed all four attacks in real time
[x] MITRE ATT&CK dashboard showed 5 techniques
[x] auth.log captured all SSH attempts with attacker IP
[x] Apache access.log captured all web and SQL injection attempts with attacker IP
[x] All four attacks confirmed detected and logged
```

### Phase 6 — Report and Documentation

```text
[x] report/report.md — 9-section report
      Section 1: Introduction
      Section 2: Environment Setup
      Section 3: Cryptography Module
      Section 4: Attacker Side — SSH Brute Force
      Section 5: Port Scanner
      Section 6: Web Brute Force
      Section 7: Defender Side — SOC and IDS
      Section 8: Integration and Testing
      Section 9: Conclusion and Recommendations

[x] SETUP.md — full local setup guide
[x] .gitignore — excludes VM files, venvs, pycache, logs
[x] Git repository initialized and pushed to GitHub
[x] PROJECT_PLAN.md — updated to reflect actual build
```

---

## Current Status

| Phase | Status |
| --- | --- |
| 1 — Environment Setup | Complete |
| 2 — Cryptography Module | Complete |
| 3 — Attacker Side | Complete |
| 4 — Defender Side | Complete |
| 5 — Integration and Testing | Complete |
| 6 — Report and Documentation | Complete |

---

## Tech Stack

| Component | Technology |
| --- | --- |
| SSH brute force | Python + paramiko |
| Web brute force | Python + requests |
| SQL injection | Python + requests (login bypass + UNION) |
| Port scanner | Python socket + threading |
| Attacker GUI | Flask + SSE (Server-Sent Events) — four tabs |
| Cryptography demo | Python hashlib + bcrypt |
| Notebook walkthrough | Jupyter (.ipynb) |
| Vulnerable web app | PHP + Apache + MySQL (port 8888) |
| SIEM and IDS | Wazuh (Manager + Indexer + Dashboard) |
| Custom Wazuh rules | local_rules.xml (rules 100002, 100003) |
| Victim SSH service | OpenSSH on Ubuntu 22.04 |
| Hypervisor | Windows Hyper-V |

---

## Key Results

| Metric | Value |
| --- | --- |
| SSH passwords tried before crack | 21 |
| SSH brute force duration | ~90 seconds |
| Web passwords tried before crack | 21 |
| Web brute force duration | ~1 second |
| SQL injection login bypass payloads | 6 |
| SQL injection UNION payloads | 6 |
| Ports scanned | 65,535 |
| Open ports found | 9 |
| Port scan duration | ~3 minutes |
| Wazuh MITRE techniques detected | 5 |
| Custom Wazuh rules written | 2 (100002, 100003) |
| Wazuh built-in rules triggered | 31103, 31106, 31122, 31164 (SQL injection) |
| Bcrypt vs MD5 speed ratio | 127,330x slower |

---

## Notes

- All attacks run **only inside the isolated VM network** — never on real infrastructure
- LabNetwork switch was abandoned — Default Switch used instead (solved VM-to-VM connectivity)
- defender/ids.py and defender/app.py were replaced entirely by Wazuh
- Wazuh installed with `-i` flag to bypass minimum hardware check (8 GB RAM required, VMs have less)
