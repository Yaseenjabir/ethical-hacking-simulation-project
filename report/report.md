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
4. [Attacker Side — SSH Brute Force](#4-attacker-side--ssh-brute-force)
5. [Port Scanner](#5-port-scanner)
6. [Defender Side — SOC and IDS](#6-defender-side--soc-and-ids)
7. [Integration and Testing](#7-integration-and-testing)
8. [Conclusion and Recommendations](#8-conclusion-and-recommendations)

---

## 1. Introduction

### 1.1 Project Objective

This project simulates a real-world cyberattack scenario in a fully controlled and isolated virtual environment. The goal is to demonstrate how ethical hackers identify vulnerabilities, evaluate defense mechanisms, and implement proactive monitoring and rapid threat detection.

The simulation covers two sides:

- **Attacker Side:** An SSH brute force attack and port scanner launched from a Kali Linux VM using Python and a Flask-based GUI
- **Defender Side:** A Security Operations Center (SOC) powered by Wazuh SIEM/IDS running on the victim Ubuntu VM

### 1.2 Attacks Simulated

| Attack | Technique | MITRE ATT&CK |
| --- | --- | --- |
| SSH Brute Force | Systematic password guessing via paramiko | T1110.001 |
| Port Scanning | TCP Connect scan across all 65,535 ports | T1046 |

Both attacks represent the reconnaissance and initial access phases of a real attack — and are easily detectable by a SIEM.

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

```text
Windows Host (Hyper-V)
        |
   Default Switch (172.22.0.0/20)
        |              |
   Kali Linux     Ubuntu VM
  172.22.225.120  172.22.229.213
  (Attacker)      (Victim + Wazuh SOC)
```

### 2.4 Time Synchronization

Both VMs and the Windows host were configured to the same timezone (Asia/Karachi, UTC+5) so that Wazuh alert timestamps match real clock time:

```bash
sudo timedatectl set-timezone Asia/Karachi
sudo timedatectl set-ntp true
```

### 2.5 Services Confirmed

| Service | VM | Status |
| --- | --- | --- |
| SSH (port 22) | Ubuntu | Running, auto-start enabled |
| auth.log | Ubuntu | Active at /var/log/auth.log |
| Wazuh Manager | Ubuntu | Running |
| Wazuh Indexer | Ubuntu | Running |
| Wazuh Dashboard | Ubuntu | Running at <https://172.22.229.213> |
| Flask Attack GUI | Kali | Running at <http://172.22.225.120:5000> |

### 2.6 Python Environment (Kali)

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

```text
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

## 4. Attacker Side — SSH Brute Force

### 4.1 Architecture

```text
Kali Linux VM
├── attack.ipynb          ← Jupyter Notebook (step-by-step attack)
├── attacker/
│   ├── app.py            ← Flask GUI (web-based attack controller)
│   ├── port_scanner.py   ← Port scanner module
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

```text
Total attempts  : 21
Failed attempts : 20
Successful      : 1
Cracked password: 123123

MITRE ATT&CK: T1110 - Brute Force
```

### 4.4 Flask GUI — Attacker Dashboard

A dark-themed web application provides a visual interface to control both attacks without using the terminal.

**Features:**

- Two-tab interface: SSH Brute Force and Port Scanner
- Configure target IP, port, username, wordlist, and timeout
- Start / Stop buttons for both attack modules
- Real-time live log via Server-Sent Events (SSE)
- Progress bar for brute force attempts
- Open ports table populated after scan completes

**Screenshot summary:**

```text
[ SSH BRUTE FORCE — ATTACKER DASHBOARD ]

// ATTACK CONFIGURATION     // LIVE ATTACK LOG
TARGET IP: 172.22.229.213   FAILED [001] 10:15:12 — 123456
SSH PORT:  22               FAILED [002] 10:15:15 — password
USERNAME:  yaseen           ...
WORDLIST:  ~/wordlist.txt   FAILED [020] 10:15:51 — shadow
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

## 5. Port Scanner

### 5.1 What Is Port Scanning?

Port scanning is a reconnaissance technique used to discover which services are running on a target machine. Before launching an exploit, attackers map open ports to understand the attack surface. This maps to **MITRE ATT&CK T1046 — Network Service Discovery**.

### 5.2 Scan Type Used — TCP Connect

We implemented a **TCP Connect scan** using Python's `socket` library. For each port, a full TCP three-way handshake is attempted:

```text
Kali → [SYN]        → Ubuntu:port
Kali ← [SYN-ACK]   ← Ubuntu   (port is OPEN)
Kali → [ACK]        → Ubuntu
Kali → [RST]        → Ubuntu   (close immediately)
```

If the port is closed, Ubuntu responds with `[RST]` immediately. If no response arrives within the timeout, the port is considered filtered by a firewall.

TCP Connect was chosen over SYN scan because it requires no raw socket privileges — standard Python sockets are sufficient.

### 5.3 Scan Results — Full 65,535 Port Scan

Target: `172.22.229.213` | Threads: 50 | Timeout: 1s | Duration: ~3 minutes

| Port | Service | Banner |
| --- | --- | --- |
| 22 | SSH | SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.15 |
| 80 | HTTP | HTTP/1.1 200 OK |
| 443 | HTTPS | — |
| 1514 | Wazuh Agent (log receiver) | — |
| 1515 | Wazuh Agent (enrollment) | — |
| 3389 | RDP | — |
| 8080 | HTTP-Alt | HTTP/1.1 200 OK |
| 8081 | Unknown | HTTP/1.1 502 Bad Gateway |
| 55000 | Wazuh Manager API | — |

9 open ports found across 65,535 scanned.

### 5.4 Notable Findings

**Ports 1514 and 1515** reveal that the target is running Wazuh. An attacker finding these ports would immediately know the system is monitored.

**Port 22 banner** discloses the exact SSH version: `OpenSSH_8.9p1 Ubuntu-3ubuntu0.15`. This allows an attacker to look up known CVEs for that specific version.

**Port 3389 (RDP)** is open on a Linux machine — exposed here by Hyper-V's built-in integration services.

### 5.5 How Threading Works

Scanning 65,535 ports sequentially at 1s timeout per port would take ~18 hours. With 50 concurrent threads:

```text
Thread 1  → Port 1
Thread 2  → Port 2
...
Thread 50 → Port 50
[all 50 complete, next batch starts]
```

Total scan time drops to ~3 minutes — a 360x speedup.

### 5.6 Banner Grabbing

After confirming a port is open, the scanner sends an HTTP probe to retrieve the service banner:

```python
s.send(b"HEAD / HTTP/1.0\r\n\r\n")
banner = s.recv(1024).decode(errors="ignore")
```

Service banners reveal software names, versions, and OS details — useful for targeting specific vulnerabilities.

### 5.7 MITRE ATT&CK Mapping

| Technique | ID | Description |
| --- | --- | --- |
| Network Service Discovery | T1046 | Scanning all ports to enumerate running services |
| Remote Services | T1021 | Identifying SSH, RDP, and web services as potential entry points |

---

## 6. Defender Side — SOC and IDS

### 6.1 Wazuh Overview

Wazuh is an open-source Security Information and Event Management (SIEM) platform. The full stack was installed on the Ubuntu VM:

| Component | Purpose | RAM Used |
| --- | --- | --- |
| Wazuh Manager | Receives and analyzes logs | 1.9 GB |
| Wazuh Indexer | Stores and indexes alerts | 1.2 GB |
| Wazuh Dashboard | Web-based SOC UI | 170 MB |

### 6.2 How Wazuh Detected the SSH Brute Force

Every SSH login attempt generates entries in `/var/log/auth.log` on Ubuntu. Wazuh's log collector monitors this file in real time and matches entries against its rule set.

**Rules triggered during the attack:**

| Rule ID | Description | Level |
| --- | --- | --- |
| 5760 | sshd: authentication failed | 5 |
| 5503 | PAM: User login failed | 5 |
| 5501 | PAM: Login session opened | 3 |

### 6.3 How Wazuh Detected the Port Scan

The port scanner connected to multiple services in rapid succession. Wazuh detected this anomalous behavior and mapped it to the Remote Services technique in the MITRE ATT&CK framework.

### 6.4 MITRE ATT&CK Dashboard

After running both attacks, the Wazuh MITRE ATT&CK dashboard showed five techniques automatically detected:

| Technique | Triggered By |
| --- | --- |
| Valid Accounts | Successful SSH login after brute force |
| Password Guessing | Brute force failed attempts |
| SSH | SSH connections from Kali |
| Sudo and Sudo Caching | sudo commands run on Ubuntu |
| Remote Services | Port scanner connecting to multiple services |

### 6.5 Evidence from auth.log

```text
Jun 21 10:20:38 sshd: Failed password for yaseen from 172.22.225.120 port 46136
Jun 21 10:20:41 sshd: Failed password for yaseen from 172.22.225.120 port 51268
...
Jun 21 10:21:21 sshd: Accepted password for yaseen from 172.22.225.120 port 60944
```

Ubuntu logged all 20 failed attempts and the final successful login from Kali's IP.

---

## 7. Integration and Testing

### 7.1 Full SSH Brute Force Flow

```text
1.  Attacker opens Flask GUI at http://172.22.225.120:5000
2.  Configures target: 172.22.229.213:22, user: yaseen
3.  Clicks START ATTACK
4.  Flask app spawns background thread running brute force
5.  Paramiko tries each password via SSH
6.  Ubuntu logs each attempt in /var/log/auth.log
7.  Wazuh reads auth.log in real time
8.  Wazuh raises alerts on dashboard
9.  After 20 failures, password "123123" succeeds
10. Flask GUI displays PASSWORD CRACKED → 123123
11. Wazuh dashboard shows spike in authentication failure alerts
```

### 7.2 Full Port Scan Flow

```text
1.  Attacker switches to PORT SCANNER tab in Flask GUI
2.  Configures target IP and port range (1-65535)
3.  Clicks START SCAN
4.  50 threads scan all ports concurrently
5.  Open ports appear in real-time log as they are found
6.  Banner grabbing retrieves service version info
7.  Scan completes in ~3 minutes — 9 open ports found
8.  Wazuh detects rapid multi-service connections
9.  Remote Services technique appears on MITRE ATT&CK dashboard
```

### 7.3 Test Results

| Test | Result |
| --- | --- |
| Kali to Ubuntu ping | Pass (0% packet loss, ~0.4 ms) |
| SSH reachability check | Pass (port 22 open) |
| Brute force notebook | Pass (password found in 21 attempts) |
| Flask GUI brute force | Pass (live log, progress bar, result banner) |
| Port scanner — common ports | Pass (6 ports found in ~2 seconds) |
| Port scanner — 1 to 65535 | Pass (9 ports found in ~3 minutes) |
| Banner grabbing | Pass (SSH version and HTTP status retrieved) |
| Wazuh brute force detection | Pass (authentication failures detected) |
| Wazuh port scan detection | Pass (Remote Services technique detected) |
| MITRE ATT&CK mapping | Pass (T1110 Brute Force, T1046 Port Scan) |
| auth.log evidence | Pass (all attempts logged with attacker IP) |
| Timezone sync | Pass (all three systems on PKT UTC+5) |

---

## 8. Conclusion and Recommendations

### 8.1 Conclusion

This project successfully simulated a complete attack cycle — reconnaissance through initial access — in a controlled environment:

- The **port scanner** demonstrated how attackers map a target's attack surface before striking, discovering 9 open ports and service version details across 65,535 ports in under 3 minutes
- The **SSH brute force** demonstrated how an automated Python script combined with a professional GUI can systematically crack weak passwords
- The **cryptography module** proved that algorithm choice is critical — bcrypt is 127,330x slower than MD5 per attempt
- The **defender side** showed how a real SIEM (Wazuh) detects, categorizes, and logs both attacks in real time using the MITRE ATT&CK framework

### 8.2 Defense Recommendations

| Recommendation | Impact |
| --- | --- |
| Use strong passwords (not in wordlists) | Eliminates simple brute force |
| Disable password auth, use SSH keys | Makes brute force impossible |
| Enable fail2ban / Wazuh Active Response | Auto-blocks attacker IP after N failures |
| Change default SSH port (22) | Reduces automated scanning |
| Use bcrypt for all stored passwords | Makes offline cracking impractical |
| Disable unused services and close unused ports | Reduces attack surface visible to scanners |
| Monitor auth.log continuously with IDS | Enables rapid threat detection |
| Suppress service version banners | Prevents attackers from targeting specific CVEs |

### 8.3 Key Takeaway

> A password like `123123` was cracked in under 2 minutes from a 21-entry wordlist.
> The port scan mapped the entire attack surface in under 3 minutes.
> Both attacks were detected and mapped to MITRE ATT&CK automatically by Wazuh.
> Security is a combination of strong cryptography, minimal exposure, and continuous monitoring.
