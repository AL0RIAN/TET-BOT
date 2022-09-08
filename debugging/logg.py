import time
import functools


def timer(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"\nFunction execution time: {round(end - start, 1)} seconds")
        return result

    return wrapped
