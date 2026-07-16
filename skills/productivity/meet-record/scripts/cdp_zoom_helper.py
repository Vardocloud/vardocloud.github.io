#!/usr/bin/env python3
"""
CDP WebSocket helper for Zoom meeting control.
Reusable across sessions — import and use.

Usage:
    from cdp_zoom_helper import ZoomController
    
    zoom = ZoomController(port=9334)
    zoom.navigate("https://app.zoom.us/wc/join/123456789?pwd=abc123")
    zoom.fill_name("Sudenaz")
    zoom.click_button("Mute")
    zoom.click_button("Stop Video")
    zoom.click_button("Join")
    zoom.click_button("Computer Audio")
    print(zoom.get_page_text())
"""

import websocket
import json
import time
import urllib.request


class ZoomController:
    """Controls a Chrome tab via CDP WebSocket for Zoom meeting interaction."""

    def __init__(self, port=9334, timeout=15):
        self.port = port
        self.timeout = timeout
        self.ws = None
        self._cmd_id = 0

    def _find_tab(self):
        """Find the first page tab (not service worker, not blank)."""
        url = f"http://localhost:{self.port}/json"
        tabs = json.loads(urllib.request.urlopen(url, timeout=5).read())
        # Prefer a tab that already has a Zoom URL
        for t in tabs:
            if t.get("type") == "page" and ("zoom.us" in t.get("url", "") or "app.zoom" in t.get("url", "")):
                return t["id"]
        # Fall back to last page tab
        for t in tabs:
            if t.get("type") == "page":
                return t["id"]
        return None

    def connect(self, target_id=None):
        """Connect to Chrome CDP WebSocket. If no target_id, auto-finds a page tab."""
        if target_id is None:
            target_id = self._find_tab()
        if target_id is None:
            raise RuntimeError("No page tab found on CDP port " + str(self.port))
        ws_url = f"ws://localhost:{self.port}/devtools/page/{target_id}"
        self.ws = websocket.create_connection(ws_url, timeout=self.timeout)
        self._send("Page.enable")
        self._send("Runtime.enable")
        return self

    def close(self):
        if self.ws:
            self.ws.close()

    def _send(self, method, params=None):
        """Send CDP command and return response."""
        self._cmd_id += 1
        msg = {"id": self._cmd_id, "method": method}
        if params:
            msg["params"] = params
        self.ws.send(json.dumps(msg))
        while True:
            resp = json.loads(self.ws.recv())
            if resp.get("id") == self._cmd_id:
                return resp

    def evaluate(self, js, await_promise=False):
        """Evaluate JavaScript in the page context."""
        r = self._send("Runtime.evaluate", {
            "expression": js,
            "returnByValue": True,
            "awaitPromise": await_promise
        })
        return r.get("result", {}).get("result", {}).get("value")

    def navigate(self, url):
        """Navigate the page to a URL."""
        r = self._send("Page.navigate", {"url": url})
        return r

    def get_page_text(self):
        """Get visible text content of the page."""
        return self.evaluate("document.body ? document.body.innerText.substring(0, 5000) : 'no body'")

    def get_title(self):
        """Get page title."""
        return self.evaluate("document.title")

    def get_url(self):
        """Get current URL."""
        return self.evaluate("window.location.href")

    def click_button(self, text_contains):
        """Click a button whose text includes the given string."""
        js = f"""
        (() => {{
            var btns = document.querySelectorAll('button');
            for (var b of btns) {{
                if (b.innerText.includes('{text_contains}')) {{
                    b.click();
                    return 'CLICKED: ' + b.innerText.trim().substring(0,50);
                }}
            }}
            // Try aria-label
            for (var b of btns) {{
                var label = b.getAttribute('aria-label') || '';
                if (label.includes('{text_contains}')) {{
                    b.click();
                    return 'CLICKED (aria): ' + label.substring(0,50);
                }}
            }}
            return 'NOT FOUND: {text_contains}';
        }})()
        """
        return self.evaluate(js)

    def fill_input(self, element_id, value):
        """Fill an input field (works with React onChange)."""
        js = f"""
        (() => {{
            var inp = document.getElementById('{element_id}');
            if (!inp) return 'NOT FOUND: {element_id}';
            inp.focus();
            inp.value = '';
            var nativeSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;
            nativeSetter.call(inp, '{value}');
            inp.dispatchEvent(new Event('input', {{bubbles: true}}));
            inp.dispatchEvent(new Event('change', {{bubbles: true}}));
            return 'SET: ' + inp.value;
        }})()
        """
        return self.evaluate(js)

    def fill_name(self, name):
        """Fill Zoom meeting display name."""
        return self.fill_input("input-for-name", name)

    def check_buttons(self):
        """List all buttons with their text and disabled state."""
        return self.evaluate("""
        (() => {
            var btns = document.querySelectorAll('button');
            return Array.from(btns).map(function(b) {
                var t = (b.innerText || b.getAttribute('aria-label') || '').trim().substring(0,40);
                return (t ? t + (b.disabled ? ' [DIS]' : ' [ENA]') : '');
            }).filter(t => t).join('\\n') || 'no buttons';
        })()
        """)

    def check_inputs(self):
        """List all non-hidden inputs."""
        return self.evaluate("""
        (() => {
            var inputs = document.querySelectorAll('input:not([type=hidden])');
            return Array.from(inputs).map(function(inp) {
                return 'id=' + inp.id + ' type=' + inp.type + ' val=' + (inp.value || '').substring(0,20);
            }).join('\\n') || 'no visible inputs';
        })()
        """)

    def wait_for_text(self, text_contains, timeout=15):
        """Wait until text appears on the page, polling every second."""
        for i in range(timeout):
            text = self.get_page_text() or ""
            if text_contains in text:
                return True
            time.sleep(1)
        return False


