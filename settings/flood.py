import time
from config import FLOOD_DELAY


class Flood:
    def __init__(self):
        self.last = dict()

    def check(self, id):
        if id in self.last and time.time() - self.last[id] < FLOOD_DELAY:
            return True
        else:
            return False

    def update(self, id):
        self.last[id] = time.time()
