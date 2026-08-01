#!/usr/bin/env python3
"""Print console for the Bambu Lab P1S — Oechslin perpetual calendar build.

Commands:
  status                          live printer state, temps, AMS, job progress
  upload <file>                   send a .gcode.3mf/.3mf/.gcode to printer storage
  start <file> [--plate N] [--version-tag TAG]
                                  start a print (asks for confirmation)
  watch                           follow the active job, report layer milestones
  reslice <project.3mf> [--xy-compensation N] [--plate N]
                                  headless re-slice via Bambu Studio CLI

Credentials come from .env (PRINTER_IP, PRINTER_ACCESS_CODE, PRINTER_SERIAL).

MQTT is done with paho directly: bambulabs_api 2.6.6's receive path never
merges P1 reports (its dump stays empty), so we subscribe to
device/<serial>/report ourselves, request a full "pushall" snapshot after
the subscription is granted, and merge incremental push_status updates on
top. The library is still used for FTPS uploads, which work independently.
"""

import argparse
import datetime as dt
import json
import os
import shutil
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import zipfile
from pathlib import Path

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
PRINT_LOG = PROJECT_DIR / "print-log.md"
SLICED_DIR = PROJECT_DIR / "sliced"
BAMBU_STUDIO = os.environ.get(
    "BAMBU_STUDIO_BIN",
    "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio",
)
CONNECT_TIMEOUT = 8    # seconds to establish MQTT
SNAPSHOT_TIMEOUT = 10  # seconds to receive the first full report

ACTIVE_STATES = ("RUNNING", "PAUSE", "PAUSED", "PREPARE", "SLICING")


# ---------------------------------------------------------------- connection

def load_credentials():
    load_dotenv(PROJECT_DIR / ".env")
    ip = os.environ.get("PRINTER_IP", "").strip()
    code = os.environ.get("PRINTER_ACCESS_CODE", "").strip()
    serial = os.environ.get("PRINTER_SERIAL", "").strip()
    missing = [k for k, v in [("PRINTER_IP", ip),
                              ("PRINTER_ACCESS_CODE", code),
                              ("PRINTER_SERIAL", serial)] if not v]
    if missing:
        sys.exit(f"Missing {', '.join(missing)} in {PROJECT_DIR / '.env'} — "
                 "fill them in (LAN values from the printer screen).")
    return ip, code, serial


class Link:
    """Direct LAN MQTT link: subscribe to reports, pushall, merge updates."""

    def __init__(self, ip, code, serial):
        self.ip, self.serial = ip, serial
        self.data = {}
        self._lock = threading.Lock()
        self._connected = threading.Event()
        self._snapshot = threading.Event()
        c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                        protocol=mqtt.MQTTv311)
        c.username_pw_set("bblp", code)
        c.tls_set(cert_reqs=ssl.CERT_NONE)
        c.tls_insecure_set(True)
        c.on_connect = self._on_connect
        c.on_subscribe = self._on_subscribe
        c.on_message = self._on_message
        self.client = c

    def _on_connect(self, c, u, flags, rc, props=None):
        if rc == 0 or str(rc) == "Success":
            c.subscribe(f"device/{self.serial}/report")
        # pushall waits for the subscription grant — see _on_subscribe

    def _on_subscribe(self, c, u, mid, rcs, props=None):
        self._connected.set()
        self.pushall()

    def _on_message(self, c, u, msg):
        try:
            doc = json.loads(msg.payload)
        except json.JSONDecodeError:
            return
        with self._lock:
            for k, v in doc.items():
                if isinstance(v, dict):
                    self.data.setdefault(k, {}).update(v)
        if doc.get("print", {}).get("nozzle_temper") is not None:
            self._snapshot.set()

    def pushall(self):
        self.client.publish(
            f"device/{self.serial}/request",
            json.dumps({"pushing": {"sequence_id": "1",
                                    "command": "pushall"}}))

    def publish(self, payload: dict):
        info = self.client.publish(f"device/{self.serial}/request",
                                   json.dumps(payload))
        info.wait_for_publish(timeout=5)
        return info.is_published()

    def print_data(self) -> dict:
        with self._lock:
            return dict(self.data.get("print", {}))

    def close(self):
        self.client.loop_stop()
        try:
            self.client.disconnect()
        except Exception:
            pass


