from flask import Flask
from threading import Thread


app = Flask('Opera bar')


@app.route('/')
def main():
    return "Server online!"


def run():
    app.run(host="0.0.0.0", port=5005, debug=True, use_reloader=False)


def opera_alive():
    server = Thread(target=run)
    server.start()
