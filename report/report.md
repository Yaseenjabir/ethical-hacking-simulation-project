# Ethical Hacking Project — Digital Report

**Course:** Cybersecurity  
**Project:** Python-Based Ethical Hacking Simulation  
**Author:** Yaseen Jabir  
**Date:** June 2026  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Environment Setup](#2-environment-setup)
3. [Cryptography Module](#3-cryptography-module)
4. [Attacker Side](#4-attacker-side)
5. [Defender Side — SOC & IDS](#5-defender-side--soc--ids)
6. [Integration & Testing](#6-integration--testing)
7. [Conclusion & Recommendations](#7-conclusion--recommendations)

---

## 1. Introduction

### 1.1 Project Objective

This project simulates a real-world cyberattack scenario in a fully controlled and isolated virtual environment. The goal is to demonstrate how ethical hackers identify vulnerabilities, evaluate defense mechanisms, and implement proactive monitoring and rapid threat detection.

The simulation covers two sides:

- **Attacker Side:** An SSH brute force attack launched from a Kali Linux VM using Python and a Flask-based GUI
- **Defender Side:** A Security Operations Center (SOC) powered by Wazuh SIEM/IDS running on the victim Ubuntu VM

### 1.2 Chosen Attack — SSH Brute Force

SSH (Secure Shell) brute force is one of the most common real-world attacks. It works by systematically trying passwords from a wordlist until one succeeds. It was chosen because:

- Clear attack and defense flow
- Strong cryptography tie-in (password hashing)
- Easily detected by an IDS
- Realistic — SSH brute force is among the top attack vectors worldwide

### 1.3 Ethical Disclaimer

All attacks were performed exclusively inside an isolated Hyper-V virtual network. No real infrastructure, external networks, or third-party systems were targeted at any point.

---

## 2. Environment Setup

### 2.1 Hypervisor

**Platform:** Windows Hyper-V (confirmed active on Windows 11 Pro)

### 2.2 Virtual Machines

| VM | OS | Role | IP Address | RAM |
| --- | --- | --- | --- | --- |
| kali-linux-2026.1-hyperv-amd64 | Kali Linux 2026.1 | Attacker | 172.22.225.120 | 1–3 GB (dynamic) |
| test-vm | Ubuntu 22.04 LTS | Victim + SOC | 172.22.229.213 | 0.5–5 GB (dynamic) |

### 2.3 Network Architecture

Both VMs are connected to the Hyper-V **Default Switch**, which provides automatic IP assignment and direct VM-to-VM communication.

```
Windows Host (Hyper-V)
        |
   Default Switch (172.22.0.0/20)
        |              |
   Kali Linux     Ubuntu VM
  172.22.225.120  172.22.229.213
  (Attacker)      (Victim + Wazuh SOC)
```

### 2.4 Services Confirmed

| Service | VM | Status |
| --- | --- | --- |
| SSH (port 22) | Ubuntu | Running, auto-start enabled |
| auth.log | Ubuntu | Active at /var/log/auth.log |
| Wazuh Manager | Ubuntu | Running |
| Wazuh Indexer | Ubuntu | Running |
| Wazuh Dashboard | Ubuntu | Running at https://192.168.2.83 |
| Flask Attack GUI | Kali | Running at http://172.22.225.120:5000 |

### 2.5 Python Environment (Kali)

A Python virtual environment was created to avoid system package conflicts:

```bash
python3 -m venv ~/project-env
source ~/project-env/bin/activate
pip install paramiko flask bcrypt
```

---

## 3. Cryptography Module

### 3.1 Purpose

Before launching the attack, the project demonstrates the cryptographic theory behind why brute force attacks succeed against weak password hashing. This is implemented in `shared/crypto_demo.py`.

### 3.2 Algorithms Compared

| Algorithm | Salt | Speed | Vulnerability |
| --- | --- | --- | --- |
| MD5 | No | 0.0086 ms | Rainbow tables, deterministic |
| SHA-256 | No | 0.0029 ms | Dictionary attacks |
| SHA-256 + Salt | Yes | ~0.003 ms | Resistant to rainbow tables |
| Bcrypt | Built-in | 1095 ms | Best — intentionally slow |

### 3.3 Key Finding

```
MD5    cracked in : 0.0086 ms
Bcrypt cracked in : 1095.036 ms

Bcrypt is 127,330x slower than MD5 — by design.
```

With a wordlist of 10,000 passwords:

| Algorithm | Estimated Crack Time |
| --- | --- |
| MD5 | ~0.086 seconds |
| SHA-256 | ~0.029 seconds |
| Bcrypt | ~3 hours |

### 3.4 Connection to the Attack

Linux SSH uses the system's password hash stored in `/etc/shadow`. Our brute force does not crack the hash directly — it lets the SSH server perform the comparison on each attempt, making it algorithm-agnostic. However, the cryptography module explains why weak systems are particularly vulnerable.

---

## 4. Attacker Side

### 4.1 Architecture

```
Kali Linux VM
├── attack.ipynb          ← Jupyter Notebook (step-by-step attack)
├── attacker/
│   ├── app.py            ← Flask GUI (web-based attack controller)
│   ├── templates/
│   │   └── index.html    ← Attacker dashboard UI
│   └── wordlists/
│       └── common_passwords.txt
└── shared/
    └── crypto_demo.py    ← Cryptography module
```

### 4.2 Wordlist

A curated wordlist of 21 common passwords was used, including the victim's actual password (`123123`) positioned near the end to generate realistic failed attempts before success.

### 4.3 Jupyter Notebook — attack.ipynb

The notebook walks through the attack step by step:

| Step | Description |
| --- | --- |
| 1 | Import libraries (paramiko, socket, datetime) |
| 2 | Run cryptography demo |
| 3 | Configure target (IP, port, username, wordlist) |
| 4 | Verify target SSH is reachable |
| 5 | Load wordlist |
| 6 | Define brute force function using paramiko |
| 7 | Launch the attack |
| 8 | Print attack summary |

**Result:**

```
Total attempts  : 21
Failed attempts : 20
Successful      : 1
Cracked password: 123123

MITRE ATT&CK: T1110 - Brute Force
```

### 4.4 Flask GUI — Attacker Dashboard

A dark-themed web application provides a visual interface to control the attack without using the terminal.

**Features:**

- Configure target IP, port, username, wordlist, and timeout
- Start / Stop attack buttons
- Real-time live log (failed attempts in red, success in green)
- Progress bar showing attempts completed
- Final result banner displaying the cracked password

**Screenshot summary:**

```
[ SSH BRUTE FORCE — ATTACKER DASHBOARD ]

// ATTACK CONFIGURATION     // LIVE ATTACK LOG
TARGET IP: 172.22.229.213   FAILED [001] 16:39:12 — 123456
SSH PORT:  22               FAILED [002] 16:39:15 — password
USERNAME:  yaseen           ...
WORDLIST:  ~/wordlist.txt   FAILED [020] 16:39:51 — shadow
                            SUCCESS — Password found: 123123
[▶ START ATTACK]
[■ STOP        ]            PASSWORD CRACKED ► 123123
Progress: 21/21
```

### 4.5 How Paramiko Works

Paramiko is a Python SSH library. For each password attempt:

```python
client.connect(
    hostname="172.22.229.213",
    port=22,
    username="yaseen",
    password="attempt",
    timeout=5
)
# Success → password found
# AuthenticationException → wrong password, try next
```

---

## 5. Defender Side — SOC & IDS

### 5.1 Wazuh Overview

Wazuh is an open-source Security Information and Event Management (SIEM) platform. The full stack was installed on the Ubuntu VM:

| Component | Purpose | RAM Used |
| --- | --- | --- |
| Wazuh Manager | Receives and analyzes logs | 1.9 GB |
| Wazuh Indexer | Stores and indexes alerts | 1.2 GB |
| Wazuh Dashboard | Web-based SOC UI | 170 MB |

### 5.2 How Wazuh Detected the Attack

Every SSH login attempt generates entries in `/var/log/auth.log` on Ubuntu. Wazuh's log collector monitors this file in real time and matches entries against its rule set.

**Rules triggered during the attack:**

| Rule ID | Description | Level |
| --- | --- | --- |
| 5760 | sshd: authentication failed | 5 |
| 5503 | PAM: User login failed | 5 |
| 5501 | PAM: Login session opened | 3 |

### 5.3 MITRE ATT&CK Mapping

Wazuh automatically mapped the detected behavior to the MITRE ATT&CK framework:

| Technique | ID | Description |
| --- | --- | --- |
| Brute Force | T1110 | Multiple failed authentication attempts |
| Password Guessing | T1110.001 | Systematic password attempts via SSH |

### 5.4 Evidence from auth.log

```
Jun 20 16:20:38 sshd: Failed password for yaseen from 172.22.225.120 port 46136
Jun 20 16:20:41 sshd: Failed password for yaseen from 172.22.225.120 port 51268
...
Jun 20 16:21:21 sshd: Accepted password for yaseen from 172.22.225.120 port 60944
```

Ubuntu logged all 20 failed attempts and the final successful login from Kali's IP.

---

## 6. Integration & Testing

### 6.1 Full Attack Flow

```
1. Attacker opens Flask GUI at http://172.22.225.120:5000
2. Configures target: 172.22.229.213:22, user: yaseen
3. Clicks START ATTACK
4. Flask app spawns background thread running brute force
5. Paramiko tries each password via SSH
6. Ubuntu logs each attempt in /var/log/auth.log
7. Wazuh reads auth.log in real time
8. Wazuh raises alerts on dashboard
9. After 20 failures, password "123123" succeeds
10. Flask GUI displays PASSWORD CRACKED → 123123
11. Wazuh dashboard shows spike in authentication failure alerts
```

### 6.2 Test Results

| Test | Result |
| --- | --- |
| Kali → Ubuntu ping | Pass (0% packet loss, ~0.4ms) |
| SSH reachability check | Pass (port 22 open) |
| Brute force notebook | Pass (password found in 21 attempts) |
| Flask GUI attack | Pass (live log, progress bar, result banner) |
| Wazuh alert detection | Pass (authentication failures detected) |
| MITRE ATT&CK mapping | Pass (T1110 — Brute Force) |
| auth.log evidence | Pass (all attempts logged with attacker IP) |

---

## 7. Conclusion & Recommendations

### 7.1 Conclusion

This project successfully simulated a complete SSH brute force attack cycle in a controlled environment:

- The **attacker side** demonstrated how an automated Python script combined with a professional GUI can systematically crack weak passwords
- The **cryptography module** proved that algorithm choice is critical — bcrypt is 127,330x slower than MD5 per attempt
- The **defender side** showed how a real SIEM (Wazuh) detects, categorizes, and logs attacks in real time using the MITRE ATT&CK framework

### 7.2 Defense Recommendations

| Recommendation | Impact |
| --- | --- |
| Use strong passwords (not in wordlists) | Eliminates simple brute force |
| Disable password auth, use SSH keys | Makes brute force impossible |
| Enable fail2ban / Wazuh Active Response | Auto-blocks attacker IP after N failures |
| Change default SSH port (22) | Reduces automated scanning |
| Use bcrypt for all stored passwords | Makes offline cracking impractical |
| Monitor auth.log continuously with IDS | Enables rapid threat detection |

### 7.3 Key Takeaway

> A password like `123123` was cracked in under 2 minutes from a 21-entry wordlist.
> The same attack against a bcrypt-protected system with SSH keys disabled would take years.
> Security is a combination of strong cryptography, proper configuration, and continuous monitoring.
