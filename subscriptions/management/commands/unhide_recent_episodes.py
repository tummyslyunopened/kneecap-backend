import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from subscriptions.models import Episode  # Adjust import if model is elsewhere


class Command(BaseCommand):
    help = "Unhides all episodes from the last N days."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Number of days in the past to unhide episodes (default: 30)",
        )

    def handle(self, *args, **options):
        days = options["days"]
        cutoff = timezone.now() - datetime.timedelta(days=days)
        updated = Episode.objects.filter(hidden=True, pub_date__gte=cutoff).update(hidden=False)
        self.stdout.write(
            self.style.SUCCESS(f"Unhid {updated} episodes from the last {days} days.")
        )
