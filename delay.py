import time

next_using = time.time()


def delay():
    global next_using

    if time.time() < next_using:
        next_using += 15
        time.sleep(next_using - time.time())
    else:
        next_using = time.time() + 15