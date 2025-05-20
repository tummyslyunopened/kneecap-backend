from typing import Any
from .models import GlobalThrottle
from datetime import timedelta
from django.utils import timezone
import logging
import time

logger = logging.getLogger(__name__)


def global_throttle(
    throttle_key,
    default_interval,
    min_allowed_interval,
    wait_on_throttled=False,
    return_on_throttled: Any = None,
):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            _wait_on_throttled = True
            while _wait_on_throttled:
                throttle, _ = GlobalThrottle.objects.get(
                    key=throttle_key,
                    defaults={"interval_seconds": default_interval, "last_called": None},
                )
                interval = throttle.interval_seconds
                interval = max(interval, min_allowed_interval)
                now = timezone.now()
                if throttle.last_called is None or now - throttle.last_called >= timedelta(
                    seconds=interval
                ):
                    throttle.last_called = now
                    throttle.save(update_fields=["last_called"])
                    return func(self, *args, **kwargs)
                else:
                    if not wait_on_throttled:
                        if callable(return_on_throttled):
                            return return_on_throttled(self, *args, **kwargs)
                        return return_on_throttled
                    _wait_on_throttled = wait_on_throttled
                    wait_seconds = (
                        throttle.last_called + timedelta(seconds=interval) - now
                    ).total_seconds()
                    if wait_seconds > 0:
                        time.sleep(wait_seconds)

        return wrapper

    return decorator


def model_instance_throttle(
    timestamp_field,
    interval_field,
    default_interval,
    min_allowed_interval,
    wait_on_throttled=False,
    return_on_throttled: Any = None,
):
    """
    Decorator to throttle method calls per model instance.
    If throttled, returns the result of on_throttled (if callable, called with same args as func), or its value.
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            _wait_on_throttled = True
            while _wait_on_throttled:
                instance = self.__class__.objects.get(pk=self.pk)
                interval = getattr(instance, interval_field, None)
                if interval is None:
                    interval = default_interval
                    setattr(instance, interval_field, interval)
                instance.save(update_fields=[interval_field])
                interval = max(interval, min_allowed_interval)
                last_called = getattr(instance, timestamp_field)
                now = timezone.now()
                if last_called is None or now - last_called >= timedelta(seconds=interval):
                    setattr(instance, timestamp_field, now)
                    instance.save(update_fields=[timestamp_field])
                    return func(self, *args, **kwargs)
                else:
                    if not wait_on_throttled:
                        logger.warning("THROTTLED - Method Not Callable Yet")
                        if callable(return_on_throttled):
                            return return_on_throttled(self, *args, **kwargs)
                        return return_on_throttled
                    _wait_on_throttled = wait_on_throttled
                    wait_seconds = (
                        last_called + timedelta(seconds=interval) - now
                    ).total_seconds()
                    if wait_seconds > 0:
                        time.sleep(wait_seconds)

        return wrapper

    return decorator
