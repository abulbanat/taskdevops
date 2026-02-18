import os
import time
from datetime import datetime, timezone

from flask import Flask

app = Flask(__name__)
start_time = time.time()


@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "myapp",
        "uptime_seconds": int(time.time() - start_time),
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    print(f"[{datetime.now(timezone.utc).isoformat()}] myapp starting on port {port}", flush=True)

    # Run Flask in a background thread so we can keep printing logs to stdout.
    import threading

    def run_server():
        app.run(host="0.0.0.0", port=port)

    threading.Thread(target=run_server, daemon=True).start()

    counter = 0
    while True:
        counter += 1
        print(
            f"[{datetime.now(timezone.utc).isoformat()}] level=INFO app=myapp msg='heartbeat log' count={counter}",
            flush=True,
        )
        time.sleep(5)