def connect() -> Link:
    """Connect over LAN. Fails plainly — no silent retries."""
    ip, code, serial = load_credentials()
    link = Link(ip, code, serial)
    try:
        link.client.connect(ip, 8883, keepalive=60)
    except OSError as e:
        sys.exit(f"Printer unreachable: cannot open MQTT connection to "
                 f"{ip}:8883 ({e}). Check that the printer is on and on "
                 "this network.")
    link.client.loop_start()
    if not link._connected.wait(CONNECT_TIMEOUT):
        link.close()
        sys.exit(f"Printer unreachable: connected to {ip} but the report "
                 "subscription was not granted within "
                 f"{CONNECT_TIMEOUT}s — the access code in .env may be wrong.")
    if not link._snapshot.wait(SNAPSHOT_TIMEOUT):
        link.close()
        sys.exit(f"Printer at {ip} accepted the connection but sent no full "
                 f"status within {SNAPSHOT_TIMEOUT}s. Check the access code "
                 "and that the printer isn't mid-boot.")
    return link


# ------------------------------------------------------------------- status

def fmt_temp(v):
    return f"{v:.1f}°C" if isinstance(v, (int, float)) else "—"


def ams_slots(pd):
    """[(ams_id, tray_id, label, color, remain), ...] from print data."""
    slots = []
    for unit in pd.get("ams", {}).get("ams", []):
        uid = unit.get("id", "?")
        for tray in unit.get("tray", []):
            tid = tray.get("id", "?")
            ttype = tray.get("tray_type") or ""
            if not ttype:
                slots.append((uid, tid, "(empty)", "", None))
                continue
            sub = tray.get("tray_sub_brands") or ""
            label = f"{ttype} {sub}".strip() if sub else ttype
            slots.append((uid, tid, label, tray.get("tray_color", ""),
                          tray.get("remain")))
    return slots


def job_line(pd):
    name = pd.get("subtask_name") or pd.get("gcode_file") or ""
    return (name, pd.get("mc_percent"), pd.get("layer_num"),
            pd.get("total_layer_num"), pd.get("mc_remaining_time"))


def cmd_status(_args):
    link = connect()
    try:
        pd = link.print_data()
        state = pd.get("gcode_state", "UNKNOWN")
        print(f"State:    {state}")
        print(f"Nozzle:   {fmt_temp(pd.get('nozzle_temper'))}"
              + (f"  (target {fmt_temp(pd.get('nozzle_target_temper'))})"
                 if pd.get("nozzle_target_temper") else ""))
        print(f"Bed:      {fmt_temp(pd.get('bed_temper'))}"
              + (f"  (target {fmt_temp(pd.get('bed_target_temper'))})"
                 if pd.get("bed_target_temper") else ""))
        ch = pd.get("chamber_temper")
        if isinstance(ch, (int, float)):
            print(f"Chamber:  {fmt_temp(ch)}")
        if pd.get("wifi_signal"):
            print(f"WiFi:     {pd['wifi_signal']}")

        print("AMS slots:")
        slots = ams_slots(pd)
        if not slots:
            print("  (no AMS detected)")
        for uid, tid, label, color, remain in slots:
            extra = []
            if color:
                extra.append(f"#{color[:6]}")
            if isinstance(remain, int) and remain >= 0:
                extra.append(f"{remain}% left")
            suffix = f"  ({', '.join(extra)})" if extra else ""
            print(f"  AMS {uid} slot {tid}: {label}{suffix}")

        name, pct, layer, total, mins = job_line(pd)
        if str(state).upper() in ACTIVE_STATES:
            print("Current job:")
            print(f"  File:     {name or '—'}")
            if pct is not None:
                print(f"  Progress: {pct}%")
            if layer is not None and total:
                print(f"  Layer:    {layer}/{total}")
            if isinstance(mins, int) and mins > 0:
                print(f"  Remaining: ~{mins} min")
        else:
            print("Current job: none")
    finally:
        link.close()


# ------------------------------------------------------------------- upload

UPLOADABLE = (".gcode.3mf", ".3mf", ".gcode")


