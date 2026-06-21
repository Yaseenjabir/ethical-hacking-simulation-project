"""
Port Scanner Module — TCP Connect Scan
Scans a target for open ports and grabs service banners.
"""

import socket
import threading
import datetime
import queue


# Well-known ports and their service names
COMMON_PORTS = {
    21:    "FTP",
    22:    "SSH",
    23:    "Telnet",
    25:    "SMTP",
    53:    "DNS",
    80:    "HTTP",
    110:   "POP3",
    139:   "NetBIOS",
    143:   "IMAP",
    443:   "HTTPS",
    445:   "SMB",
    3306:  "MySQL",
    3389:  "RDP",
    5432:  "PostgreSQL",
    8080:  "HTTP-Alt",
    8443:  "HTTPS-Alt",
    9200:  "Wazuh Indexer",
    55000: "Wazuh Manager API",
}


def get_service_name(port):
    return COMMON_PORTS.get(port, "Unknown")


def grab_banner(ip, port, timeout=2):
    """Try to read the service banner — what the service announces about itself."""
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((ip, port))
        # Send a generic probe to trigger a response
        s.send(b"HEAD / HTTP/1.0\r\n\r\n")
        banner = s.recv(1024).decode(errors="ignore").strip()
        s.close()
        # Return first line only
        return banner.split("\n")[0].strip() if banner else ""
    except Exception:
        return ""


def scan_port(ip, port, timeout, results, log_queue):
    """Attempt a TCP connection to a single port."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, port))
        s.close()

        service = get_service_name(port)
        ts = datetime.datetime.now().strftime("%H:%M:%S")

        if result == 0:
            banner = grab_banner(ip, port, timeout)
            entry = {
                "port":    port,
                "state":   "OPEN",
                "service": service,
                "banner":  banner,
                "time":    ts,
            }
            results.append(entry)
            banner_str = f" | {banner}" if banner else ""
            log_queue.put(f"OPEN    {ts}  Port {port:<6} {service:<20}{banner_str}")
        else:
            log_queue.put(f"CLOSED  {ts}  Port {port:<6} {service}")

    except Exception as e:
        log_queue.put(f"ERROR   Port {port} — {e}")


def run_scan(ip, ports, timeout=1, max_threads=50, log_queue=None, stop_event=None):
    """
    Run a threaded TCP connect scan across a list of ports.
    Threads allow scanning multiple ports simultaneously — much faster than sequential.
    """
    results = []
    semaphore = threading.Semaphore(max_threads)

    def worker(port):
        if stop_event and stop_event.is_set():
            return
        with semaphore:
            scan_port(ip, port, timeout, results, log_queue)

    log_queue.put(f"INFO: Scanning {ip} — {len(ports)} ports")
    log_queue.put(f"INFO: Threads: {max_threads} | Timeout: {timeout}s")
    log_queue.put(f"INFO: Scan started at {datetime.datetime.now().strftime('%H:%M:%S')}")

    threads = []
    for port in ports:
        t = threading.Thread(target=worker, args=(port,), daemon=True)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    open_ports = [r for r in results if r["state"] == "OPEN"]

    log_queue.put(f"INFO: Scan complete — {len(open_ports)} open ports found")
    log_queue.put("DONE")

    return sorted(open_ports, key=lambda x: x["port"])


def parse_port_range(port_input):
    """
    Parse port input string into a list of ports.
    Examples:
        "22"          → [22]
        "22,80,443"   → [22, 80, 443]
        "1-1024"      → [1, 2, ..., 1024]
        "common"      → list of common ports
    """
    if port_input.strip().lower() == "common":
        return list(COMMON_PORTS.keys())

    ports = []
    for part in port_input.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            ports.extend(range(int(start), int(end) + 1))
        else:
            ports.append(int(part))

    return ports


if __name__ == "__main__":
    import sys
    import queue as q

    target = sys.argv[1] if len(sys.argv) > 1 else "172.22.229.213"
    lq = q.Queue()

    ports = parse_port_range("common")
    results = run_scan(target, ports, timeout=1, max_threads=50, log_queue=lq)

    while not lq.empty():
        print(lq.get())

    print("\n--- OPEN PORTS SUMMARY ---")
    for r in results:
        print(f"  {r['port']:<6} {r['service']:<20} {r['banner']}")
