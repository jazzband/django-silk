import Queue
import threading


class SilkyThread(threading.Thread):
    """we pass saving of queries etc to another thread so the request
    can return straight away and avoid impacting response time as much
    as possible"""

    def __init__(self, q):
        super(SilkyThread, self).__init__()
        self.q = q
        self.running = True

    def run(self):
        while self.running:
            try:
                self.q.get(timeout=0.2).run()
            except Queue.Empty:
                pass