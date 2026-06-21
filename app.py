from flask import Flask, request, jsonify
from queue import Queue
from threading import Thread
import random
import time

app = Flask(__name__)

main_queue = Queue()
dead_letter_queue = []

MAX_RETRIES = 3


# ---------- Worker ----------
def worker():

    while True:

        message = main_queue.get()

        retries = message.get(
            "retries",
            0
        )

        # Simulate failure
        success = random.choice(
            [True, False]
        )

        if success:

            print(
                "Processed:",
                message["data"]
            )

        else:

            retries += 1

            if retries < MAX_RETRIES:

                message[
                    "retries"
                ] = retries

                main_queue.put(
                    message
                )

            else:

                dead_letter_queue.append(
                    message
                )

        main_queue.task_done()

        time.sleep(2)


Thread(
    target=worker,
    daemon=True
).start()


# ---------- Add Message ----------
@app.route(
    "/enqueue",
    methods=["POST"]
)
def enqueue():

    data = request.get_json()

    main_queue.put({
        "data": data["message"],
        "retries": 0
    })

    return jsonify({
        "message":
        "Added to queue"
    })


# ---------- Queue Status ----------
@app.route("/queue")
def queue_status():

    return jsonify({
        "messages_waiting":
        main_queue.qsize()
    })


# ---------- Dead Letter Queue ----------
@app.route("/dlq")
def dlq():

    return jsonify(
        dead_letter_queue
    )


# ---------- Health ----------
@app.route("/health")
def health():

    return jsonify({
        "status":
        "healthy"
    })


if __name__ == "__main__":

    app.run(debug=True)
