#!/usr/bin/env python3
import json, os, subprocess, time, urllib.request, websocket

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 9336
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

        errors = []
        exceptions = []

        def drain():
            ws.settimeout(0.3)
            for _ in range(20):
                try:
                    msg = json.loads(ws.recv())
                    if msg.get("method") == "Runtime.consoleAPICalled" and msg["params"].get("type") == "error":
                        text = " ".join(str(i.get("value", i.get("description", ""))) for i in msg["params"].get("args", []))
                        errors.append(text)
                    elif msg.get("method") == "Runtime.exceptionThrown":
                        ex = msg["params"]["exceptionDetails"]
                        exceptions.append(f"{ex.get('text','')} {ex.get('exception',{}).get('description','')}")
                except websocket._exceptions.WebSocketTimeoutException:
                    break

        ws.send(json.dumps({"id": req_id, "method": "Runtime.evaluate", "params": {"expression": "Object.keys(app)", "returnByValue": True}}))
        req_id += 1
        r0 = recv_until(ws, req_id-1, timeout=5)
        print("app keys:", r0.get("result",{}).get("result",{}).get("value",[]) if r0 else "none")

        expr = """
        app.view = 'catalog';
        ['cs101','cs201','math201','eng102'].forEach(id => { if (!app.selectedIds.includes(id)) app.selectedIds.push(id); });
        app.view = 'builder';
        generateSchedules();
        JSON.stringify({ count: app.builder.generated.length, firstScore: app.builder.generated[0]?.score });
        """
        ws.send(json.dumps({"id": req_id, "method": "Runtime.evaluate", "params": {"expression": expr, "returnByValue": True}}))
        req_id += 1
        result = recv_until(ws, req_id-1, timeout=5)
        drain()

        print("Errors:", errors)
        print("Exceptions:", exceptions)
        if result:
            print("Full result:", json.dumps(result, indent=2)[:1000])
        else:
            print("No result")

        # Check render output length
        ws.send(json.dumps({"id": req_id, "method": "Runtime.evaluate", "params": {"expression": "document.getElementById('app').innerHTML.length", "returnByValue": True}}))
        req_id += 1
        r2 = recv_until(ws, req_id-1, timeout=5)
        print("Rendered HTML length:", r2.get("result",{}).get("result",{}).get("value",0) if r2 else "none")

        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    main()