def cmd_upload(args):
    src = Path(args.file).expanduser()
    if not src.is_file():
        sys.exit(f"No such file: {src}")
    if not any(src.name.endswith(ext) for ext in UPLOADABLE):
        sys.exit(f"Refusing to upload {src.name}: expected one of {UPLOADABLE}")
    import bambulabs_api as bl
    ip, code, serial = load_credentials()
    printer = bl.Printer(ip, code, serial)  # FTPS only; no MQTT started
    print(f"Uploading {src.name} ({src.stat().st_size / 1e6:.1f} MB) over FTPS…")
    try:
        with open(src, "rb") as f:
            result = printer.upload_file(f, src.name)
    except Exception as e:
        sys.exit(f"Upload failed: {e}. Printer FTPS at {ip}:990 — check "
                 "network and access code.")
    if "226" in str(result):
        print(f"Uploaded: {src.name}")
    else:
        print(f"Upload finished with unexpected FTP status: {result}")


# -------------------------------------------------------------------- start

def log_entry(line):
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(PRINT_LOG, "a") as f:
        f.write(f"- {stamp} · {line}\n")


def cmd_start(args):
    filename = Path(args.file).name
    link = connect()
    try:
        state = str(link.print_data().get("gcode_state", "UNKNOWN")).upper()
        if state in ACTIVE_STATES:
            sys.exit(f"Printer is busy (state {state}) — not starting.")

        if args.ams_mapping:
            try:
                mapping = [int(x) for x in args.ams_mapping.split(",")]
            except ValueError:
                sys.exit(f"--ams-mapping must be comma-separated integers, "
                         f"got {args.ams_mapping!r}")
        else:
            mapping = [args.ams_slot]

        print(f"About to START PRINT: {filename} (plate {args.plate})")
        print(f"  ams_mapping = {mapping}  (T-index -> AMS tray)")
        if not args.yes:
            answer = input("Type 'yes' to start: ").strip().lower()
            if answer != "yes":
                print("Not started.")
                return
        ok = link.publish({"print": {
            "sequence_id": "10000000",
            "command": "project_file",
            "param": f"Metadata/plate_{args.plate}.gcode",
            "project_id": "0", "profile_id": "0",
            "task_id": "0", "subtask_id": "0",
            "subtask_name": filename.replace(".gcode.3mf", ""),
            "url": f"file:///sdcard/{filename}",
            "timelapse": False,
            "bed_type": "auto",
            "bed_levelling": True,
            "flow_cali": not args.no_flow_cali,
            "vibration_cali": True,
            "layer_inspect": False,
            "use_ams": not args.no_ams,
            "ams_mapping": mapping,
        }})
        if ok:
            tag = args.version_tag or "(no version tag)"
            log_entry(f"{filename} · {tag} · started (outcome pending)")
            print(f"Print command sent for {filename}. Logged to "
                  "print-log.md. Run 'watch' to follow it.")
        else:
            print("Start command could not be published — printer link "
                  "dropped. Nothing was logged.")
    finally:
        link.close()


# -------------------------------------------------------------------- watch

def cmd_watch(_args):
    link = connect()
    try:
        pd = link.print_data()
        state = str(pd.get("gcode_state", "UNKNOWN")).upper()
        name = job_line(pd)[0]
        if state not in ACTIVE_STATES:
            print(f"No active job (state {state}).")
            return
        print(f"Watching: {name or '(unnamed job)'} — Ctrl-C to stop "
              "(the print keeps running).")
        last_layer = last_bucket = last_state = last_err = None
        last_pushall = time.time()
        while True:
            pd = link.print_data()
            state = str(pd.get("gcode_state", "UNKNOWN")).upper()
            name, pct, layer, total, mins = job_line(pd)
            stamp = dt.datetime.now().strftime("%H:%M:%S")

            if state != last_state:
                print(f"[{stamp}] state: {state}")
                last_state = state
            if layer is not None and layer != last_layer and total:
                print(f"[{stamp}] layer {layer}/{total}"
                      + (f" · {pct}%" if pct is not None else "")
                      + (f" · ~{mins} min left"
                         if isinstance(mins, int) and mins > 0 else ""))
                last_layer = layer
            elif isinstance(pct, int) and pct // 10 != last_bucket:
                print(f"[{stamp}] {pct}% complete")
                last_bucket = pct // 10

            err = pd.get("print_error")
            if err and err != last_err:
                print(f"[{stamp}] PRINTER ERROR code {err} — check the "
                      "printer screen.")
                log_entry(f"{name} · error code {err} during print")
                last_err = err

            if state == "FINISH":
                print(f"[{stamp}] Print finished.")
                log_entry(f"{name} · finished OK")
                return
            if state == "FAILED":
                print(f"[{stamp}] Print FAILED.")
                log_entry(f"{name} · FAILED")
                return

            if time.time() - last_pushall > 60:  # resync full state
                link.pushall()
                last_pushall = time.time()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopped watching (print continues).")
    finally:
        link.close()


