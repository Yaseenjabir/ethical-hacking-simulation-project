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
6. [Web Login Brute Force](#6-web-login-brute-force)
7. [SQL Injection](#7-sql-injection)
8. [Defender Side — SOC and IDS](#8-defender-side--soc-and-ids)
9. [Integration and Testing](#9-integration-and-testing)
10. [Conclusion and Recommendations](#10-conclusion-and-recommendations)

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
| Web Login Brute Force | HTTP POST form attacks via requests library | T1110.001 |
| SQL Injection | Login bypass and UNION data extraction via requests | T1190 |

These attacks represent the reconnaissance, initial access, and exploitation phases of a real attack — and are all detectable by a SIEM.

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

## 6. Web Login Brute Force

### 6.1 What Is Web Login Brute Force?

Web login brute force targets the application layer instead of the network protocol layer. Rather than speaking SSH directly, the attacker submits HTTP POST requests to a login form — exactly as a browser would — and detects success by the server's response code.

This maps to **MITRE ATT&CK T1110.001 — Brute Force: Password Guessing**.

### 6.2 Target Setup — PHP Login Page on Apache

A simple vulnerable login page was deployed on Ubuntu using PHP and Apache:

```text
Stack:  Apache 2 + PHP 8.1
Port:   8888 (port 80 occupied by Wazuh)
URL:    http://172.22.229.213:8888/login.php
Creds:  admin / 123123
```

The login page returns:

- `200 OK` with "Invalid credentials" text on failure
- `302 Redirect` to `/dashboard.php` on success

### 6.3 How the Attack Works

```text
Kali → POST /login.php {username=admin, password=123456} → Ubuntu:8888
       ← 200 OK "Invalid credentials"   (failed)
Kali → POST /login.php {username=admin, password=password} → Ubuntu:8888
       ← 200 OK "Invalid credentials"   (failed)
...
Kali → POST /login.php {username=admin, password=123123} → Ubuntu:8888
       ← 302 Found → /dashboard.php     (SUCCESS)
```

The key implementation detail is `allow_redirects=False` in the requests call. Without it, both success and failure return `200 OK` (after following the redirect) and are indistinguishable:

```python
resp = requests.post(url, data={"username": u, "password": p}, allow_redirects=False)
if resp.status_code in (301, 302):
    return True   # redirected = login succeeded
if "Invalid credentials" in resp.text:
    return False  # error text = login failed
```

### 6.4 Key Difference vs SSH Brute Force

| | SSH Brute Force | Web Brute Force |
| --- | --- | --- |
| Protocol | TCP + SSH | HTTP POST |
| Library | paramiko | requests |
| Success indicator | No exception raised | 302 redirect |
| Failure indicator | AuthenticationException | 200 + error text |
| Logged in | /var/log/auth.log | /var/log/apache2/access.log |
| User-Agent visible | No | Yes — `python-requests/2.34.2` |

The User-Agent `python-requests/2.34.2` is a detection signal — a real attacker would spoof this to look like a normal browser.

### 6.5 Scan Results

```text
Target:   http://172.22.229.213:8888/login.php
Username: admin
Wordlist: 21 passwords
Duration: ~1 second (HTTP is faster than SSH handshake)

FAILED [001] — 123456
FAILED [002] — password
...
FAILED [020] — shadow
SUCCESS [021] — 123123
```

### 6.6 Wazuh Detection — Custom Rules

Apache logs are not monitored by Wazuh by default. Two changes were made on Ubuntu:

**1. Added Apache log to ossec.conf:**

```xml
<localfile>
  <log_format>apache</log_format>
  <location>/var/log/apache2/access.log</location>
</localfile>
```

**2. Written custom rules in local_rules.xml:**

```xml
<rule id="100002" level="3">
  <if_sid>31108</if_sid>
  <url>/login.php</url>
  <description>Web login page request detected</description>
</rule>

<rule id="100003" level="10" frequency="5" timeframe="30">
  <if_matched_sid>100002</if_matched_sid>
  <same_srcip />
  <description>Web brute force — multiple login attempts from same IP</description>
  <mitre>
    <id>T1110.001</id>
  </mitre>
</rule>
```

Rule 100002 fires on every POST to `/login.php`. Rule 100003 fires at **level 10** after 5 hits from the same IP in 30 seconds — our 21-attempt attack triggers it four times.

### 6.7 Evidence from Apache Access Log

```text
172.22.225.120 - [21/Jun/2026:12:25:22] "POST /login.php HTTP/1.1" 200 664 "python-requests/2.34.2"
172.22.225.120 - [21/Jun/2026:12:25:22] "POST /login.php HTTP/1.1" 200 664 "python-requests/2.34.2"
...
172.22.225.120 - [21/Jun/2026:12:25:22] "POST /login.php HTTP/1.1" 302 400 "python-requests/2.34.2"
```

21 POST requests from `172.22.225.120`, all within 1 second, ending with a `302` — the fingerprint of a successful web brute force.

---

## 7. SQL Injection

### 7.1 What is SQL Injection

SQL injection is a vulnerability where user input is inserted directly into a SQL query without sanitization. The attacker supplies SQL syntax as input, changing the logic of the query.

The vulnerable PHP code on the victim:

```php
$query = "SELECT * FROM users WHERE username='$username' AND password='$password'";
```

When `$username = admin' OR '1'='1 #`, the query becomes:

```sql
SELECT * FROM users WHERE username='admin' OR '1'='1' #' AND password='...'
```

The `OR '1'='1'` is always true. The `#` comments out the rest. The WHERE clause matches every row — login succeeds without knowing any password.

### 7.2 Attack Phases

The SQL injection module ran three phases automatically:

**Phase 0 — Probe:** Sent a single quote `'` to detect SQL errors in the response (error-based detection).

**Phase 1 — Login Bypass (6 payloads):**

| Payload | Technique |
| --- | --- |
| `' OR '1'='1' #` | Always-true OR condition |
| `admin' #` | Comment out password check |
| `' OR 1=1 #` | Numeric always-true |
| `admin' OR '1'='1` | No comment needed — string closes naturally |
| `' OR 'x'='x' #` | String always-true variant |
| `" OR "1"="1" #` | Double-quote variant |

**Phase 2 — UNION Extraction (6 payloads):** Once injection was confirmed, UNION SELECT payloads dumped data from the `users` table via the vulnerable `search.php` page:

```sql
' UNION SELECT username,password,role FROM users #
```

This appends a second SELECT to the original query and returns its results alongside the page output — leaking all usernames, passwords, emails, roles, and even the MySQL server version.

### 7.3 Wazuh Detection — Built-in Rules

SQL injection payloads contain distinctive SQL keywords. Wazuh's built-in web rules matched them from the Apache access log automatically — **no custom rule was needed**:

| Rule ID | Level | Description |
| --- | --- | --- |
| 31103 | 7 | SQL injection attempt (OR/UNION keywords detected) |
| 31164 | 6 | SQL injection pattern matched |
| 31106 | 6 | Web attack returned 200 success |
| 31122 | 5 | 500 error during probe phase |

This contrasts with web brute force — which requires a custom frequency rule because the individual requests look identical to normal login attempts.

### 7.4 Why SQL Injection Works

The root cause is **string concatenation** instead of **parameterized queries**:

| Vulnerable (PHP) | Secure (PHP) |
| --- | --- |
| `"SELECT * WHERE user='$input'"` | `$stmt = $pdo->prepare("SELECT * WHERE user=?"); $stmt->execute([$input]);` |

Parameterized queries send the SQL structure and the data separately — the database never interprets user input as SQL syntax.

---

## 8. Defender Side — SOC and IDS

### 8.1 Wazuh Overview

Wazuh is an open-source Security Information and Event Management (SIEM) platform. The full stack was installed on the Ubuntu VM:

| Component | Purpose | RAM Used |
| --- | --- | --- |
| Wazuh Manager | Receives and analyzes logs | 1.9 GB |
| Wazuh Indexer | Stores and indexes alerts | 1.2 GB |
| Wazuh Dashboard | Web-based SOC UI | 170 MB |

### 8.2 How Wazuh Detected the SSH Brute Force

Every SSH login attempt generates entries in `/var/log/auth.log` on Ubuntu. Wazuh's log collector monitors this file in real time and matches entries against its rule set.

**Rules triggered during the attack:**

| Rule ID | Description | Level |
| --- | --- | --- |
| 5760 | sshd: authentication failed | 5 |
| 5503 | PAM: User login failed | 5 |
| 5501 | PAM: Login session opened | 3 |

### 8.3 How Wazuh Detected the Port Scan

The port scanner connected to multiple services in rapid succession. Wazuh detected this anomalous behavior and mapped it to the Remote Services technique in the MITRE ATT&CK framework.

### 8.4 MITRE ATT&CK Dashboard

After running both attacks, the Wazuh MITRE ATT&CK dashboard showed five techniques automatically detected:

| Technique | Triggered By |
| --- | --- |
| Valid Accounts | Successful SSH login after brute force |
| Password Guessing | Brute force failed attempts |
| SSH | SSH connections from Kali |
| Sudo and Sudo Caching | sudo commands run on Ubuntu |
| Remote Services | Port scanner connecting to multiple services |

### 8.5 Evidence from auth.log

```text
Jun 21 10:20:38 sshd: Failed password for yaseen from 172.22.225.120 port 46136
Jun 21 10:20:41 sshd: Failed password for yaseen from 172.22.225.120 port 51268
...
Jun 21 10:21:21 sshd: Accepted password for yaseen from 172.22.225.120 port 60944
```

Ubuntu logged all 20 failed attempts and the final successful login from Kali's IP.

---

## 9. Integration and Testing

### 9.1 Full SSH Brute Force Flow

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

### 9.2 Full Port Scan Flow

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

### 9.3 Test Results

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

## 10. Conclusion and Recommendations

### 10.1 Conclusion

This project successfully simulated a complete attack cycle — reconnaissance through initial access — in a controlled environment:

- The **port scanner** demonstrated how attackers map a target's attack surface before striking, discovering 9 open ports and service version details across 65,535 ports in under 3 minutes
- The **SSH brute force** demonstrated how an automated Python script combined with a professional GUI can systematically crack weak passwords over the SSH protocol
- The **web login brute force** demonstrated the same concept at the application layer — cracking an HTTP login form in under 1 second using Python's requests library
- The **cryptography module** proved that algorithm choice is critical — bcrypt is 127,330x slower than MD5 per attempt
- The **defender side** showed how a real SIEM (Wazuh) detects all three attacks — including a custom rule written from scratch to detect web brute force — and maps them to MITRE ATT&CK in real time

### 10.2 Defense Recommendations

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

### 10.3 Key Takeaway

> A password like `123123` was cracked in under 2 minutes from a 21-entry wordlist.
> The port scan mapped the entire attack surface in under 3 minutes.
> Both attacks were detected and mapped to MITRE ATT&CK automatically by Wazuh.
> Security is a combination of strong cryptography, minimal exposure, and continuous monitoring.
