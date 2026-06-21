# Ethical Hacking Project — Project Plan

## Overview

A Python-based ethical hacking simulation with two sides:

- **Attacker:** SSH brute force + port scanner launched from Kali Linux via a Flask GUI and Jupyter Notebook
- **Defender:** Wazuh SIEM/IDS running on the victim Ubuntu VM, detecting attacks and mapping them to MITRE ATT&CK

---

## Attacks Simulated

| Attack | Tool | MITRE ATT&CK |
| --- | --- | --- |
| SSH Brute Force | Python paramiko | T1110.001 — Password Guessing |
| Port Scanning | Python socket + threading | T1046 — Network Service Discovery |

---

## Project Structure

```text
cybersecurity/
│
├── attacker/
│   ├── app.py                    # Flask GUI — two-tab attacker dashboard
│   ├── port_scanner.py           # Port scanner module (TCP Connect, threading, banner grab)
│   ├── attack.ipynb              # Jupyter Notebook — step-by-step brute force
│   ├── templates/
│   │   └── index.html            # Attacker dashboard UI (dark hacker theme)
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

[x] attacker/templates/index.html
      - Two-tab dashboard: SSH BRUTE FORCE | PORT SCANNER
      - Brute force tab: config panel, live log, progress bar, result banner
      - Port scanner tab: config panel, live log, open ports table
      - Dark hacker theme (green on black, Courier New)
      - Default port range: 1-65535
```

### Phase 4 — Defender Side

```text
[x] Wazuh all-in-one installed on Ubuntu
[x] Wazuh Manager, Indexer, Dashboard — all running
[x] Dashboard accessible at https://172.22.229.213
[x] SSH brute force detected — rules 5760, 5503, 5501 triggered
[x] Port scan detected — Remote Services technique flagged
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
[x] Wazuh dashboard showed both attacks in real time
[x] MITRE ATT&CK dashboard showed 5 techniques
[x] auth.log captured all 20 failed and 1 successful SSH attempt
[x] Both attacks confirmed detected and logged with attacker IP
```

### Phase 6 — Report and Documentation

```text
[x] report/report.md — 8-section report
      Section 1: Introduction
      Section 2: Environment Setup
      Section 3: Cryptography Module
      Section 4: Attacker Side — SSH Brute Force
      Section 5: Port Scanner
      Section 6: Defender Side — SOC and IDS
      Section 7: Integration and Testing
      Section 8: Conclusion and Recommendations

[x] SETUP.md — full local setup guide (11 steps)
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
| Port scanner | Python socket + threading |
| Attacker GUI | Flask + SSE (Server-Sent Events) |
| Cryptography demo | Python hashlib + bcrypt |
| Notebook walkthrough | Jupyter (.ipynb) |
| SIEM and IDS | Wazuh (Manager + Indexer + Dashboard) |
| Victim service | OpenSSH on Ubuntu 22.04 |
| Hypervisor | Windows Hyper-V |

---

## Key Results

| Metric | Value |
| --- | --- |
| Passwords tried before crack | 21 |
| Brute force duration | ~90 seconds |
| Ports scanned | 65,535 |
| Open ports found | 9 |
| Port scan duration | ~3 minutes |
| Wazuh MITRE techniques detected | 5 |
| Bcrypt vs MD5 speed ratio | 127,330x slower |

---

## Notes

- All attacks run **only inside the isolated VM network** — never on real infrastructure
- LabNetwork switch was abandoned — Default Switch used instead (solved VM-to-VM connectivity)
- defender/ids.py and defender/app.py were replaced entirely by Wazuh
- Wazuh installed with `-i` flag to bypass minimum hardware check (8 GB RAM required, VMs have less)
