import whisper
import json
from tempfile import NamedTemporaryFile

from flask import Flask, request

app = Flask(__name__)

# load model and processor
model = whisper.load_model('tiny')


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return "Ok"

@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio_data = request.get_data()

    with NamedTemporaryFile() as f:
        f.write(audio_data)
        transcript = model.transcribe(f.name)
        print(transcript)
        return json.dumps({'transcription': transcript})


if __name__ == '__main__':
    print("Running...")
    app.run(host="0.0.0.0",port=5050)