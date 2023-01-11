import logging
from base64 import b64encode

from flask import Flask, request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from task_queue import tasks

app = Flask(__name__)


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return "Ok"


@app.route('/transcribe_async', methods=['POST'])
def transcribe_async():
    audio_data = request.get_data()
    b64_audio_data = b64encode(audio_data).decode()
    # tasks.transcribe.delay(b64_audio_data, b64=True)
    tasks.transcribe.apply_async(args=[b64_audio_data],
                                 kwargs={'b64': True},
                                 expires=15)
    return ''


@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio_data = request.get_data()
    transcript = tasks.transcribe(audio_data)
    return transcript


if __name__ == '__main__':
    logging.info("Running...")
    app.run(host="0.0.0.0", port=5050)