def get_chrome_tabs(port=9334):
    """List all tabs on a Chrome CDP port."""
    url = f"http://localhost:{port}/json"
    tabs = json.loads(urllib.request.urlopen(url, timeout=5).read())
    for t in tabs:
        print(f"  [{t['id'][:20]}...] {t.get('title','?')[:40]} | {t.get('url','?')[:60]}")
    return tabs


def check_pulse_sinks():
    """Check PulseAudio sinks and which Chrome is connected to which."""
    import subprocess
    try:
        r = subprocess.run(["pactl", "list", "sinks", "short"],
                         capture_output=True, text=True, timeout=5)
        print("SINKS:", r.stdout)
        r = subprocess.run(["pactl", "list", "sink-inputs"],
                         capture_output=True, text=True, timeout=5)
        print("SINK INPUTS:", r.stdout)
    except FileNotFoundError:
        # Custom pulseaudio path
        import os
        extract = "/tmp/pulseaudio_extract"
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = f"{extract}/usr/lib/x86_64-linux-gnu:{extract}/usr/lib/x86_64-linux-gnu/pulseaudio:{extract}/usr/lib/pulse-17.0+dfsg1/modules"
        env["PULSE_SERVER"] = "unix:/tmp/pulse-PKdhtXMmr18n/native"
        r = subprocess.run([f"{extract}/usr/bin/pactl", "list", "sinks", "short"],
                         capture_output=True, text=True, timeout=5, env=env)
        print("SINKS:", r.stdout)
        r = subprocess.run([f"{extract}/usr/bin/pactl", "list", "sink-inputs"],
                         capture_output=True, text=True, timeout=5, env=env)
        print("SINK INPUTS:", r.stdout)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  cdp_zoom_helper.py <port> check       # Check tabs and pulse state")
        print("  cdp_zoom_helper.py <port> status      # Check page status")
        print("  cdp_zoom_helper.py <port> navigate <url>  # Navigate to URL")
        sys.exit(1)
    
    port = int(sys.argv[1])
    action = sys.argv[2] if len(sys.argv) > 2 else "status"
    
    try:
        zoom = ZoomController(port=port).connect()
        
        if action == "check":
            print("=== TABS ===")
            get_chrome_tabs(port)
            print("\n=== PULSE ===")
            check_pulse_sinks()
        elif action == "status":
            print(f"Title: {zoom.get_title()}")
            print(f"URL: {zoom.get_url()[:100]}")
            print(f"\nButtons:\n{zoom.check_buttons()}")
            print(f"\nInputs:\n{zoom.check_inputs()}")
            print(f"\nPage text:\n{zoom.get_page_text()[:800]}")
        elif action == "navigate" and len(sys.argv) > 3:
            url = sys.argv[3]
            print(f"Navigating to: {url}")
            zoom.navigate(url)
        else:
            print(f"Unknown action: {action}")
        
        zoom.close()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
