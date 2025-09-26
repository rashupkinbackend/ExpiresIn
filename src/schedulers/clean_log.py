import os


def cleanup_log():
    with open("app.log", "r+") as file:
        file.truncate(0)
