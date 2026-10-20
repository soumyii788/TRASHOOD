"""Safe Celery dispatch so missing brokers never break request handling."""
import logging

logger = logging.getLogger(__name__)


def enqueue(task, *args, **kwargs):
    try:
        return task.delay(*args, **kwargs)
    except Exception:
        logger.exception('Celery broker unavailable; running %s inline', getattr(task, 'name', task))
        try:
            return task.apply(args=args, kwargs=kwargs)
        except Exception:
            logger.exception('Inline task %s also failed', getattr(task, 'name', task))
            return None
