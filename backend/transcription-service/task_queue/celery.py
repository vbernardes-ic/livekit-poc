import os
from celery import Celery

app = Celery('task_queue',
             broker=os.getenv('REDIS_URL'),
             backend=os.getenv('REDIS_URL'),
             include=['task_queue.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()
