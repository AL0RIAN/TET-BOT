import sys
import time
import logging
import datetime
import functools


def timer(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger(text=f"Function execution time - {round(end - start, 1)} seconds", report_type="debug")
        return result

    return wrapped


def logger(text: str, report_type: str) -> None:
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    if report_type == "debug":
        logging.debug(f" {text} | {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    elif report_type == "info":
        logging.info(f" {text} | {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    else:
        logging.error(f" {text} | {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
