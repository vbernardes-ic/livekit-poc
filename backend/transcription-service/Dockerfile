FROM python:3.10
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install -y ffmpeg && \
    pip install setuptools && \
    pip install --upgrade pip && \
    pip install flask && \
    pip install git+https://github.com/openai/whisper.git
EXPOSE 5050
COPY my_whisper_service.py /app/
WORKDIR /app
CMD ["python", "my_whisper_service.py"]
