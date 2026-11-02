#!/usr/bin/env python3
import json, os, subprocess, time, urllib.request, base64, websocket

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 9337
CHROME = "/usr/bin/google-chrome"


def wait_for_devtools(timeout=15):
    url = f"http://127.0.0.1:{PORT}/json/version"
    for _ in range(timeout * 10):
        try:
            with urllib.request.urlopen(url, timeout=1) as r:
                return True
        except Exception:
            time.sleep(0.1)
    return False


def get_ws_url():
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list") as r:
        pages = json.loads(r.read())
    for p in pages:
        if p["type"] == "page":
            return p["webSocketDebuggerUrl"]
    raise RuntimeError("no page found")


def recv_until(ws, target_id, timeout=5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        ws.settimeout(max(0.1, deadline - time.time()))
        try:
            msg = json.loads(ws.recv())
        except websocket._exceptions.WebSocketTimeoutException:
            continue
        if msg.get("id") == target_id:
            return msg
    return None


def main():
    proc = subprocess.Popen([
        CHROME, "--headless", "--disable-gpu", "--no-sandbox",
        f"--remote-debugging-port={PORT}",
        "--remote-allow-origins=*",
        "--window-size=1440,900",
        "--run-all-compositor-stages-before-draw",
        "about:blank"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        wait_for_devtools()
        ws_url = get_ws_url()
        ws = websocket.create_connection(ws_url, timeout=10)
        req_id = 1
        for method in ["Runtime.enable", "Page.enable"]:
            ws.send(json.dumps({"id": req_id, "method": method}))
            req_id += 1
            recv_until(ws, req_id-1, timeout=2)
        ws.send(json.dumps({"id": req_id, "method": "Page.navigate", "params": {"url": f"file://{ROOT}/phaseD/index.html"}}))
        req_id += 1
        recv_until(ws, req_id-1, timeout=5)
        time.sleep(2.5)

        expr = """
        ['cs101','cs201','math201','eng102'].forEach(id => { if (!app.selectedIds.includes(id)) app.selectedIds.push(id); });
        app.view = 'builder';
        generateSchedules();
        'ok'
        """
        ws.send(json.dumps({"id": req_id, "method": "Runtime.evaluate", "params": {"expression": expr, "returnByValue": True}}))
        req_id += 1
        recv_until(ws, req_id-1, timeout=5)
        time.sleep(1.0)

        ws.send(json.dumps({"id": req_id, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
        req_id += 1
        result = recv_until(ws, req_id-1, timeout=5)
        data = result.get("result", {}).get("data", "")
        if data:
            path = os.path.join(ROOT, "screenshots", "builder-generated.png")
            with open(path, "wb") as f:
                f.write(base64.b64decode(data))
            print(f"saved {path}")
        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    main()
