# Ethical Hacking Project — Project Plan

## Overview

A Python-based ethical hacking simulation with two sides:

- **Attacker:** Brute force attack launched from Kali Linux via a Flask GUI + Jupyter Notebook
- **Defender:** SOC dashboard (Flask) + Python IDS monitoring a victim Ubuntu VM

---

## Chosen Attack: SSH Brute Force

**Why:** Clear attack/defense flow, strong cryptography tie-in (password hashing), easy IDS detection, works in isolated VM network.

---

## Project Structure

```text
cybersecurity/
│
├── attacker/
│   ├── attack.ipynb              # Jupyter Notebook — brute force logic + hash demo
│   ├── app.py                    # Flask GUI for attacker
│   ├── templates/
│   │   └── index.html            # Attacker dashboard UI
│   ├── static/                   # CSS / JS
│   └── wordlists/
│       └── common_passwords.txt  # Password wordlist
│
├── defender/
│   ├── ids.py                    # IDS — monitors auth logs, triggers alerts
│   ├── app.py                    # Flask SOC dashboard
│   ├── templates/
│   │   └── dashboard.html        # SOC dashboard UI
│   ├── static/                   # CSS / JS
│   └── alerts.db                 # SQLite — stores alert history
│
├── shared/
│   └── crypto_demo.py            # Cryptography demos (hashing, salting)
│
├── report/
│   └── report.md                 # Digital report (to be written last)
│
└── PROJECT_PLAN.md               # This file
```

---

## Build Order

```text
Phase 1 — Environment Setup
  [x] Confirm Hyper-V is active
  [x] Ubuntu victim VM (test-vm) exists and confirmed in Hyper-V
  [x] Dynamic memory enabled on test-vm (512 MB min / 1 GB startup / 4 GB max)
  [x] Download Kali Hyper-V image and create kali-attacker VM
  [x] Create LabNetwork internal switch in Hyper-V
  [x] Connect both VMs to LabNetwork
  [x] Disable Secure Boot on kali-attacker
  [x] Enable Dynamic memory on kali-attacker (1 GB min / 2 GB startup / 3 GB max)
  [x] SSH confirmed running on Ubuntu (port 22, user: yaseen, IP: 192.168.2.83)
  [x] auth.log confirmed at /var/log/auth.log
  [x] Wazuh installed on Ubuntu (all-in-one)
  [x] Ubuntu disk expanded to 50 GB
  [x] Verify Kali and Ubuntu can ping each other
        Kali IP:   172.22.225.120 (Default Switch)
        Ubuntu IP: 172.22.229.213 (Default Switch via eth2)
        Latency:   ~0.4ms, 0% packet loss
  [x] Install Python deps on Kali (flask, paramiko — installed in ~/project-env)

Phase 2 — Cryptography Module
  [ ] shared/crypto_demo.py
      - MD5 / SHA-256 hashing demo
      - Salted hash demo
      - Show why weak hashes are crackable

Phase 3 — Attacker Side
  [ ] attack.ipynb
      - Connect to target via paramiko (SSH)
      - Loop through wordlist
      - Log results (success / fail / timestamp)
      - Embed crypto_demo.py output
  [ ] attacker/app.py (Flask GUI)
      - Input: target IP, port, username, wordlist
      - Start / Stop attack button
      - Live progress log display
      - Show cracked password if found

Phase 4 — Defender Side
  [x] Wazuh installed on Ubuntu (all-in-one) — replaces ids.py and defender/app.py
  [x] Wazuh dashboard accessible at https://192.168.2.83
  [x] Wazuh detects SSH authentication failures (confirmed)
  [x] MITRE ATT&CK mapping working (Password Guessing + SSH)
  [ ] Configure Wazuh active response to block attacker IP (optional)

Phase 5 — Integration & Testing
  [ ] Run attack from Kali VM to target Ubuntu VM
  [ ] Confirm IDS detects and alerts
  [ ] Confirm SOC dashboard shows real-time alerts
  [ ] Test IP blocking

Phase 6 — Report & Presentation
  [ ] Write report/report.md
  [ ] Prepare slides
  [ ] Record or prepare live demo
```

---

## VM Network Setup

Hypervisor: **Windows Hyper-V** (confirmed active)

```text
Hyper-V Internal/Private Network

  Kali Linux (Attacker)   ->  VM to be created   [NOT SET UP YET]
  Ubuntu (Victim)         ->  VM name: test-vm   [RUNNING]
        |                   IP: 192.168.2.83
        |                   User: yaseen
        +-- SSH running on port 22        [CONFIRMED]
        +-- auth.log at /var/log/auth.log [CONFIRMED]
        +-- IDS script (ids.py) running   [not deployed yet]
        +-- SOC dashboard on port 5001    [not deployed yet]
```

---

## Tech Stack

| Component          | Technology          |
| ------------------ | ------------------- |
| Attack script      | Python + paramiko   |
| Attacker GUI       | Flask               |
| Notebook           | Jupyter (.ipynb)    |
| Cryptography demo  | Python hashlib      |
| IDS                | Python + watchdog   |
| SOC Dashboard      | Flask               |
| Alert storage      | SQLite (sqlite3)    |
| Victim service     | OpenSSH             |
| IDS block action   | fail2ban / iptables |

---

## Python Dependencies

### Attacker VM (Kali)

```bash
pip install flask paramiko jupyter
```

### Victim VM (Ubuntu)

```bash
pip install flask watchdog
```

---

## Deliverables Checklist

```text
[ ] attack.ipynb          — Jupyter notebook with brute force + crypto demo
[ ] attacker/app.py       — Flask attacker GUI
[ ] defender/ids.py       — IDS monitoring script
[ ] defender/app.py       — SOC dashboard
[ ] shared/crypto_demo.py — Cryptography module
[ ] report/report.md      — Full written report
[ ] Presentation slides
[ ] Live demo ready
```

---

## Current Status

| Phase                      | Status                  |
| -------------------------- | ----------------------- |
| 1 — Environment Setup      | Complete                |
| 2 — Cryptography Module    | Complete                |
| 3 — Attacker Side          | Complete                |
| 4 — Defender Side          | Complete (4/5)          |
| 5 — Integration & Testing  | Complete                |
| 6 — Report & Presentation  | In Progress             |

---

## Notes

- All attacks run **only inside the isolated VM network** — never on real infrastructure
- The project demonstrates ethical hacking principles: controlled environment, detection, and defense
- Start each session by checking this file to know where we left off
