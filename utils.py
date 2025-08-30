import csv, time
from collections import deque

class RollingCounter:
    def __init__(self): self.count = 0
    def update(self, cond):
        self.count = self.count + 1 if cond else 0
        return self.count

class EventLogger:
    def __init__(self, path, enabled=True):
        self.enabled = enabled; self.path = path
        if self.enabled:
            try:
                with open(self.path, "a", newline="") as f:
                    f.write("timestamp,event,detail\n")
            except Exception: self.enabled=False
    def log(self, event, detail=""):
        if not self.enabled: return
        try:
            with open(self.path, "a", newline="") as f:
                f.write(f"{int(time.time())},{event},{detail}\n")
        except Exception: pass

class ValueBuffer:
    def __init__(self, size=5): self.buf = deque(maxlen=size)
    def add(self, x): self.buf.append(float(x))
    @property
    def mean(self): return sum(self.buf)/len(self.buf) if self.buf else 0.0
