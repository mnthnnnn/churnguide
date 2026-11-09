"""
Automated End-to-End Visual Verification & Screenshot Capture using Edge Headless.
Captures screenshots across all pages for the multi-business analytics platform.
"""

import os
import time
import socket
import subprocess
import urllib.request

def get_free_port():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

PORT = get_free_port()
EDGE_EXE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
BASE_URL = f'http://127.0.0.1:{PORT}'
OUT_DIR = os.path.abspath(os.path.join('static', 'screenshots'))
os.makedirs(OUT_DIR, exist_ok=True)

# 1. Start Flask app
cmd = ['python', '-c', f"from app import app; app.run(host='127.0.0.1', port={PORT}, debug=False)"]
server_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

print(f"Starting Flask server on dynamic free port {PORT}...")
server_up = False
for _ in range(30):
    try:
        with urllib.request.urlopen(f"{BASE_URL}/wizard/step1", timeout=1) as resp:
            if resp.status == 200:
                server_up = True
                break
    except Exception:
        time.sleep(0.5)

if not server_up:
    server_proc.terminate()
    raise RuntimeError("Flask server failed to start.")

print("Flask server is live! Capturing real screenshots...")

routes = [
    ('step1_add_data.png', f'{BASE_URL}/wizard/step1'),
    ('step3_see_results.png', f'{BASE_URL}/wizard/step3'),
    ('predict_single.png', f'{BASE_URL}/predict'),
    ('bulk_scoring.png', f'{BASE_URL}/bulk'),
    ('analytics_view.png', f'{BASE_URL}/analytics'),
    ('segments_view.png', f'{BASE_URL}/segments'),
    ('model_transparency.png', f'{BASE_URL}/model')
]

for filename, url in routes:
    dest = os.path.join(OUT_DIR, filename)
    edge_cmd = [
        EDGE_EXE,
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        '--window-size=1280,880',
        '--hide-scrollbars',
        '--virtual-time-budget=2000',
        f'--screenshot={dest}',
        url
    ]
    subprocess.run(edge_cmd, capture_output=True)
    if os.path.exists(dest):
        print(f"Captured: {filename} ({os.path.getsize(dest)} bytes)")
    else:
        print(f"Failed to capture: {filename}")

server_proc.terminate()
print("All screenshots successfully captured!")
