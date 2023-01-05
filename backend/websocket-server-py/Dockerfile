FROM python:3.9-alpine
RUN pip install aiohttp websockets
EXPOSE 8765
COPY server.py /app/
WORKDIR /app
CMD ["python", "server.py"]
