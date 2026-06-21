# Project Setup Guide

## Prerequisites

### Hardware Requirements

| Resource | Minimum |
| --- | --- |
| RAM | 16 GB |
| Storage | 100 GB free |
| CPU | Quad-core |
| OS | Windows 10/11 Pro (Hyper-V required) |

### Software Requirements

- Windows Hyper-V enabled
- Python 3.10+ (on Kali VM)
- Git

---

## Step 1 — Clone the Repository

```bash
git clone <repo-url>
cd cybersecurity
```

---

## Step 2 — Enable Hyper-V

Open PowerShell as Administrator:

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

Restart your machine when prompted.

---

## Step 3 — Set Up Ubuntu VM (Victim)

### 3.1 Download Ubuntu

Download Ubuntu 22.04 LTS ISO from ubuntu.com and create a new VM in Hyper-V Manager:

- Generation: 2
- RAM: 1 GB startup, 5 GB max (Dynamic Memory)
- Storage: 50 GB
- Network: Default Switch

### 3.2 Install Ubuntu

Boot from ISO and complete installation. Create a user (note the username and password).

### 3.3 Enable SSH

```bash
sudo apt update
sudo apt install openssh-server -y
sudo systemctl enable ssh
sudo systemctl start ssh
```

### 3.4 Verify SSH

```bash
sudo systemctl status ssh
ls -lh /var/log/auth.log
ip a
```

Note the Ubuntu IP address — you will need it later.

---

## Step 4 — Install Wazuh on Ubuntu (All-in-One)

```bash
# Expand disk first if needed (Ubuntu must have 50 GB free)
curl -sO https://packages.wazuh.com/4.14/wazuh-install.sh
sudo bash ./wazuh-install.sh -a -i
```

Installation takes 10–15 minutes. After completion verify all services:

```bash
sudo systemctl status wazuh-manager
sudo systemctl status wazuh-indexer
sudo systemctl status wazuh-dashboard
```

Access the Wazuh dashboard from your Windows browser:

```
https://<ubuntu-ip>
Username: admin
Password: admin
```

---

## Step 5 — Set Up Kali Linux VM (Attacker)

### 5.1 Download Kali Hyper-V Image

Go to kali.org/get-kali → Virtual Machines → Hyper-V → Download the `.zip`

Extract it to a **local path** (not OneDrive or network drive):

```
C:\VMs\kali-attacker\
```

### 5.2 Create the VM

Run the included `create-vm.ps1` script in Admin PowerShell from the extracted folder:

```powershell
cd C:\VMs\kali-attacker\kali-linux-<version>
.\create-vm.ps1
```

### 5.3 Configure Memory

```powershell
Set-VMMemory -VMName "kali-linux-<version>" `
             -DynamicMemoryEnabled $true `
             -MinimumBytes 1GB `
             -StartupBytes 2GB `
             -MaximumBytes 3GB
```

### 5.4 Connect to Default Switch

```powershell
Connect-VMNetworkAdapter -VMName "kali-linux-<version>" -SwitchName "Default Switch"
```

### 5.5 Start Kali

```powershell
Start-VM -Name "kali-linux-<version>"
vmconnect localhost "kali-linux-<version>"
```

Default credentials:

```
Username: kali
Password: kali
```

---

## Step 6 — Verify Network Connectivity

Get Kali IP:

```bash
ip a show eth0 | grep inet
```

From Kali, ping Ubuntu:

```bash
ping <ubuntu-ip> -c 4
```

Expect 0% packet loss.

---

## Step 7 — Set Up Python Environment on Kali

```bash
python3 -m venv ~/project-env
source ~/project-env/bin/activate
pip install flask paramiko bcrypt notebook
```

---

## Step 8 — Transfer Project Files to Kali

From Windows PowerShell:

```powershell
scp shared/crypto_demo.py kali@<kali-ip>:~/crypto_demo.py
scp attacker/app.py kali@<kali-ip>:~/app.py
scp attacker/port_scanner.py kali@<kali-ip>:~/port_scanner.py
scp attacker/wordlists/common_passwords.txt kali@<kali-ip>:~/wordlist.txt
scp attacker/attack.ipynb kali@<kali-ip>:~/attack.ipynb
```

Then on Kali, organize the files:

```bash
mkdir -p ~/attacker/templates
mv ~/app.py ~/attacker/
mv ~/port_scanner.py ~/attacker/
mv ~/attack.ipynb ~/attacker/
cp ~/wordlist.txt ~/attacker/wordlist.txt
```

Transfer the HTML template:

```powershell
scp "attacker/templates/index.html" kali@<kali-ip>:~/attacker/templates/index.html
```

---

## Step 9 — Add Target Password to Wordlist

On Ubuntu, set a password that exists in the wordlist:

```bash
sudo passwd <username>
# Set it to: 123123
```

Or add your own password to `wordlist.txt` on Kali.

---

## Step 10 — Run the Project

### Option A — Jupyter Notebook

```bash
source ~/project-env/bin/activate
cd ~/attacker
jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser
```

Open in Windows browser: `http://<kali-ip>:8888`

Open `attack.ipynb` and run cells top to bottom.

### Option B — Flask GUI (Recommended for Demo)

```bash
source ~/project-env/bin/activate
cd ~/attacker
python3 app.py
```

Open in Windows browser: `http://<kali-ip>:5000`

The dashboard has two tabs:

- **SSH BRUTE FORCE** — configure target IP, username, and wordlist path, then click **START ATTACK**
- **PORT SCANNER** — configure target IP and port range (`common`, `1-1024`, or `1-65535`), then click **START SCAN**

---

## Step 11 — Monitor on Wazuh Dashboard

While the attack runs, open the Wazuh dashboard:

```
https://<ubuntu-ip>
```

Navigate to:

```
Threat Intelligence → Threat Hunting → Events
Add column: data.srcip
```

You will see real-time SSH authentication failure alerts from the attacker IP.

---

## Project Structure

```
cybersecurity/
├── attacker/
│   ├── app.py                        # Flask attacker GUI
│   ├── port_scanner.py               # Port scanner module
│   ├── attack.ipynb                  # Jupyter notebook
│   ├── templates/
│   │   └── index.html                # Dashboard UI (two tabs)
│   └── wordlists/
│       └── common_passwords.txt      # Password wordlist
├── shared/
│   └── crypto_demo.py                # Cryptography module
├── report/
│   └── report.md                     # Project report
├── SETUP.md                          # This file
└── PROJECT_PLAN.md                   # Project plan and progress
```

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Kali kernel panic on boot | Move VHDX to local path (not OneDrive) |
| Kali out of memory on boot | Increase startup RAM to 2 GB |
| VMs cannot ping each other | Use Default Switch — avoid Internal/Private switch |
| `pip install` blocked on Kali | Use virtual environment: `python3 -m venv ~/project-env` |
| Wazuh install fails (RAM check) | Use `-i` flag: `sudo bash wazuh-install.sh -a -i` |
| Wordlist not found in notebook | Use absolute path: `/home/kali/wordlist.txt` |
| Wazuh dashboard not loading | Wait 2–3 minutes after boot — indexer takes time to start |
| Port scanner results table empty | Scroll down in the browser — table renders after scan completes |
| Port scan takes too long | Use `common` or `1-1024` instead of `1-65535` for a quicker scan |
