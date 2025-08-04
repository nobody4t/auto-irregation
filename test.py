import threading
import time


def test_thread():
    while True:
        print("start")
        while True:
            time.sleep(3)
            print("exit")
            exit()


test = threading.Thread(target=test_thread, daemon=True)
test.start()

while True:
    time.sleep(1)
    test.join()
    print("done")