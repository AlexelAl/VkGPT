from datetime import datetime
import pytz


def logger(msg):
    with open('../log.txt', 'a') as log:
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        dt = str(now.date()) + " " + str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2)
        log.write(dt + '\n')
        log.write(msg + '\n\n')