# --------------------------------------------------------------------- snap

SNAP_DIR = PROJECT_DIR / "snapshots"


def take_snapshot(tag: str = "") -> Path:
    import bambulabs_api as bl
    ip, code, serial = load_credentials()
    p = bl.Printer(ip, code, serial)
    p.camera_start()
    img = None
    for attempt in range(4):        # camera can be slow to produce a frame
        time.sleep(4)
        try:
            img = p.get_camera_image()
            break
        except Exception:
            if attempt == 3:
                p.camera_stop()
                raise
    p.camera_stop()
    SNAP_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"snap-{stamp}{'-' + tag if tag else ''}.png"
    out = SNAP_DIR / name
    img.save(out)
    return out


def cmd_snap(args):
    out = take_snapshot(args.tag)
    print(f"Saved {out}")
    if args.open_it:
        subprocess.run(["open", str(out)])


# ----------------------------------------------------------------- countdown

def _fmt_clock(epoch: float) -> str:
    return dt.datetime.fromtimestamp(epoch).strftime("%-I:%M %p")


def _countdown_html(name, start, finish, sync) -> Path:
    """Write a self-contained browser countdown seeded from live data."""
    html = COUNTDOWN_HTML.replace("__NAME__", name.replace("<", "").replace(">", "")) \
        .replace("__START__", str(int(start * 1000))) \
        .replace("__FINISH__", str(int(finish * 1000))) \
        .replace("__SYNC__", str(int(sync * 1000)))
    out = PROJECT_DIR / "countdown.html"
    out.write_text(html)
    return out


def cmd_countdown(args):
    """Live terminal countdown that re-syncs to the printer's own estimate.
    --html also opens a browser timer seeded from the current job."""
    link = connect()
    A, G, D, B, R = ("\033[38;5;179m", "\033[38;5;114m", "\033[2m",
                     "\033[1m", "\033[0m")
    finish = start = None
    last_fetch = 0.0
    d = {"state": "", "name": "(no job)", "lay": None, "tot": None, "pct": None}
    html_opened = False
    try:
        while True:
            now = time.time()
            if now - last_fetch > 8:
                pd = link.print_data()
                d["state"] = str(pd.get("gcode_state", "")).upper()
                d["name"] = pd.get("subtask_name") or pd.get("gcode_file") or "(no job)"
                d["lay"] = pd.get("layer_num")
                d["tot"] = pd.get("total_layer_num")
                d["pct"] = pd.get("mc_percent")
                rem = pd.get("mc_remaining_time")
                if isinstance(rem, int) and rem >= 0:
                    finish = now + rem * 60
                    pf = (d["pct"] or 0) / 100.0
                    total = (rem / (1 - pf)) if pf < 0.98 else rem
                    start = finish - total * 60
                last_fetch = now
                if args.html and not html_opened and finish and start:
                    out = _countdown_html(d["name"], start, finish, now)
                    subprocess.run(["open", str(out)])
                    html_opened = True
                if d["state"] in ("FINISH", "FAILED"):
                    print("\033[2J\033[H", end="")
                    tag = f"{G}COMPLETE{R}" if d["state"] == "FINISH" else f"\033[38;5;203mFAILED{R}"
                    print(f"\n  {tag}  {d['name']}\n")
                    return

            # local 1s tick between fetches
            secs = int(finish - now) if finish else None
            print("\033[2J\033[H", end="")
            print(f"\n  {A}⏱{R}  {B}{d['name']}{R}   {D}[{d['state'] or '—'}]{R}\n")
            if secs is not None and secs > 0:
                h, rem2 = divmod(secs, 3600)
                m, s = divmod(rem2, 60)
                print(f"     {B}{A}{h:02d}:{m:02d}:{s:02d}{R}   {D}remaining{R}\n")
            elif d["state"] == "RUNNING":
                print(f"     {D}preparing / heating…{R}\n")
            pct = d["pct"] or 0
            filled = round(pct / 100 * 26)
            bar = "█" * filled + "░" * (26 - filled)
            print(f"     {A}{bar}{R}  {pct}%")
            lay = f"{d['lay']}/{d['tot']}" if d["tot"] else "—"
            eta = f"ETA {_fmt_clock(finish)}" if finish else ""
            print(f"     {D}layer{R} {lay}        {D}{eta}{R}")
            print(f"\n  {D}re-syncs to the printer every 8s · Ctrl-C to exit"
                  f" (print keeps running){R}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n(exited countdown; print continues)")
    finally:
        link.close()


