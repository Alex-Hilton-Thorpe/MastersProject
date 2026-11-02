import subprocess
import signal
import sys
import time
 
DIR = "/home/alex/MastersProject/src"
SCRIPTS = [f"{DIR}/power.py", f"{DIR}/record.py"]
 
procs = {}
 
 
def launch(script):
    # -u = unbuffered, so prints show up straight away in the journal
    procs[script] = subprocess.Popen([sys.executable, "-u", script], cwd=DIR)
    print(f"Started {script}", flush=True)
 
 
def stop_all(*_):
    print("Stopping scripts...", flush=True)
    for p in procs.values():
        if p.poll() is None:
            p.send_signal(signal.SIGINT)      # lets each script clean up
    for p in procs.values():
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            p.kill()
    sys.exit(0)
 
 
signal.signal(signal.SIGTERM, stop_all)
signal.signal(signal.SIGINT, stop_all)
 
for s in SCRIPTS:
    launch(s)
 
# Restart either script if it crashes
while True:
    for s, p in list(procs.items()):
        if p.poll() is not None:
            print(f"{s} exited ({p.returncode}), restarting in 2s", flush=True)
            time.sleep(2)
            launch(s)
    time.sleep(1)