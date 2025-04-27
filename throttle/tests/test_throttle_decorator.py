from django.test import TransactionTestCase
from django.db import models, connection
from throttle.decorators import global_throttle, model_instance_throttle
from throttle.models import GlobalThrottle
from django.utils import timezone
import time


class TempThrottleModel(models.Model):
    last_called_instance = models.DateTimeField(null=True, blank=True)
    interval_instance = models.IntegerField(null=True)
    last_called_combined = models.DateTimeField(null=True, blank=True)
    interval_combined = models.IntegerField(null=True)
    last_called_combined2 = models.DateTimeField(null=True, blank=True)
    interval_combined2 = models.IntegerField(null=True)

    @global_throttle("test_global_key", 5, 3)
    def global_throttled_method(self):
        return "global"

    @model_instance_throttle("last_called_instance", "interval_instance", 5, 3)
    def instance_throttled_method(self):
        return "instance"

    @model_instance_throttle("last_called_combined", "interval_combined", 3, 1)
    @global_throttle("test_combined_key", 5, 1)
    def combined_throttled_method(self):
        return "combined"

    @global_throttle("test_combined_key2", 3, 1)
    @model_instance_throttle("last_called_combined2", "interval_combined2", 5, 1)
    def combined_throttled_method2(self):
        return "combined"

    @global_throttle("test_patient_key", 5, 3, wait_on_throttled=True)
    def patient_throttled_method(self):
        return "patient"


class TempThrottleModelTestBase(TransactionTestCase):
    reset_sequences = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TempThrottleModel)

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(TempThrottleModel)
        super().tearDownClass()


