# focus_app.py
import os, time, csv, subprocess, threading, serial, sys
import pandas as pd
from flask import Flask, jsonify, send_file

# ----- Config -----
PORT = "/dev/ttyACM0"   # change if needed
BAUD = 9600
CSV_PATH = "focus_log.csv"
ALERT_WAV = "/home/pi/alert.wav"
USE_SOUND = os.path.exists(ALERT_WAV)
USE_TOAST = True
ALERT_MIN_GAP_S = 30
# ------------------

app = Flask(__name__)
last_alert = 0

def ensure_csv():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            csv.writer(f).writerow(["timestamp","state"])

def play_sound():
    if USE_SOUND:
        try: subprocess.run(["aplay", ALERT_WAV], check=False)
        except Exception: pass

def toast(msg: str):
    if USE_TOAST:
        try: subprocess.run(["notify-send", "Focus Assistant", msg], check=False)
        except Exception: pass

def open_serial(port: str, baud: int, tries: int = 10, delay_s: float = 2.0):
    for i in range(tries):
        try:
            ser = serial.Serial(port, baud, timeout=2)
            time.sleep(2)
            return ser
        except Exception as e:
            print(f"[focus_app] Serial open failed ({i+1}/{tries}): {e}")
            time.sleep(delay_s)
    print("[focus_app] Could not open serial port. Exiting.")
    sys.exit(1)

def logger_thread():
    global last_alert
    ensure_csv()
    ser = open_serial(PORT, BAUD)
    print(f"[focus_app] Logging from {PORT} @ {BAUD} → {CSV_PATH}")

    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        while True:
            try:
                line = ser.readline().decode(errors="ignore").strip()
                if not line:
                    continue
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                print(ts, line)
                writer.writerow([ts, line])
                f.flush()

                if line == "DISTRACTED":
                    now = time.time()
                    if now - last_alert >= ALERT_MIN_GAP_S:
                        play_sound()
                        toast("Away > 5 minutes — time to return!")
                        last_alert = now
            except Exception as e:
                print(f"[focus_app] Logger error: {e}")
                time.sleep(1)

def read_df():
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame(columns=["timestamp","state"])
    try:
        return pd.read_csv(CSV_PATH)
    except Exception:
        return pd.DataFrame(columns=["timestamp","state"])

@app.route("/stats")
def stats():
    df = read_df()
    if df.empty:
        return jsonify({
            "focus_min":0,"warning_min":0,"short_break_min":0,
            "away_min":0,"distracted_events":0,"rows":0
        })
    secs_per_row = 0.2
    focus_sec = (df["state"] == "FOCUS").sum() * secs_per_row
    warn_sec  = (df["state"] == "WARNING").sum() * secs_per_row
    sb_sec    = (df["state"] == "SHORT BREAK").sum() * secs_per_row
    dist_sec  = (df["state"] == "DISTRACTED").sum() * secs_per_row
    away_sec  = warn_sec + sb_sec + dist_sec
    events    = (df["state"] == "DISTRACTED").sum()
    return jsonify({
        "focus_min": round(focus_sec/60, 1),
        "warning_min": round(warn_sec/60, 1),
        "short_break_min": round(sb_sec/60, 1),
        "away_min": round(away_sec/60, 1),
        "distracted_events": int(events),
        "rows": int(len(df))
    })

@app.route("/")
def home():
    return """
    <html>
    <head><title>Focus Assistant</title></head>
    <body style="font-family:sans-serif;max-width:720px;margin:2rem auto;">
      <h1>Focus Assistant</h1>
      <p><a href="/stats">JSON stats</a> | <a href="/download">Download CSV</a></p>
      <div id="stats">Loading…</div>
      <script>
        async function refresh(){
          const r = await fetch('/stats'); const j = await r.json();
          document.getElementById('stats').innerHTML = `
            <ul>
              <li><b>Focused minutes:</b> ${j.focus_min}</li>
              <li><b>Short break minutes:</b> ${j.short_break_min}</li>
              <li><b>Warning minutes:</b> ${j.warning_min}</li>
              <li><b>Total away minutes:</b> ${j.away_min}</li>
              <li><b>Distracted events:</b> ${j.distracted_events}</li>
              <li><b>Rows logged:</b> ${j.rows}</li>
            </ul>`;
        }
        setInterval(refresh, 2000); refresh();
      </script>
    </body>
    </html>
    """

@app.route("/download")
def download():
    return send_file(CSV_PATH, as_attachment=True)

def run():
    t = threading.Thread(target=logger_thread, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    run()
