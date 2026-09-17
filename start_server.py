import threading
import uvicorn
import time

def run_server():
    uvicorn.run("src.backend.main:app", host="0.0.0.0", port=8000)

t = threading.Thread(target=run_server, daemon=True)
t.start()
time.sleep(5)