COUNTDOWN_HTML = """<!doctype html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Print Countdown</title><style>
:root{--g:#16130f;--s:#201c16;--s2:#2a251d;--t:#efe9df;--m:#9a917f;--f:#6d6553;
--a:#d8a24a;--ad:#9c7328;--tr:#322c22;--good:#77c489;--h:#332d23}
@media(prefers-color-scheme:light){:root{--g:#f0eadd;--s:#fbf8f1;--s2:#f4eee1;
--t:#241f18;--m:#6a6154;--f:#938872;--a:#b0791f;--ad:#cbb489;--tr:#e4dccb;--good:#3f8f57;--h:#e0d8c6}}
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:var(--g);color:var(--t);
font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;padding:28px}
.c{width:100%;max-width:420px;background:var(--s);border:1px solid var(--h);border-radius:18px;
padding:28px;box-shadow:0 22px 55px -26px rgba(0,0,0,.6)}
.e{font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:var(--m);font-weight:600}
h1{font-size:19px;margin:12px 0 20px;font-weight:650}
.k{font-family:ui-monospace,Menlo,monospace;font-variant-numeric:tabular-nums;font-weight:600;
font-size:clamp(48px,14vw,68px);line-height:1}.k .s{color:var(--ad)}
.lab{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--f);margin:14px 0 4px;font-weight:600}
.bar{height:8px;background:var(--tr);border-radius:99px;overflow:hidden;margin:18px 0 8px}
.bar>span{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--ad),var(--a));transition:width .5s}
.row{display:flex;justify-content:space-between;font-size:12px;color:var(--m);font-variant-numeric:tabular-nums}
.ft{margin-top:16px;font-size:11px;color:var(--f);line-height:1.5}</style></head><body>
<div class=c><div class=e>Printing · silent</div><h1>__NAME__</h1>
<div class=lab id=lab>Time remaining</div><div class=k id=clk>--:--:--</div>
<div class=bar><span id=fill></span></div>
<div class=row><span id=pct>—</span><span id=eta>ETA —</span></div>
<div class=ft id=ft></div></div><script>
var S=__START__,F=__FINISH__;function tc(ms){var d=new Date(ms),h=d.getHours(),m=d.getMinutes(),
ap=h>=12?'PM':'AM';h=h%12||12;return h+':'+(m<10?'0':'')+m+' '+ap}
document.getElementById('eta').textContent='ETA '+tc(F);
document.getElementById('ft').textContent='Seeded from the printer estimate at '+tc(__SYNC__)+'; will not re-sync.';
function t(){var n=Date.now(),r=F-n,p=Math.max(0,Math.min(1,(n-S)/(F-S)));
document.getElementById('fill').style.width=(p*100).toFixed(1)+'%';
document.getElementById('pct').textContent=Math.round(p*100)+'% elapsed';
var c=document.getElementById('clk');if(r<=0){c.textContent='Finishing…';c.style.color='var(--good)';
document.getElementById('lab').textContent='Past estimate';return}
var s=Math.floor(r/1000),h=Math.floor(s/3600);s-=h*3600;var m=Math.floor(s/60);s-=m*60;
function z(n){return(n<10?'0':'')+n}c.innerHTML=z(h)+'<span class=s>:</span>'+z(m)+'<span class=s>:</span>'+z(s)}
t();setInterval(t,1000)</script></body></html>"""


# ------------------------------------------------------------------ reslice

