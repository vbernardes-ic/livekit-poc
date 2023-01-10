FROM python:3.10
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install -y ffmpeg && \
    pip install setuptools && \
    pip install --upgrade pip && \
    pip install flask && \
    pip install git+https://github.com/openai/whisper.git
RUN pip install -U "celery[redis]" && \
    ln -s /run/shm /dev/shm  # workaround for celery
EXPOSE 5050
#COPY *.py /app/
#ADD task_queue /app/task_queue
WORKDIR /app
RUN touch celery.log  # workaround for celery
CMD celery -A task_queue.celery worker -l INFO -f celery.log & \
    python my_whisper_service.py
