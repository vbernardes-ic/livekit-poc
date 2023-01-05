FROM python:3.9-alpine
RUN pip install aiohttp websockets requests
EXPOSE 8765
COPY server.py /app/
WORKDIR /app
CMD ["python", "server.py"]