def patch_xy_compensation(src: Path, xy: float) -> Path:
    """Copy the .3mf and set xy_contour_compensation in its embedded
    project settings, so the tweak travels inside the project file
    (the CLI is unreliable with external preset JSONs)."""
    out = Path(tempfile.mkdtemp(prefix="reslice-")) / src.name
    with zipfile.ZipFile(src) as zin, \
         zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        names = zin.namelist()
        cfg_name = "Metadata/project_settings.config"
        if cfg_name not in names:
            sys.exit(f"{src.name} has no embedded presets ({cfg_name} missing). "
                     "Re-save it from Bambu Studio as a project file.")
        for name in names:
            data = zin.read(name)
            if name == cfg_name:
                cfg = json.loads(data)
                cfg["xy_contour_compensation"] = str(xy)
                data = json.dumps(cfg, indent=2).encode()
            zout.writestr(name, data)
    return out


def cmd_reslice(args):
    src = Path(args.file).expanduser()
    if not src.is_file():
        sys.exit(f"No such file: {src}")
    if not src.name.endswith(".3mf"):
        sys.exit("reslice only accepts saved .3mf project files with embedded "
                 "presets — not STLs.")
    if not Path(BAMBU_STUDIO).is_file():
        sys.exit(f"Bambu Studio binary not found at {BAMBU_STUDIO}")

    work_src = src
    tag = ""
    if args.xy_compensation is not None:
        work_src = patch_xy_compensation(src, args.xy_compensation)
        tag = f"-xy{args.xy_compensation:+g}"
        print(f"Applied xy_contour_compensation = {args.xy_compensation} "
              "inside a working copy of the project.")

    SLICED_DIR.mkdir(exist_ok=True)
    stem = src.name[:-len(".3mf")]
    out_name = f"{stem}{tag}.gcode.3mf"
    out_path = slice_project(work_src, out_name, args.plate,
                             label=src.name)
    print(f"Sliced OK → {out_path}")
    if work_src is not src:
        shutil.rmtree(work_src.parent, ignore_errors=True)


def slice_project(work_src: Path, out_name: str, plate: int,
                  label: str = "") -> Path:
    """Slice a .3mf project via the Bambu Studio CLI; exits on failure."""
    if not Path(BAMBU_STUDIO).is_file():
        sys.exit(f"Bambu Studio binary not found at {BAMBU_STUDIO}")
    SLICED_DIR.mkdir(exist_ok=True)
    pipe_path = Path(tempfile.mkdtemp(prefix="reslice-pipe-")) / "progress"
    os.mkfifo(pipe_path)

    def read_progress():
        try:
            with open(pipe_path) as fifo:
                for line in fifo:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                        pct = msg.get("percent")
                        text = msg.get("message") or msg.get("stage") or ""
                        if pct is not None:
                            print(f"  [{pct:>3}%] {text}")
                        elif text:
                            print(f"  {text}")
                    except json.JSONDecodeError:
                        print(f"  {line}")
        except OSError:
            pass

    t = threading.Thread(target=read_progress, daemon=True)
    t.start()

    cmd = [
        BAMBU_STUDIO,
        "--slice", str(plate),
        "--export-3mf", out_name,
        "--outputdir", str(SLICED_DIR),
        "--mstpp", "300",
        "--pipe", str(pipe_path),
        "--debug", "1",
        str(work_src),
    ]
    print(f"Slicing {label or work_src.name} "
          f"(plate {'all' if plate == 0 else plate})…")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    t.join(timeout=2)

    out_path = SLICED_DIR / out_name
    if proc.returncode == 0 and out_path.is_file():
        return out_path
    print(f"Slice FAILED (exit {proc.returncode}).")
    tail = "\n".join((proc.stdout + proc.stderr).splitlines()[-15:])
    if tail:
        print(tail)
    sys.exit(1)


# ------------------------------------------------------------------ compose

