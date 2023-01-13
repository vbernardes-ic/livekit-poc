import json
from tempfile import NamedTemporaryFile
import whisper
import logging
from base64 import b64decode
from .celery import app
import time
from celery.signals import task_prerun, task_postrun, worker_ready

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Set up transcription model
model_name = 'base.en'
model = None

# To get task execution times
tasks_exec_time = {}


@app.task
def hello():
    return 'hello world'


@app.task(track_started=True)
def transcribe(audio_data, b64=False):
    with NamedTemporaryFile() as f:
        bin_data = b64decode(audio_data.encode()) if b64 else audio_data
        f.write(bin_data)
        transcript = model.transcribe(f.name)
        logger.info(transcript)

        return json.dumps({'transcription': transcript})


@worker_ready.connect
def load_model(sender=None, conf=None, **kwargs):
    global model
    model = whisper.load_model(model_name)
    logger.info(f'Loaded model: {model_name}')


@task_prerun.connect
def task_prerun_handler(task_id, task, **extras):
    """ Dispatched before a task is executed. """
    tasks_exec_time[task_id] = time.perf_counter()


@task_postrun.connect
def task_postrun_handler(task_id, task, **extras):
    """ Dispatched after a task has been executed. """
    end = time.perf_counter()
    elapsed_time = end - tasks_exec_time.pop(task_id)

    delay = 7
    with open(f'performance_{delay}secs.txt', 'a') as f:
        f.write(str(elapsed_time) + '\n')
    logger.info(f'Task {task_id} took {str(round(elapsed_time, 3))} seconds.')
