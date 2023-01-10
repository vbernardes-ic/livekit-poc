import json
from tempfile import NamedTemporaryFile
import whisper
import logging
from base64 import b64decode
from .celery import app

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Set up transcription model
model = whisper.load_model('tiny.en')


@app.task
def hello():
    return 'hello world'


@app.task(track_started=True)
def transcribe(audio_data, b64=False):
    with NamedTemporaryFile() as f:
        bin_data = b64decode(audio_data.encode()) if b64 else audio_data
        f.write(bin_data)
        transcript = model.transcribe(f.name, verbose=True)
        logger.info(transcript)
        return json.dumps({'transcription': transcript})