class TestThrottleDecorators(TempThrottleModelTestBase):
    def setUp(self):
        self.obj = TempThrottleModel.objects.create()

    def test_global_throttle(self):
        self.assertEqual(self.obj.global_throttled_method(), "global")
        self.assertEqual(GlobalThrottle.objects.get(key="test_global_key").interval_seconds, 5)
        self.assertEqual(self.obj.global_throttled_method(), None)
        gt = GlobalThrottle.objects.get(key="test_global_key")
        gt.last_called = timezone.now() - timezone.timedelta(seconds=5)
        gt.save(update_fields=["last_called"])
        self.assertEqual(self.obj.global_throttled_method(), "global")

    def test_global_throttle_min_fallback(self):
        self.assertEqual(self.obj.global_throttled_method(), "global")
        gt = GlobalThrottle.objects.get(key="test_global_key")
        gt.interval_seconds = 1
        gt.save(update_fields=["interval_seconds"])
        self.assertIsNone(self.obj.global_throttled_method())
        gt = GlobalThrottle.objects.get(key="test_global_key")
        gt.last_called = timezone.now() - timezone.timedelta(seconds=1)
        gt.save(update_fields=["last_called"])
        self.assertIsNone(self.obj.global_throttled_method())
        gt = GlobalThrottle.objects.get(key="test_global_key")
        gt.last_called = timezone.now() - timezone.timedelta(seconds=3)
        gt.save(update_fields=["last_called"])
        self.assertEqual(self.obj.global_throttled_method(), "global")

    def test_instance_throttle(self):
        start = time.time()
        self.assertEqual(self.obj.last_called_instance, None)
        self.assertEqual(self.obj.instance_throttled_method(), "instance")
        self.obj.refresh_from_db()
        self.assertIsNotNone(self.obj.last_called_instance)
        self.assertEqual(self.obj.interval_instance, 5)
        self.assertEqual(self.obj.instance_throttled_method(), None)
        while self.obj.instance_throttled_method() is None:
            pass
        elapsed = int(round(time.time() - start))
        self.assertGreaterEqual(elapsed, 5)
        self.assertLessEqual(elapsed, 6)

    def test_instance_throttle_min_fallback(self):
        start = time.time()
        self.assertEqual(self.obj.last_called_instance, None)
        self.assertEqual(self.obj.instance_throttled_method(), "instance")
        self.obj.interval_instance = 1
        self.obj.save(update_fields=["interval_instance"])
        self.obj.refresh_from_db()
        self.assertIsNotNone(self.obj.last_called_instance)
        self.assertEqual(self.obj.interval_instance, 1)
        while self.obj.instance_throttled_method() is None:
            pass
        elapsed = int(round(time.time() - start))
        self.assertGreaterEqual(elapsed, 3)
        self.assertLessEqual(elapsed, 4)

    def test_combined_throttle(self):
        start = time.time()
        self.assertEqual(self.obj.last_called_combined, None)
        self.assertEqual(self.obj.interval_combined, None)
        self.assertEqual(self.obj.combined_throttled_method(), "combined")
        self.assertEqual(GlobalThrottle.objects.get(key="test_combined_key").interval_seconds, 5)
        self.obj.refresh_from_db()
        self.assertIsNotNone(self.obj.last_called_combined)
        self.assertEqual(self.obj.interval_combined, 3)
        self.assertEqual(self.obj.combined_throttled_method(), None)
        while self.obj.combined_throttled_method() is None:
            pass
        elapsed = int(round(time.time() - start))
        self.assertGreaterEqual(elapsed, 5)
        self.assertLessEqual(elapsed, 6)

    def test_combined_throttle2(self):
        start = time.time()
        self.assertEqual(self.obj.last_called_combined2, None)
        self.assertEqual(self.obj.interval_combined2, None)
        self.assertEqual(self.obj.combined_throttled_method2(), "combined")
        self.assertEqual(GlobalThrottle.objects.get(key="test_combined_key2").interval_seconds, 3)
        self.obj.refresh_from_db()
        self.assertIsNotNone(self.obj.last_called_combined2)
        self.assertEqual(self.obj.interval_combined2, 5)
        self.assertEqual(self.obj.combined_throttled_method2(), None)
        while self.obj.combined_throttled_method2() is None:
            pass
        elapsed = int(round(time.time() - start))
        self.assertGreaterEqual(elapsed, 5)
        self.assertLessEqual(elapsed, 6)

    def test_patient_throttle(self):
        start = time.time()
        self.assertEqual(self.obj.patient_throttled_method(), "patient")
        self.assertEqual(self.obj.patient_throttled_method(), "patient")
        elapsed = int(round(time.time() - start))
        self.assertGreaterEqual(elapsed, 5)
        self.assertLessEqual(elapsed, 6)

    def test_global_throttle_wait_on_throttled_sleeps(self):
        self.obj.global_throttled_method()
        gt = GlobalThrottle.objects.get(key="test_global_key")
        gt.last_called = timezone.now()
        gt.interval_seconds = 2
        gt.save(update_fields=["last_called", "interval_seconds"])
        decorated = global_throttle("test_global_key", 2, 2, wait_on_throttled=True)(
            lambda self: "ran_after_wait"
        )
        start = time.time()
        result = decorated(self.obj)
        elapsed = time.time() - start
        self.assertEqual(result, "ran_after_wait")
        self.assertGreaterEqual(elapsed, 2)
        self.assertLess(elapsed, 3)

    def test_model_instance_throttle_wait_on_throttled_sleeps(self):
        self.obj.instance_throttled_method()
        self.obj.last_called_instance = timezone.now()
        self.obj.interval_instance = 2
        self.obj.save(update_fields=["last_called_instance", "interval_instance"])
        decorated = model_instance_throttle(
            "last_called_instance", "interval_instance", 2, 2, wait_on_throttled=True
        )(lambda self: "ran_after_wait")
        start = time.time()
        result = decorated(self.obj)
        elapsed = time.time() - start
        self.assertEqual(result, "ran_after_wait")
        self.assertGreaterEqual(elapsed, 2)
        self.assertLess(elapsed, 3)

    def test_model_instance_throttle_sets_interval_if_none(self):
        self.obj.interval_instance = None
        self.obj.save(update_fields=["interval_instance"])
        self.obj.last_called_instance = None
        self.obj.save(update_fields=["last_called_instance"])
        decorated = model_instance_throttle("last_called_instance", "interval_instance", 7, 3)(
            lambda self: "set_interval"
        )
        result = decorated(self.obj)
        self.assertEqual(result, "set_interval")
        self.obj.refresh_from_db()
        self.assertEqual(self.obj.interval_instance, 7)
