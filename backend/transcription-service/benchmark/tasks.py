from celery import Celery
import json
import whisper
import logging
import time
from celery.signals import task_prerun, task_postrun

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Set up transcription models

model_names = ['tiny.en', 'base.en', 'small.en']
models = {name: whisper.load_model(name) for name in model_names}

# To get task execution times
tasks_exec_time = {}


app = Celery('tasks',
             broker='redis://localhost',
             backend='redis://localhost')


@app.task(track_started=True)
def transcribe(audio_file, model_name, chunk_size=None, counter=None):
    transcript = models[model_name].transcribe(audio_file)

    # Output transcription results
    if chunk_size is not None:
        filename = f'transcription_{model_name}_{chunk_size}secs_{counter}.txt'
    else:
        filename = f'transcription_{model_name}.txt'
    with open(filename, 'w') as transcript_f:
        transcript_f.write(transcript['text'].strip() + '\n')
    logger.info(transcript)

    return json.dumps({'transcription': transcript})


@task_prerun.connect
def task_prerun_handler(task_id, task, **extras):
    """ Dispatched before a task is executed. """
    tasks_exec_time[task_id] = time.perf_counter()


@task_postrun.connect
def task_postrun_handler(task_id, task, **extras):
    """ Dispatched after a task has been executed. """
    end = time.perf_counter()
    elapsed_time = end - tasks_exec_time.pop(task_id)

    model_name = extras['args'][1]
    chunk_size = extras['kwargs']['chunk_size']

    # output performance
    if chunk_size is not None:
        filename = f'performance_{model_name}_{chunk_size}secs.csv'
    else:
        filename = f'performance_{model_name}.csv'
    with open(filename, 'a') as f:
        f.write(str(elapsed_time) + '\n')
    logger.info(f'Task {task_id} took {str(round(elapsed_time, 3))} seconds.')
