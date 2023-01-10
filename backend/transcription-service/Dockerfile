FROM python:3.10
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install -y ffmpeg && \
    pip install setuptools && \
    pip install --upgrade pip && \
    pip install flask && \
    pip install git+https://github.com/openai/whisper.git
RUN pip install -U "celery[redis]" flower && \
    ln -s /run/shm /dev/shm  # workaround for celery \
EXPOSE 5050 5555
WORKDIR /app
RUN touch celery.log  # workaround for celery
CMD celery -A task_queue.celery worker -l INFO -f celery.log & \
    celery -A task_queue.celery flower & \
    python my_whisper_service.py