def cmd_compose(args):
    import compose_plate

    spec_path = Path(args.spec).expanduser()
    if not spec_path.is_file():
        sys.exit(f"No such spec: {spec_path}")
    spec = json.loads(spec_path.read_text())
    name = spec.get("name") or spec_path.stem

    composed = PROJECT_DIR / "composed" / f"{name}.3mf"
    compose_plate.compose(spec_path, composed)
    print(f"Composed project → {composed}")

    sliced = slice_project(composed, f"{name}.gcode.3mf", 1, label=name)
    compose_plate.finalize_sliced(sliced, spec)
    print(f"Sliced → {sliced}")

    print("Pre-flight audit…")
    problems = compose_plate.audit_sliced(sliced, spec)

    link = connect()
    try:
        slot = compose_plate.find_ams_slot(
            link.print_data(), spec.get("ams_tray_type", "PLA"),
            spec.get("ams_sub_brand", "Matte"),
            spec.get("filament_colour", "#000000"))
        if slot is None:
            problems.append(
                "AMS: no slot currently holds "
                f"{spec.get('filament_colour', '#000000')} "
                f"{spec.get('ams_tray_type', 'PLA')} "
                f"{spec.get('ams_sub_brand', 'Matte')}")
        if problems:
            print("AUDIT FAILED — refusing to stage:")
            for p in problems:
                print(f"  ✗ {p}")
            sys.exit(1)
        ams_id, tray_id = slot
        print(f"Audit PASSED. Filament in AMS {ams_id} slot {tray_id}.")

        if args.no_stage:
            return
        import bambulabs_api as bl
        ip, code, serial = load_credentials()
        printer = bl.Printer(ip, code, serial)
        print(f"Staging: uploading {sliced.name} "
              f"({sliced.stat().st_size / 1e6:.1f} MB) over FTPS…")
        with open(sliced, "rb") as f:
            result = printer.upload_file(f, sliced.name)
        if "226" not in str(result):
            sys.exit(f"Upload finished with unexpected FTP status: {result}")
        print(f"Staged on printer storage: {sliced.name}")
        print(f"NOT started. To print: ./pc start {sliced.name} "
              f"--ams-slot {tray_id}")
    finally:
        link.close()


# --------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(prog="pc", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="live printer status").set_defaults(fn=cmd_status)

    p = sub.add_parser("upload", help="upload a file to printer storage")
    p.add_argument("file")
    p.set_defaults(fn=cmd_upload)

    p = sub.add_parser("start", help="start a print (asks for confirmation)")
    p.add_argument("file", help="filename already on printer storage")
    p.add_argument("--plate", type=int, default=1)
    p.add_argument("--version-tag", help='part version for the log, e.g. "v16b"')
    p.add_argument("--ams-slot", type=int, default=0)
    p.add_argument("--ams-mapping",
                   help="explicit AMS tray mapping for multi-filament plates: "
                        "comma-separated 0-based tray indices ordered by gcode "
                        "filament (T0,T1,...), e.g. '2,0' routes T0->tray2, "
                        "T1->tray0. Overrides --ams-slot.")
    p.add_argument("--no-ams", action="store_true")
    p.add_argument("--no-flow-cali", action="store_true")
    p.add_argument("--yes", action="store_true",
                   help="skip the interactive prompt (only after an explicit "
                        "yes from Ron in conversation)")
    p.set_defaults(fn=cmd_start)

    sub.add_parser("watch", help="follow the active job").set_defaults(fn=cmd_watch)

    p = sub.add_parser("countdown",
                       help="live terminal countdown (re-syncs to the printer)")
    p.add_argument("--html", action="store_true",
                   help="also open a browser timer seeded from the current job")
    p.set_defaults(fn=cmd_countdown)

    p = sub.add_parser("snap", help="save a chamber-camera frame")
    p.add_argument("--tag", default="", help="label for the filename")
    p.add_argument("--open", dest="open_it", action="store_true",
                   help="open the frame in Preview")
    p.set_defaults(fn=cmd_snap)

    p = sub.add_parser("compose",
                       help="compose plate from STLs + spec, slice, audit, stage")
    p.add_argument("spec", help="plate spec JSON")
    p.add_argument("--no-stage", action="store_true",
                   help="compose/slice/audit only, skip the upload")
    p.set_defaults(fn=cmd_compose)

    p = sub.add_parser("reslice", help="headless re-slice of a .3mf project")
    p.add_argument("file")
    p.add_argument("--xy-compensation", type=float,
                   help="xy_contour_compensation in mm, e.g. -0.05")
    p.add_argument("--plate", type=int, default=0, help="0 = all plates")
    p.set_defaults(fn=cmd_reslice)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
